# Honkshoo

Honkshoo reads, converts and visualizes data from CPAP machines.

There is no guarantee that the data read is currently correct in any way.

Currently supported is

* EDF data from ResMed machines (tested with AirSense 11).

## Installation

In a virtualenv,

```
pip install -e .
```

## Usage (visualization)

Once you have a directory (structure) with EDF files, you can run

```
honkshoo convert-to-sqlite data/DATALOG/20230703/*.edf -o ./20230703.sqlite3
honkshoo visualize-sqlite ./20230703.sqlite3
```

## Usage (InfluxDB ingestion)

You can use Honkshoo to ingest EDF files into an InfluxDB time-series database.

This requires the package to have been installed with the `influxdb` extra, so `pip install -e .[influxdb]`.

Then, you can run e.g.

```
honkshoo ingest-to-influxdb ./data/DATALOG/20230703/*.edf --influxdb-token=my-token --influxdb-bucket=honk
```

You can then use e.g. Grafana to visualize the data.
