![Build Status][build-badge]
[![Coverage][coverage-badge]][coverage-url]

[build-badge]: https://github.com/pawel-slowik/sql-non-unique-fk/workflows/tests/badge.svg
[coverage-badge]: https://codecov.io/gh/pawel-slowik/sql-non-unique-fk/branch/master/graph/badge.svg
[coverage-url]: https://codecov.io/gh/pawel-slowik/sql-non-unique-fk

This script inspects a SQL database to find foreign keys referring to columns
that do not have a unique key. For example:

	CREATE TABLE parent (
		id INT
	);

	CREATE TABLE child (
		parent_id INT,
		FOREIGN KEY(parent_id) REFERENCES parent(id)
	);

Here, the key declared on the `parent_id` column refers to a non-unique column.
This, [according to MySQL documentation][mysql-doc], may cause undefined behavior:

> The handling of foreign key references to nonunique keys or keys that contain
> NULL values is not well defined for operations such as UPDATE or DELETE
> CASCADE. You are advised to use foreign keys that reference only UNIQUE
> (including PRIMARY) and NOT NULL keys.

Note: this particular example is rather obvious and somewhat contrived, but there
may be cases where the problematic key is harder to find (for example, when the
unique key on the referred column evolved into a multi-column key, but analogous
change was not applied to the child table).

[mysql-doc]: https://dev.mysql.com/doc/mysql-reslimits-excerpt/8.0/en/ansi-diff-foreign-keys.html

## Installation

Clone this repository and make sure you have Python 3.x and
[SQLAlchemy][sqlalchemy] installed:

	pip3 install -r requirements.txt

You will also need to install a [SQLAlchemy dialect][sqlalchemy-dialect]
suitable for your database:

	pip3 install mysqlclient

[sqlalchemy]:https://www.sqlalchemy.org/
[sqlalchemy-dialect]:https://docs.sqlalchemy.org/en/latest/dialects/index.html

## Example usage

	~/path/sqlnufk.py mysql://bar_user:barP455word@host.bar/bar_database

For MySQL databases you can also use an option group name instead of the
database URL. This works similar to the `--defaults-group-suffix` parameter of
the `mysql` command line utility. For example, if you have the following
options saved in your `~/.my.cnf` file:

	[client_foo]
	host=host.bar
	database=bar_database
	user=bar_user
	password=barP455word

then you can run:

	~/path/sqlnufk.py foo

The script will exit with code 0 if no problematic foreign keys are found.
If problematic keys are found, they will be printed on standard output and the
script will exit with code 64. Any other exit code means that the script could
not check the keys (connection problem, driver / dialect not installed, invalid
URL etc.)
