# Study setup: preparing input files and metadata

[Back to README](../README.md)

nimbalwear organizes all work around a **study**: a folder that holds raw data, metadata, settings, outputs and
reports. Within a study, each **collection** is one data collection session for one participant, identified by
`subject_id` and `coll_id`. A collection can include several devices.

## 1. Create a study

```python
from nimbalwear import Study

study = Study("/data/MYSTUDY", create=True)
```

- `create=True` creates the folder and a hidden `.nimbalwear` marker file. `Study` only opens folders that contain
  this marker.
- If the folder already exists, it is not created again. If it exists but has no marker, you get a
  `FileNotFoundError`.
- The folder name (`MYSTUDY`) becomes the `study_code`. The `study_code` column in `devices.csv` and
  `collections.csv` must match it.

To open an existing study later:

```python
study = Study("/data/MYSTUDY")
```

## 2. Folder layout

Opening a study creates any folders that are missing. The default layout, defined in `[study.dirs]` of the
[settings](configuration.md), is:

```text
MYSTUDY/
├── .nimbalwear
├── study/
│   ├── devices.csv              # device metadata (you fill this in)
│   ├── collections.csv          # collection metadata (you fill this in)
│   ├── status.csv               # pipeline status (generated)
│   ├── supplementary_info.xlsx  # optional, used by the collection report
│   ├── settings/settings.toml   # study settings (copied from package defaults)
│   └── logs/                    # per-collection logs and settings dumps
├── wearables/
│   ├── raw/                     # raw device files go here
│   ├── device_edf_raw/          # converted EDF
│   ├── device_edf_standard/     # calibrated and synchronized EDF
│   ├── device_edf_cropped/      # cropped EDF (input to analytics)
│   └── sensor_edf/              # optional per-sensor EDF
├── analytics/
│   ├── calib/
│   ├── sync/{events,segments}/
│   ├── nonwear/{bouts_standard,bouts_cropped,daily_standard,daily_cropped}/
│   ├── activity/{epochs,bouts,daily,avm}/
│   ├── gait/{steps,bouts,daily}/
│   ├── sleep/{sptw,bouts,daily}/
│   └── events/custom/
└── reports/
    ├── collection/
    └── feedback/
```

See [outputs.md](outputs.md) for what is written to each folder.

## 3. Add raw device files

Copy the raw files into `wearables/raw/`. Each file name must match a `file_name` entry in `devices.csv`.

| `device_type` | Expected raw file |
|---|---|
| `GNOR` | GENEActiv `.bin` |
| `AXV6` | Axivity AX6 `.cwa` |
| `BF18`, `BF36` | Bittium Faros `.edf` |
| `EDF` | An EDF file already in nimbalwear format |

