import unittest
import sqlalchemy
from sqlnufk import ForeignKey, list_non_unique_foreign_keys

class TestForeignKey(unittest.TestCase):

    def test_key_simple(self) -> None:
        engine = self.db_from_sql("""
            CREATE TABLE parent (
                id INT
            );

            CREATE TABLE child (
                parent_id INT,
                FOREIGN KEY(parent_id) REFERENCES parent(id)
            );
        """)
        self.assertEqual(
            list_non_unique_foreign_keys(engine),
            [ForeignKey("child", ["parent_id"], "parent", ["id"])]
        )

    def test_key_partial(self) -> None:
        engine = self.db_from_sql("""
            CREATE TABLE parent (
                id INT,
                language INT,
                PRIMARY KEY(id, language)
            );

            CREATE TABLE child (
                parent_id INT,
                FOREIGN KEY(parent_id) REFERENCES parent(id)
            );
        """)
        self.assertEqual(
            list_non_unique_foreign_keys(engine),
            [ForeignKey("child", ["parent_id"], "parent", ["id"])]
        )

    def test_key_composite(self) -> None:
        engine = self.db_from_sql("""
            CREATE TABLE parent (
                id INT,
                language INT,
                PRIMARY KEY(id, language)
            );

            CREATE TABLE child (
                parent_id INT,
                parent_language INT,
                FOREIGN KEY(parent_id) REFERENCES parent(id),
                FOREIGN KEY(parent_language) REFERENCES parent(language)
            );
        """)
        self.assertEqual(
            sorted(list_non_unique_foreign_keys(engine)),
            sorted([
                ForeignKey("child", ["parent_id"], "parent", ["id"]),
                ForeignKey("child", ["parent_language"], "parent", ["language"]),
            ])
        )

    def test_key_none_primary(self) -> None:
        engine = self.db_from_sql("""
            CREATE TABLE parent (
                id INT,
                PRIMARY KEY(id)
            );

            CREATE TABLE child (
                parent_id INT,
                FOREIGN KEY(parent_id) REFERENCES parent(id)
            );
        """)
        self.assertEqual(list_non_unique_foreign_keys(engine), [])

    def test_key_none_unique(self) -> None:
        engine = self.db_from_sql("""
            CREATE TABLE parent (
                id INT,
                UNIQUE (id)
            );

            CREATE TABLE child (
                parent_id INT,
                FOREIGN KEY(parent_id) REFERENCES parent(id)
            );
        """)
        self.assertEqual(list_non_unique_foreign_keys(engine), [])

    @staticmethod
    def db_from_sql(sql: str) -> sqlalchemy.engine.Engine:
        engine = sqlalchemy.create_engine("sqlite://")
        for statement in sql.split(";"):
            engine.execute(statement)
        return engine
