# Outputs

[Back to README](../README.md)

All outputs are written inside the study folder. The folders are set in `[study.dirs]` and can be changed in the
[settings](configuration.md#studydirs). Every CSV output starts with the identifier columns `study_code`,
`subject_id` and `coll_id`, so files from many collections can be combined directly.

## File naming

| Output type | Pattern |
|---|---|
| Device EDF | `{study_code}_{subject_id}_{coll_id}_{device_type}_{device_location}.edf` |
| Sensor EDF | `{study_code}_{subject_id}_{coll_id}_{device_type}_{device_location}_{SENSOR}.edf` |
| Per-device CSV | `{study_code}_{subject_id}_{coll_id}_{device_type}_{device_location}_{SUFFIX}.csv` |
| Per-collection CSV | `{study_code}_{subject_id}_{coll_id}_{SUFFIX}.csv` |
| Collection report | `{study_code}_{subject_id}_{coll_id}_collection_report.html` |

## Standardized EDF files

| Folder | Written after | Contents |
|---|---|---|
| `wearables/device_edf_raw/` | `convert` | Native data converted to EDF, with headers standardized and personal fields removed |
| `wearables/device_edf_standard/` | `prep` (after `adj_start`, `autocal`, `sync`) | Calibrated, synchronized data |
| `wearables/device_edf_cropped/` | `prep` (after `nonwear`, `crop`) | Standard data with non-wear at the start and end removed. This is the input to analytics. |
| `wearables/sensor_edf/` | `prep` if `save_sensors = true` | One file per sensor (`ACCELEROMETER`, `GYROSCOPE`, `TEMPERATURE`, `LIGHT`, `BUTTON`, `ECG`, `PLSOX`) |

**EDF header mapping.** nimbalwear stores its identifiers in standard EDF header fields:

| EDF field | nimbalwear value |
|---|---|
| `admincode` | `study_code` |
| `patientcode` | `subject_id` |
| `patient_additional` | `coll_id` and `device_location`, separated by a space |
| `equipment` | `device_type` and `device_id`, separated by `_` |
| `recording_additional` | device configuration time (`YYYYmmddHHMMSS`) |
| `startdate` | recording start date and time |
| `patientname`, `sex`, `birthdate` | blank (de-identified) |

Signals use the standard labels (`Accelerometer x`, `Gyroscope z`, `Temperature`, ...) with units in the signal
headers: acceleration in g, angular velocity in degree/s, temperature in °C. The files can be opened in any EDF
reader, or loaded back with `Device().import_edf(path)` (see [python-api.md](python-api.md)).

## Analytics CSV files

All `start_time`, `end_time` and `*_time` values are local timestamps taken from the device clock, after any
`adj_start` shift and synchronization.

### Calibration: `analytics/calib/` (`*_CALIB.csv`, per device)

| Column | Description |
|---|---|
| `device_type`, `device_location`, `device_id` | Device identifiers |
| `pre_err`, `post_err` | Calibration error before and after calibration (mg) |
| `iter` | Iterations to converge |
| `offset_x/y/z`, `scale_x/y/z`, `tempoffset_x/y/z` | Calibration coefficients for each axis |

### Synchronization: `analytics/sync/events/` (`*_SYNC_EVENTS.csv`) and `analytics/sync/segments/` (`*_SYNC_SEGMENTS.csv`), per target device

- **Sync events**: one row per matched sync. Columns: `sync_id`, `start_time`, `end_time`, `ref_device_type`,
  `ref_device_location`, `ref_sig_idx`, `ref_sig_label`, `ref_start_idx`, `ref_end_idx`, `ref_flips`, `ref_ae`,
  `tgt_sig_idx`, `tgt_sig_label`, `tgt_start_idx`, `tgt_end_idx`, `tgt_corr`. A `ref_sig_label` of `Config` marks the
  configuration-time sync point.
- **Sync segments**: one row per interval between syncs. Columns: `segment_id`, `start_time`, `end_time`,
  reference and target start/end sample indices, `ref_samples`, `tgt_samples`, `tgt_drift`, `tgt_drift_rate`,
  `tgt_adjust`.

The first device listed for a collection in `devices.csv` is the reference, so it has no sync files.

### Non-wear: `analytics/nonwear/` (per device)

| Folder | File | Description |
|---|---|---|
| `bouts_standard/` | `*_NONWEAR.csv` | Wear and non-wear bouts for the whole recording |
| `bouts_cropped/` | `*_NONWEAR.csv` | Bouts left after cropping |
| `daily_standard/` | `*_NONWEAR_DAILY.csv` | Daily wear and non-wear totals for the whole recording |
| `daily_cropped/` | `*_NONWEAR_DAILY.csv` | Daily totals after cropping |

- **Bout columns:** `device_type`, `device_location`, the DETACH settings used (`accel_std_thresh_mg`,
  `low_temperature_cutoff`, `high_temperature_cutoff`, `temp_dec_roc`, `temp_inc_roc`), `id`, `event` (`wear` or
  `nonwear`), `start_time`, `end_time`.
- **Daily columns:** the same identifiers and settings, then `day_num`, `date`, `wear`, `nonwear`. Both totals are
  in **seconds**. Bouts that cross midnight are split between the days.

### Activity: `analytics/activity/` (per collection, one block of rows per wrist device)

| Folder | File | Columns |
|---|---|---|
| `epochs/` | `*_ACTIVITY_EPOCHS.csv` | `activity_epoch_num`, `device_location`, `cutpoint_type`, `cutpoint_dominant`, `start_time`, `end_time`, `avm` (mg), `intensity` |
| `bouts/` | `*_ACTIVITY_BOUTS.csv` | `activity_bout_num`, `device_location`, `cutpoint_type`, `cutpoint_dominant`, `start_time`, `end_time`, `intensity` (a bout is a run of consecutive epochs with the same intensity) |
| `daily/` | `*_ACTIVITY_DAILY.csv` | `day_num`, `date`, `device_location`, `cutpoint_type`, `cutpoint_dominant`, `type`, `none`, `sedentary`, `sedentary_gait`, `light`, `moderate`, `vigorous` (all in **minutes**) |
| `avm/` | `*_ACTIVITY_AVM.csv` | `device_location`, `avm_num`, `avm` (1-second average vector magnitude, mg) |

`intensity` is one of:

- `sedentary`, `light`, `moderate` or `vigorous`
- `sedentary_gait`: a sedentary epoch that overlaps a gait bout, when `sedentary_gait = true`
- `none`: non-wear, or a sleep period time window that contains sleep

### Gait: `analytics/gait/` (per collection)

| Folder | File | Columns |
|---|---|---|
| `steps/` | `*_GAIT_STEPS.csv` | `step_num`, `gait_bout_num` (0 means the step is not in a bout), `step_time`, `step_idx`, `loc`, `side` (`left`/`right`), `data_type` (`gyro`/`accel`), `alg` |
| `bouts/` | `*_GAIT_BOUTS.csv` | `gait_bout_num`, `start_time`, `end_time`, `step_count` |
| `daily/` | `*_GAIT_DAILY.csv` | `day_num`, `date`, `type`, `longest_bout_time` (s), `longest_bout_steps`, `bouts_over_3min`, `total_steps` |

Bouts are sequences of at least 3 steps with no gap longer than 2 seconds. With only one ankle device, the step
counts in the daily summary are doubled.

### Sleep: `analytics/sleep/` (per collection)

| Folder | File | Columns |
|---|---|---|
| `sptw/` | `*_SPTW.csv` | `sptw_num`, `relative_date`, `start_time`, `end_time`, `overnight` |
| `bouts/` | `*_SLEEP_BOUTS.csv` | `sleep_bout_num`, `sptw_num`, `bout_detect`, `start_time`, `end_time`, `overnight` |
| `daily/` | `*_SLEEP_DAILY.csv` | `day_num`, `date`, `bout_detect`, `type`, `sptw_inc`, `sptw_duration`, `sleep_duration`, `sleep_to_wake_duration`, `se`, `waso` |

- **SPTW** means sleep period time window. `relative_date` is the date of the "night": days run from noon to noon.
  `overnight` marks windows that fall in the overnight period (22:00–08:00).
- **`bout_detect`** identifies the sleep bout detection threshold used:
  - `t5a5`: z-angle change below 5° for at least 5 minutes
  - `t8a4`: z-angle change below 4° for at least 8 minutes

  Activity uses the `t8a4` bouts.
- **`sptw_inc`** identifies which windows are included in each daily summary row:
  - `long`: the longest window
  - `all`: all windows
  - `sleep`: windows that contain sleep
  - `overnight_sleep`: overnight windows that contain sleep
- Durations are in **minutes**. `se` is sleep efficiency (sleep duration divided by SPTW duration). `waso` is wake
  after sleep onset.

### Custom events: `analytics/events/custom/` (`*_EVENTS_CUSTOM.csv`)

Events imported with `Study.add_custom_events()`. Columns: `study_code`, `subject_id`, `coll_id`, `event`, `id`,
`start_time`, `end_time`, `details`, `notes`. See [advanced.md](advanced.md#custom-events).

## Collection report

The `reports` stage writes `reports/collection/{study_code}_{subject_id}_{coll_id}_collection_report.html`. When
`daily_plot = true`, it also writes figures to `reports/collection/figures/`. The report includes:

- collection information from `collections.csv` and device information from `devices.csv`
- supplementary information from `supplementary_info.xlsx` (if `include_supp = true`)
- a daily event plot and table, combining:
  - non-wear
  - periods when a device was not collecting
  - sync events
  - light, moderate and vigorous activity for each wrist
  - sleep windows and sleep bouts (day and night)
  - gait bouts
  - custom events (if `include_custom = true`)

The report is built from the saved CSV outputs, so you can regenerate it on its own with
`run_pipeline(stages=["reports"])`.

## Pipeline records

| File | Description |
|---|---|
| `study/status.csv` | Success or failure for each stage and step, one row per collection |
| `study/logs/*.log` | Full log for each collection run |
| `study/logs/*_settings.txt` | Merged settings used for each collection run |

## Combining outputs across collections

```python
from pathlib import Path
import pandas as pd

daily = pd.concat(pd.read_csv(f) for f in Path("/data/MYSTUDY/analytics/activity/daily").glob("*.csv"))
```
