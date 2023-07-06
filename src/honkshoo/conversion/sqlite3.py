import sqlite3

from honkshoo.conversion.base import Converter
from honkshoo.conversion.helpers import open_edf, process_edf_to_samples

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS ch (id INTEGER PRIMARY KEY, name TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS edf (ts NUMBER, ch_id INTEGER, value NUMBER);
CREATE UNIQUE INDEX IF NOT EXISTS edf_ts_ch ON edf (ts, ch_id);
"""

SQLITE_SUPER_ZOOMIES_MODE = """
pragma journal_mode = WAL;
pragma synchronous = normal;
pragma temp_store = memory;
pragma mmap_size = 30000000000;
"""


class SQLiteConverter(Converter):
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.initialize_db()

    def initialize_db(self):
        self.db.executescript(SQLITE_SCHEMA)
        self.db.executescript(SQLITE_SUPER_ZOOMIES_MODE)

    def finalize(self):
        self.db.commit()

    def read_edf(self, edf_path: str):
        edf = open_edf(edf_path)
        ch_names = list(edf.info["ch_names"])

        # Create channels if they don't exist, and get their IDs
        self.db.executemany("INSERT OR IGNORE INTO ch (name) VALUES (?)", [(ch_name,) for ch_name in ch_names])
        ch_ids = {ch_name: ch_id for ch_id, ch_name in self.db.execute("SELECT id, name FROM ch")}

        self.db.executemany(
            "INSERT OR IGNORE INTO edf (ts, ch_id, value) VALUES (?, ?, ?)",
            process_edf_to_samples(
                edf,
                map_channel_name=ch_ids.__getitem__,
                map_timestamp=lambda ts: ts.timestamp(),
            ),
        )
