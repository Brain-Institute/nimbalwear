# nimbalwear

nimbalwear is an open source Python toolkit for processing data from wearable sensors. It takes raw files from
research-grade wearables, converts them to a standardized EDF format, prepares them (calibration, synchronization,
non-wear detection, cropping) and produces standardized analytics for **activity**, **gait** and **sleep**, along with
an HTML collection report for each participant.

## Contents

- [Features](#features)
- [Supported devices](#supported-devices)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Documentation](#documentation)
- [Changelog](#changelog)
- [License](#license)

## Features

| Step | What it does |
|---|---|
| Convert | Reads native device files and writes standardized, de-identified EDF files |
| Auto-calibration | Gravity-based accelerometer calibration with temperature correction (van Hees et al., 2014) |
| Synchronization | Aligns multiple devices to a reference device using "flip" sync events and corrects clock drift |
| Non-wear detection | DETACH algorithm with location-specific (wrist, ankle, chest) thresholds |
| Cropping | Removes non-wear at the start and end of each recording |
| Activity | Wrist-based activity intensity (sedentary, light, moderate, vigorous) using age-based cutpoints (Powell, Fraysse) |
| Gait | Ankle-based step and walking bout detection from gyroscope or accelerometer data |
| Sleep | Sleep period time windows and sleep bouts from wrist data (HDCZA, van Hees et al., 2018) |
| Reports | Per-collection HTML report with a daily event plot |

## Supported devices

| `device_type` | Device | Raw file | Signals |
|---|---|---|---|
| `GNOR` | GENEActiv Original | `.bin` | Accelerometer x/y/z, Temperature, Light, Button |
| `AXV6` | Axivity AX6 | `.cwa` | Accelerometer x/y/z, Gyroscope x/y/z, Temperature, Light |
| `BF18`, `BF36` | Bittium Faros 180 / 360 | `.edf` | ECG, Accelerometer x/y/z, Temperature (varies by model) |
| `EDF` | Any EDF file already in nimbalwear format | `.edf` | As stored |

Activity and sleep analytics need a wrist-worn `GNOR` or `AXV6`. Gait analytics need an ankle-worn `GNOR` or `AXV6`.
See [docs/limitations.md](docs/limitations.md) for more on device support.

## Installation

nimbalwear requires Python 3.9–3.12 (newer versions cannot build the pinned matplotlib). These instructions install
from the [Brain-Institute/nimbalwear](https://github.com/Brain-Institute/nimbalwear) fork. To install the latest
version from its `main` branch:

```bash
pip install git+https://github.com/Brain-Institute/nimbalwear
```

To pin a specific version, add a tag or commit hash after `@`, for example:

```bash
pip install git+https://github.com/Brain-Institute/nimbalwear@<tag-or-commit>
```

To add nimbalwear as a dependency of another package, put this in `install_requires` (replace `[ref]` with a tag,
branch or commit):

```python
install_requires=['nimbalwear@git+https://github.com/Brain-Institute/nimbalwear@[ref]']
```

The fork is based on the original [nimbal/nimbalwear](https://github.com/nimbal/nimbalwear) project.

See [docs/installation.md](docs/installation.md) for virtual environments, installing for development, and
troubleshooting.

## Quickstart

nimbalwear has no command-line tool. You run it from a Python script or notebook.

1. **Create a study.** The folder name becomes the study code.

   ```python
   from nimbalwear import Study

   study = Study("/data/MYSTUDY", create=True)
   ```

   This creates the study folder tree, a copy of the default settings in `study/settings/settings.toml`, and empty
   `study/devices.csv` and `study/collections.csv` files.

2. **Copy the raw device files** into `MYSTUDY/wearables/raw/`.

3. **Describe each device file** in `MYSTUDY/study/devices.csv`:

   ```csv
   study_code,subject_id,coll_id,device_type,device_id,device_location,file_name
   MYSTUDY,0001,01,AXV6,12345,LWRIST,0001_01_LW.cwa
   MYSTUDY,0001,01,AXV6,12346,LANKLE,0001_01_LA.cwa
   MYSTUDY,0001,01,AXV6,12347,RANKLE,0001_01_RA.cwa
   ```

4. **Describe each collection** in `MYSTUDY/study/collections.csv`:

   ```csv
   study_code,subject_id,coll_id,dominant_hand,age,var_1,var_2,var_3
   MYSTUDY,0001,01,right,67,,,
   ```

5. **Run the pipeline.** Reload the study so it picks up the edited CSV files:

   ```python
   study = Study("/data/MYSTUDY")
   study.run_pipeline()
   ```

6. **Check the results:**
   - `study/status.csv` records success or failure for each stage of each collection
   - `study/logs/` holds a log file and a settings dump for each collection run
   - `wearables/device_edf_*` holds the standardized EDF files
   - `analytics/` holds the CSV outputs
   - `reports/collection/` holds the HTML reports

## Documentation

| Guide | Contents |
|---|---|
| [Installation](docs/installation.md) | Environments, installing, checking the install, development setup |
| [Study setup](docs/study-setup.md) | Study folder layout, raw files, `devices.csv`, `collections.csv`, supplementary info, device placement and sync |
| [Running the pipeline](docs/running-pipeline.md) | `run_pipeline()` options, stages, re-running stages, logs and status |
| [Configuration](docs/configuration.md) | How settings are layered, full `settings.toml` reference, common recipes |
| [Outputs](docs/outputs.md) | Standardized EDF files, analytics CSV files and their columns, collection report |
| [Advanced features](docs/advanced.md) | Custom events, per-collection settings, start-time adjustment, raw data syncing, sensor files |
| [Python API](docs/python-api.md) | Using `Device` and the analysis modules directly, without the pipeline |
| [Limitations](docs/limitations.md) | Known limitations and common pitfalls |

Device placement and handling guides (Word documents):

- [Wearable device orientation](docs/Wearable%20device%20orientation.docx)
- [Wearable device usage guide](docs/Wearable%20device%20usage%20guide.docx)

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

See [LICENSE](LICENSE).