If raw files arrive in another folder (a shared drive, for example), `Study.sync_raw()` can copy any new files for
you. See [advanced.md](advanced.md#syncing-raw-files-from-a-source-folder).

## 4. Fill in `study/devices.csv`

`devices.csv` has one row per device file. Its columns are:

| Column | Description |
|---|---|
| `study_code` | Must match the study folder name |
| `subject_id` | Participant ID (read as text, so leading zeros are kept) |
| `coll_id` | Collection ID for this participant (for example `01`) |
| `device_type` | One of `GNOR`, `AXV6`, `BF18`, `BF36`, `EDF` |
| `device_id` | Device serial number, compared against the file header |
| `device_location` | Body location. Must match one of the location aliases (see below) for analytics to find the device |
| `file_name` | File name inside `wearables/raw/` |

Example:

```csv
study_code,subject_id,coll_id,device_type,device_id,device_location,file_name
MYSTUDY,0001,01,AXV6,12345,LWRIST,0001_01_LW.cwa
MYSTUDY,0001,01,AXV6,12346,LANKLE,0001_01_LA.cwa
MYSTUDY,0001,01,AXV6,12347,RANKLE,0001_01_RA.cwa
MYSTUDY,0001,01,BF36,A1B2C3,CHEST,0001_01_CH.edf
```

**Device locations.** Locations are matched case-insensitively against the aliases in
`[pipeline.device_locations]`:

| Location key | Default aliases | Used by |
|---|---|---|
| `lwrist` | `LW`, `LEFTWRIST`, `LWRIST` | activity, sleep, wrist non-wear thresholds |
| `rwrist` | `RW`, `RIGHTWRIST`, `RWRIST` | activity, sleep, wrist non-wear thresholds |
| `lankle` | `LA`, `LEFTANKLE`, `LANKLE` | gait, ankle non-wear thresholds |
| `rankle` | `RA`, `RIGHTANKLE`, `RANKLE` | gait, ankle non-wear thresholds |
| `chest` | `CHEST` | chest non-wear thresholds |

You can add aliases in the settings (see [configuration.md](configuration.md#add-device-location-aliases)).

**Row order matters for sync.** The **first** device listed for a collection is the sync reference. All other
devices in the collection are synchronized to it.

**Header checks.** When a file is read, its header (`study_code`, `subject_id`, `coll_id`, `device_type`,
`device_id`, `device_location`) is compared with the `devices.csv` row. Any mismatch is logged as a warning. With the
default `[modules.read] overwrite_header = true`, the values from `devices.csv` replace the header values. Personal
fields (name, sex, birthdate) are always removed.

## 5. Fill in `study/collections.csv`

`collections.csv` has one row per collection. `run_pipeline()` processes the collections listed here by default.

| Column | Description |
|---|---|
| `study_code` | Must match the study folder name |
| `subject_id` | Participant ID |
| `coll_id` | Collection ID |
| `dominant_hand` | `right` or `left` (case-insensitive). Used to pick the wrist for sleep and to label activity cutpoints as dominant or non-dominant. Leave blank if unknown. |
| `age` | Age in whole years. **Required for activity**: it selects the cutpoint set (see [configuration.md](configuration.md#modulesactivity)). |
| `var_1`, `var_2`, `var_3` | Free-form fields shown in the collection report |

Example:

```csv
study_code,subject_id,coll_id,dominant_hand,age,var_1,var_2,var_3
MYSTUDY,0001,01,right,67,,,
MYSTUDY,0002,01,left,45,,,
```

After editing either CSV file, open the study again (`Study("/data/MYSTUDY")`), because the files are read when the
study is opened.

## 6. Device placement for each analysis

| Analysis | Required device | Notes |
|---|---|---|
| Non-wear | Any device with Accelerometer x/y/z and Temperature | Devices without these signals are skipped |
| Activity | `GNOR` or `AXV6` on a wrist | Each wrist device is analyzed separately |
| Sleep | `GNOR` or `AXV6` on a wrist | With two wrists, the non-dominant one is used by default (`[modules.sleep] dominant`) |
| Gait | `GNOR` or `AXV6` on one or both ankles | Uses `Gyroscope z` (gyro mode) or `Accelerometer x` (accel mode) by default |
| Sync | Two or more devices with accelerometers | Needs flip sync events recorded during the collection |

Orientation matters for gait: the default signal labels assume the device orientation described in
[Wearable device orientation](Wearable%20device%20orientation.docx).

### Recording sync events

Devices are aligned using **flip sync events**: all devices are held together and flipped quickly several times
(at least `min_flips`, default 4), with a rest before and after. Record sync events at the start and end of a
collection, and ideally at intermediate visits. The device's configuration time can also be used as a sync point
(`sync_at_config = true`). See [Wearable device usage guide](Wearable%20device%20usage%20guide.docx) for the
procedure and [configuration.md](configuration.md#modulessync) for tuning options.

## 7. Optional: supplementary information

The collection report can include extra participant information from an Excel workbook at
`study/supplementary_info.xlsx` (the location can be changed with `[modules.collection_report] supp_path`).

- The first sheet must have `subject_id` and `coll_id` columns. All other columns are shown in the report for the
  matching collection.
- If the workbook is password-protected, pass the password with `run_pipeline(supp_pwd="...")`.
- If you do not provide this file, set `include_supp = false` in `[modules.collection_report]`. See
  [limitations.md](limitations.md).

## 8. Optional: custom events

Logged events (device removals, time in bed, naps, medication) can be imported from a CSV file and are shown in the
collection report. See [advanced.md](advanced.md#custom-events).

## Setup checklist

- [ ] Study created with `Study(..., create=True)`
- [ ] Raw files copied to `wearables/raw/`
- [ ] One row per device file in `devices.csv`, with the sync reference device listed first
- [ ] `device_location` values match the configured aliases
- [ ] One row per collection in `collections.csv`, with `age` filled in (and `dominant_hand` if known)
- [ ] `supplementary_info.xlsx` present, or `include_supp = false`
- [ ] Study opened again after editing the CSV files

Next: [Running the pipeline](running-pipeline.md).
