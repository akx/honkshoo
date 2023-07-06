from __future__ import annotations

import logging
from urllib.parse import urljoin

import httpx

from honkshoo.conversion.base import Converter
from honkshoo.conversion.helpers import batched, open_edf, process_edf_to_samples
from honkshoo.helpers import override_log_level


class InfluxDBConverter(Converter):
    def __init__(
        self,
        *,
        url: str,
        token: str,
        org: str,
        bucket: str,
    ):
        self.client = httpx.Client()
        self.bucket = bucket
        self.client.headers["Authorization"] = f"Token {token}"
        self.org = org
        self.url = url

    def finalize(self):
        self.client.close()

    def read_edf(self, edf_path: str):
        edf = open_edf(edf_path)
        records = (
            f"honkshoo,channel={channel} value={value!s} {int(ts.timestamp() * 1_000_000)}"
            for ts, channel, value in process_edf_to_samples(edf)
        )
        # httpx insists on INFOing every request it makes, and we make quite some requests
        with override_log_level(logging.getLogger("httpx"), logging.WARNING):
            for batch in batched(records, 10_000):
                resp = self.client.post(
                    url=urljoin(self.url, f"/api/v2/write?org={self.org}&bucket={self.bucket}&precision=us"),
                    content="\n".join(batch).encode("UTF-8"),
                    headers={"Content-Type": "text/plain; charset=utf-8"},
                )
                resp.raise_for_status()
