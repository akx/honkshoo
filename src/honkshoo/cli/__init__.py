from __future__ import annotations

import sqlite3
from pathlib import Path

import click
import matplotlib.pyplot as plt

from honkshoo.__about__ import __version__


@click.group()
@click.version_option(version=__version__, prog_name="honkshoo")
def honkshoo():
    pass


@honkshoo.command("convert", help="Convert EDF files to SQLite database")
@click.argument("edfs", nargs=-1, type=click.Path(exists=True, file_okay=True, path_type=Path))
@click.option("--output-database", "-o", default=":memory:")
def convert(
    edfs: tuple[Path],
    output_database: str,
) -> None:
    from honkshoo.conversion import convert_edfs_to_sqlite

    convert_edfs_to_sqlite(edfs, sqlite3.connect(output_database))


@honkshoo.command("visualize", help="Visualize channels from SQLite database")
@click.argument("database", nargs=1, type=click.Path(exists=True, file_okay=True, path_type=Path))
@click.option("--channels", "-c", multiple=True)
@click.option("--output", "-o", help="Output image file")
def visualize(
    database: Path,
    channels: tuple[str] | None,
    output: str | None = None,
) -> None:
    from honkshoo.visualization import plot_channels

    db = sqlite3.connect(database)
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
""".strip()
    )
