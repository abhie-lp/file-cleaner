"""Database related functions"""

from sqlite3 import connect, Connection, Row, PARSE_DECLTYPES


def get_db() -> Connection:
    """Return connection with the sqlite3 database"""
    db: Connection = connect("sqlite.db", detect_types=PARSE_DECLTYPES)
    db.row_factory = Row
    return db


def init_db() -> None:
    """Create database and tables if not exist"""
    with get_db() as db:
        with open("schema.sql") as fr:
            db.executescript(fr.read())
