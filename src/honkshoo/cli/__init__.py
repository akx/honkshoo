from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

import click
import matplotlib.pyplot as plt

from honkshoo.__about__ import __version__


@click.group()
@click.version_option(version=__version__, prog_name="honkshoo")
@click.option("--log-level", "-l", default="INFO", type=click.Choice(("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")))
def honkshoo(log_level):
    logging.basicConfig(level=log_level)


@honkshoo.command("convert-to-sqlite", help="Convert EDF files to SQLite database")
@click.argument("edfs", nargs=-1, type=click.Path(exists=True, file_okay=True, path_type=Path))
@click.option("--output-database", "-o", default=":memory:")
def convert_to_sqlite(
    edfs: tuple[Path],
    output_database: str,
) -> None:
    from honkshoo.conversion.sqlite3 import SQLiteConverter
    with sqlite3.connect(output_database) as db:
        SQLiteConverter(db).read_edfs(edfs)


@honkshoo.command("visualize-sqlite", help="Visualize channels from SQLite database")
@click.argument("database", nargs=1, type=click.Path(exists=True, file_okay=True, path_type=Path))
@click.option("--channels", "-c", multiple=True)
@click.option("--output", "-o", help="Output image file")
def visualize_sqlite(
    database: Path,
    channels: tuple[str] | None,
    output: str | None = None,
) -> None:
    from honkshoo.visualization import plot_channels

    with sqlite3.connect(database) as db:
        plot_channels(db, channels=(channels or None))
    if output:
        plt.savefig(output)
    else:
        plt.show()


@honkshoo.command("mimimi", hidden=True)
def mimimi() -> None:
    tag = click.style("#sleeps with a feather over my mouth that goes up and down as i breathe", dim=True)
    print(
        f"""
<@moisturiser> me sleeping: honk shoo honk shoo honk shoo
<@eliteknightcats> me sleeping: snrrrk mi mi mi mi snrrrk mi mi mi mi
                   {tag}
""".strip(),
    )
