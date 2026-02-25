#!/usr/bin/env python3

import sys
import os.path
import configparser
import itertools
import argparse
from typing import Iterable, Sequence, List, Any
import sqlalchemy


class UniqueKey:

    def __init__(self, table: str, columns: Iterable[str]) -> None:
        self.table = table
        self.columns = columns

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<{self.table}({', '.join(self.columns)})>"


class ForeignKey:

    def __init__(
            self,
            source_table: str,
            source_columns: Sequence[str],
            destination_table: str,
            destination_columns: Sequence[str]
        ) -> None:
        if len(source_columns) != len(destination_columns):
            raise ValueError
        self.source_table = source_table
        self.source_columns = source_columns
        self.destination_table = destination_table
        self.destination_columns = destination_columns

    def destination_matches(self, key: UniqueKey) -> bool:
        return self.destination_table == key.table and self.destination_columns == key.columns

    def __str__(self) -> str:
        source = f"{self.source_table}({', '.join(self.source_columns)})"
        destination = f"{self.destination_table}({', '.join(self.destination_columns)})"
        return f"{self.__class__.__name__}<{source} -> {destination}>"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ForeignKey):
            return super().__eq__(other)
        return (
            self.source_table == other.source_table
            and self.source_columns == other.source_columns
            and self.destination_table == other.destination_table
            and self.destination_columns == other.destination_columns
        )

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, ForeignKey):
            return super().__eq__(other)
        return str(self) < str(other)


def list_primary_keys(meta: sqlalchemy.MetaData) -> List[UniqueKey]:
    return [
        UniqueKey(table.name, [c.name for c in table.primary_key.columns])
        for table in meta.tables.values()
    ]


def list_unique_keys(meta: sqlalchemy.MetaData) -> List[UniqueKey]:

    def table_unique_keys(
            table: sqlalchemy.sql.schema.Table
        ) -> Iterable[UniqueKey]:
        from_constraints = [
            UniqueKey(table.name, [column.name for column in constraint.columns])
            for constraint in table.constraints
            if isinstance(constraint, sqlalchemy.UniqueConstraint)
        ]
        from_unique_indexes = [
            UniqueKey(table.name, [column.name for column in index.columns])
            for index in table.indexes
            if index.unique
        ]
        return from_constraints + from_unique_indexes

    return flatten([table_unique_keys(table) for table in meta.tables.values()])


def list_foreign_keys(meta: sqlalchemy.MetaData) -> List[ForeignKey]:

    def table_foreign_keys(table: sqlalchemy.sql.schema.Table) -> List[ForeignKey]:
        return [
            ForeignKey(
                table.name,
                cnst.column_keys,
                cnst.referred_table.name,
                [element.column.name for element in cnst.elements]
            )
            for cnst in table.constraints if isinstance(cnst, sqlalchemy.ForeignKeyConstraint)
        ]

    return flatten([table_foreign_keys(table) for table in meta.tables.values()])


def list_non_unique_foreign_keys(engine: sqlalchemy.engine.Engine) -> Iterable[ForeignKey]:
    meta = sqlalchemy.MetaData()
    meta.reflect(bind=engine)
    unique_keys = list_primary_keys(meta) + list_unique_keys(meta)
    return [fk for fk in list_foreign_keys(meta) if not check_foreign_key(fk, unique_keys)]


def check_foreign_key(foreign_key: ForeignKey, unique_keys: Iterable[UniqueKey]) -> bool:
    for key in unique_keys:
        if foreign_key.destination_matches(key):
            return True
    return False


def url_from_mysql_config(cfg: configparser.ConfigParser, name: str) -> str:
    try_section_names = [
        "client" + name,
        "client-" + name,
        "client_" + name,
    ]
    for section_name in try_section_names:
        if not cfg.has_section(section_name):
            continue
        section_url = "mysql://"
        if cfg.has_option(section_name, "user"):
            section_url += cfg.get(section_name, "user")
            if cfg.has_option(section_name, "password"):
                section_url += (":" + cfg.get(section_name, "password"))
            section_url += "@"
        if cfg.has_option(section_name, "host"):
            section_url += cfg.get(section_name, "host")
        if cfg.has_option(section_name, "port"):
            section_url += (":" + cfg.get(section_name, "port"))
        if cfg.has_option(section_name, "database"):
            section_url += ("/" + cfg.get(section_name, "database"))
        return section_url
    return name


def flatten(list2d: Iterable[Iterable]) -> List:
    return list(itertools.chain.from_iterable(list2d))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="database URL or MySQL option group suffix")
    args = parser.parse_args()
    url = args.url
    if "://" not in url:
        cfg = configparser.ConfigParser()
        cfg.read(os.path.expanduser("~/.my.cnf"))
        url = url_from_mysql_config(cfg, url)
    engine = sqlalchemy.create_engine(url)
    non_unique_foreign_keys = list_non_unique_foreign_keys(engine)
    for foreign_key in non_unique_foreign_keys:
        print(foreign_key)
    return 64 if non_unique_foreign_keys else 0


if __name__ == "__main__":
    sys.exit(main())
