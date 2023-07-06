from __future__ import annotations

import datetime
import logging
import warnings
from collections import defaultdict
from collections.abc import Iterable
from typing import Any, Callable

import mne.io
from mne.io.edf.edf import RawEDF

from honkshoo.excs import EDFReadError

log = logging.getLogger(__name__)

Sample = tuple[Any, Any, float]


def identity(x: Any) -> Any:
    return x


def process_edf_to_samples(
    edf: RawEDF,
    *,
    map_channel_name: Callable[[str], Any] = identity,
    map_timestamp: Callable[[datetime], Any] = identity,
) -> Iterable[Sample]:
    meas_date = edf.info["meas_date"]
    # TODO: maybe support non-UTC? chances are the device is not UTC aware either
    assert meas_date.utcoffset() in (datetime.timedelta(0), None)
    ch_names = list(edf.info["ch_names"])
    data, times = edf.get_data(return_times=True)
    by_chname = defaultdict(list)
    for time_offset, row in zip(times, data.T, strict=True):
        time = meas_date + datetime.timedelta(seconds=time_offset)
        for ch_name, value in zip(ch_names, row):
            if ch_name == "Crc16":
                continue
            by_chname[ch_name].append(
                (
                    map_timestamp(time),
                    map_channel_name(ch_name),
                    float(value),
                ),
            )
    for chname, samples in by_chname.items():
        v0 = samples[0][2]
        if all(v == v0 for _, _, v in samples):
            log.info(f"Skipping constant channel {chname} (value {v0} over {len(samples)} samples)")
            continue
        yield from samples


def open_edf(edf_path):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            edf = mne.io.read_raw_edf(edf_path, preload=True, verbose="WARNING")
    except Exception as e:
        msg = f"Error reading {edf_path}: {e}"
        raise EDFReadError(msg) from e
    return edf


def batched(gen, batch_size: int):
    batch = []
    for item in gen:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
