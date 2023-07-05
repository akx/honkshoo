from __future__ import annotations

import datetime
import sqlite3

import numpy as np
from matplotlib import pyplot as plt


def plot_channels(db: sqlite3.Connection, *, channels: list[str] | None):
    ch_map = dict(db.execute("SELECT name, id FROM ch"))
    ch_map.pop("Crc16", None)
    if not channels:
        channels = tuple(ch_map)
    plotted_channels = []
    for channel in channels:
        try:
            ch_id = ch_map[channel]
        except KeyError:
            print(f"Channel {channel} not found; available channels: {', '.join(ch_map)}")
            continue
        res = [
            (datetime.datetime.fromtimestamp(ts, tz=datetime.UTC), value)
            for (ts, value) in db.execute("SELECT ts, value FROM edf WHERE ch_id = ? ORDER BY ts", (ch_id,)).fetchall()
        ]
        if not res:
            print(f"Channel {channel} has no data")
            continue
        val0 = res[0][1]
        if all(value == val0 for (_, value) in res):
            print(f"Channel {channel} is constant over {len(res)} points: {val0}, not plotting")
            continue
        data = np.array(res)
        plt.plot(data[:, 0], data[:, 1])
        plotted_channels.append(channel)
    plt.xlabel("Time")
    plt.gcf().autofmt_xdate()
    plt.legend(plotted_channels, loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
