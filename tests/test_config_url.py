import configparser
import pytest
from sqlnufk import url_from_mysql_config

# pylint: disable=redefined-outer-name; (for pytest fixtures)

@pytest.fixture
def config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read_string("""
[client_foo]
host=host.foo
port=3307
database=foo_database
user=foo_user
password=fooP455word

[client_bar]
host=host.bar
database=bar_database
user=bar_user
password=barP455word

[client_baz]
host=host.baz
database=baz_database
user=baz_user
""")
    return config

def test_url_from_config_foo(config: configparser.ConfigParser) -> None:
    test = url_from_mysql_config(config, "foo")
    expected = "mysql://foo_user:fooP455word@host.foo:3307/foo_database"
    assert test == expected

def test_url_from_config_bar(config: configparser.ConfigParser) -> None:
    test = url_from_mysql_config(config, "bar")
    expected = "mysql://bar_user:barP455word@host.bar/bar_database"
    assert test == expected

def test_url_from_config_baz(config: configparser.ConfigParser) -> None:
    test = url_from_mysql_config(config, "baz")
    expected = "mysql://baz_user@host.baz/baz_database"
    assert test == expected
