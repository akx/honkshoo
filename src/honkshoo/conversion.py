import datetime
import sqlite3
from collections.abc import Iterable
from pathlib import Path

import mne.io
import tqdm


def write_from_edf(db: sqlite3.Connection, edf_path: Path):
    try:
        edf = mne.io.read_raw_edf(str(edf_path), preload=True, verbose="error")
    except Exception as e:
        print(f"Error reading {edf_path}: {e}")
        return False
    meas_date = edf.info["meas_date"]
    ch_names = list(edf.info["ch_names"])
    # TODO: maybe support non-UTC? chances are the device is not UTC aware either
    assert meas_date.utcoffset() in (datetime.timedelta(0), None)

    # Create channels if they don't exist, and get their IDs
    db.executemany("INSERT OR IGNORE INTO ch (name) VALUES (?)", [(ch_name,) for ch_name in ch_names])
    ch_ids = {ch_name: ch_id for ch_id, ch_name in db.execute("SELECT id, name FROM ch")}

    data, times = edf.get_data(return_times=True)
    for time_offset, row in zip(times, data.T, strict=True):
        time = meas_date + datetime.timedelta(seconds=time_offset)
        datas = [
            (time.timestamp(), ch_ids[ch_name], float(value))
            for ch_name, value in zip(ch_names, row)
            if ch_name != "Crc16"
        ]
        db.executemany("INSERT OR IGNORE INTO edf (ts, ch_id, value) VALUES (?, ?, ?)", datas)
    return True


def convert_edfs_to_sqlite(edfs: Iterable[Path], db: sqlite3.Connection):
    db.execute("CREATE TABLE IF NOT EXISTS ch (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    db.execute("CREATE TABLE IF NOT EXISTS edf (ts NUMBER, ch_id INTEGER, value NUMBER)")
    db.execute("CREATE UNIQUE INDEX IF NOT EXISTS edf_ts_ch ON edf (ts, ch_id)")
    db.executescript(
        """
    pragma journal_mode = WAL;
pragma synchronous = normal;
pragma temp_store = memory;
pragma mmap_size = 30000000000;
    """,
    )
    with tqdm.tqdm(edfs) as pbar:
        for edf_path in pbar:
            pbar.set_description(f"Reading {edf_path}")
            write_from_edf(db, edf_path)
    db.commit()
