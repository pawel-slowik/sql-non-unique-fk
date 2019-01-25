import unittest
import configparser
from sqlnufk import url_from_mysql_config

class TestConfigURL(unittest.TestCase):

    def setUp(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read_string("""
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

    def test_url_from_config_foo(self) -> None:
        self.assertEqual(
            url_from_mysql_config(self.config, "foo"),
            "mysql://foo_user:fooP455word@host.foo:3307/foo_database"
        )

    def test_url_from_config_bar(self) -> None:
        self.assertEqual(
            url_from_mysql_config(self.config, "bar"),
            "mysql://bar_user:barP455word@host.bar/bar_database"
        )

    def test_url_from_config_baz(self) -> None:
        self.assertEqual(
            url_from_mysql_config(self.config, "baz"),
            "mysql://baz_user@host.baz/baz_database"
        )
