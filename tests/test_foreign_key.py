import sqlalchemy
from sqlnufk import ForeignKey, list_non_unique_foreign_keys

def test_key_simple() -> None:
    engine = db_from_sql("""
        CREATE TABLE parent (
            id INT
        );

        CREATE TABLE child (
            parent_id INT,
            FOREIGN KEY(parent_id) REFERENCES parent(id)
        );
    """)
    test = list_non_unique_foreign_keys(engine)
    expected = [ForeignKey("child", ["parent_id"], "parent", ["id"])]
    assert test == expected

def test_key_partial() -> None:
    engine = db_from_sql("""
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
    test = list_non_unique_foreign_keys(engine)
    expected = [ForeignKey("child", ["parent_id"], "parent", ["id"])]
    assert test == expected

def test_key_composite() -> None:
    engine = db_from_sql("""
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
    test = list_non_unique_foreign_keys(engine)
    expected = [
        ForeignKey("child", ["parent_id"], "parent", ["id"]),
        ForeignKey("child", ["parent_language"], "parent", ["language"]),
    ]
    assert sorted(test) == sorted(expected)

def test_key_none_primary() -> None:
    engine = db_from_sql("""
        CREATE TABLE parent (
            id INT,
            PRIMARY KEY(id)
        );

        CREATE TABLE child (
            parent_id INT,
            FOREIGN KEY(parent_id) REFERENCES parent(id)
        );
    """)
    assert list_non_unique_foreign_keys(engine) == []

def test_key_none_unique() -> None:
    engine = db_from_sql("""
        CREATE TABLE parent (
            id INT,
            UNIQUE (id)
        );

        CREATE TABLE child (
            parent_id INT,
            FOREIGN KEY(parent_id) REFERENCES parent(id)
        );
    """)
    assert list_non_unique_foreign_keys(engine) == []

def db_from_sql(sql: str) -> sqlalchemy.engine.Engine:
    engine = sqlalchemy.create_engine("sqlite://")
    connection = engine.connect()
    transaction = connection.begin()
    for statement in sql.split(";"):
        connection.execute(sqlalchemy.sql.text(statement))
    transaction.commit()
    return engine
