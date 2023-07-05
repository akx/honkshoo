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
honkshoo convert data/DATALOG/20230703/*.edf -o ./20230703.sqlite3
honkshoo visualize ./20230703.sqlite3
```
