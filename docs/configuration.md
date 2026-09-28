# Configuration

[Back to README](../README.md)

All pipeline behaviour is controlled by TOML settings. The package defaults are in
[src/nimbalwear/settings/settings.toml](../src/nimbalwear/settings/settings.toml).

## How settings are layered

Settings are merged from four levels. Nested tables are merged key by key, so an override file only needs the keys
you want to change.

| Order | Source | Scope |
|---|---|---|
| 1 | Package defaults (`nimbalwear/settings/settings.toml`) | All studies |
| 2 | `study/settings/settings.toml`, copied from the defaults the first time a study is opened | This study |
| 3 | `Study(study_dir, settings_path=...)` | Every run on this `Study` object |
| 4 | `run_pipeline(settings_path=...)`, or `settings_path='auto'` for a per-collection file | This run only |

To change settings for a whole study, edit `study/settings/settings.toml`. For one-off changes, write a small
override file:

```toml
# only_accel_gait.toml
[modules.gait]
step_detect_type = "accel"
```

```python
study.run_pipeline(stages=["analytics"], settings_path="only_accel_gait.toml")
```

The final merged settings for each collection run are saved to `study/logs/*_settings.txt`.

## Settings reference

### `[study.dirs]`

Folder paths relative to the study folder (see [study-setup.md](study-setup.md#2-folder-layout)). Each key is used
internally (for example `device_raw`, `device_edf_cropped`, `activity_daily`, `reports_collection`), so keep the keys
and change only the values.

### `[study.abs_dirs]` (optional)

Absolute paths that override or add to `[study.dirs]`. For example, to keep raw files outside the study:

```toml
[study.abs_dirs]
device_raw = "/mnt/share/MYSTUDY_raw"
raw_source = "/mnt/incoming/MYSTUDY"   # used by Study.sync_raw()
```

### `[pipeline]`

| Key | Default | Description |
|---|---|---|
| `stages` | `["convert", "prep", "analytics", "reports"]` | Stages run when `run_pipeline(stages=None)` |

### `[pipeline.sensors.*]`

Standard signal labels for each sensor type. They are used to find signals and to split files when `save_sensors` is
on.

| Sensor | Signals |
|---|---|
| `accelerometer` | `Accelerometer x`, `Accelerometer y`, `Accelerometer z` |
| `gyroscope` | `Gyroscope x`, `Gyroscope y`, `Gyroscope z` |
| `ecg` | `ECG` |
| `plsox` | `Pulse`, `SpO2` |
| `temperature` | `Temperature` |
| `light` | `Light` |
| `button` | `Button` |

### `[pipeline.device_locations.*]`

Aliases for `lankle`, `rankle`, `lwrist`, `rwrist` and `chest`. Each alias is compared with the upper-cased
`device_location` in `devices.csv`. See [study-setup.md](study-setup.md#4-fill-in-studydevicescsv).

### `[modules.read]`

| Key | Default | Description |
|---|---|---|
| `overwrite_header` | `true` | Replace mismatched header fields with values from `devices.csv` |

### `[modules.prep]`

| Key | Default | Description |
|---|---|---|
| `adj_start` | `""` | Shift all device start times by an ISO 8601 duration, for example `"+PT1H"` or `"-PT30M"`. An empty string turns this off. |
| `autocal` | `true` | Run accelerometer auto-calibration |
| `sync` | `true` | Synchronize devices to the first device listed |
| `nonwear` | `true` | Run non-wear detection |
| `crop` | `true` | Crop non-wear at the start and end |
| `save_sensors` | `false` | Also write one EDF file per sensor to `wearables/sensor_edf/` |

### `[modules.analytics]` and `[modules.reports]`

| Key | Default | Description |
|---|---|---|
| `analytics.gait` | `true` | Run gait analysis |
| `analytics.sleep` | `true` | Run sleep analysis |
| `analytics.activity` | `true` | Run activity analysis |
| `reports.collection_report` | `true` | Generate the HTML collection report |

### `[modules.autocal]`

| Key | Default | Description |
|---|---|---|
| `save` | `true` | Write calibration results to `analytics/calib/` |

### `[modules.sync]`

| Key | Default | Description |
|---|---|---|
| `type` | `"flip"` | Sync detection method (only `flip` is available) |
| `sync_at_config` | `true` | Use the reference device's configuration time as an extra sync point |
| `search_radius` | `60` | Minutes around each reference sync in which to search for the matching target sync |
| `rest_min` / `rest_max` | `2` / `15` | Minimum and maximum rest durations around a flip sequence |
| `rest_sens` | `0.12` | Acceleration variability threshold for detecting rest |
| `flip_max` | `2` | Maximum duration of one flip |
| `min_flips` | `4` | Minimum number of flips for a valid sync event |
| `reject_above_ae` | `0.2` | Reject reference sync events whose alignment error is above this |
| `req_tgt_corr` | `0.8` | Minimum correlation between reference and target sync signals |
| `save` | `true` | Write sync events and segments to `analytics/sync/` |

### `[modules.nonwear]`

`save = true` writes non-wear outputs. The DETACH thresholds are set separately for each location type. The type is
decided by which aliases the device location matches:

| Key | Wrist | Ankle | Chest | Description |
|---|---|---|---|---|
| `accel_std_thresh_mg` | 8 | 9 | 5 | Accelerometer standard deviation threshold (mg) |
| `low_temperature_cutoff` | 26 | 23 | 25 | Temperature (°C) below which non-wear is likely |
| `high_temperature_cutoff` | 30 | 31.5 | 30 | Temperature (°C) above which wear is likely |
| `temp_dec_roc` | -0.2 | -0.3 | -0.1 | Rate of temperature decrease that suggests removal (°C/min) |
| `temp_inc_roc` | 0.1 | 0.05 | 0.05 | Rate of temperature increase that suggests putting the device on (°C/min) |

Tables: `[modules.nonwear.settings.wrist]`, `[modules.nonwear.settings.ankle]`, `[modules.nonwear.settings.chest]`.

### `[modules.crop]`

| Key | Default | Description |
|---|---|---|
| `min_wear_time` | `120` | Minutes. Data before the first and after the last wear bout of at least this length is cropped. |
| `save` | `true` | Write cropped non-wear outputs |

### `[modules.activity]`

| Key | Default | Description |
|---|---|---|
| `lowpass` | `20` | Low-pass filter cutoff (Hz) applied before computing vector magnitude |
| `epoch_length` | `15` | Epoch length (seconds) |
| `sedentary_gait` | `true` | Label sedentary epochs that overlap gait bouts as `sedentary_gait` |
| `pref_cutpoint` | not set | `"dominant"` or `"non-dominant"` forces which cutpoint variant is used. If not set, it is decided from `dominant_hand`, and dominant is assumed when `dominant_hand` is unknown. |
| `save` | `true` | Write activity outputs |

Cutpoints are chosen by age from the `[[modules.activity.cutpoints]]` array:

```toml
[[modules.activity.cutpoints]]
min_age = 0
max_age = 59
type = "Powell"

[[modules.activity.cutpoints]]
min_age = 60
max_age = 999
type = "Fraysse"
```

The age ranges must not overlap, and together they must cover every participant's age. Available cutpoint types, as
average vector magnitude thresholds in g (see `avm_cutpoints()` in [activity.py](../src/nimbalwear/activity.py)):

| Type | Wrist | Light | Moderate | Vigorous |
|---|---|---|---|---|
| `Powell` | dominant | 0.1133 | 0.1511 | 0.3156 |
| `Powell` | non-dominant | 0.1044 | 0.1422 | 0.3489 |
| `Fraysse` | dominant | 0.0625 | 0.0925 | – |
| `Fraysse` | non-dominant | 0.0425 | 0.098 | – |

### `[modules.sleep]`

| Key | Default | Description |
|---|---|---|
| `dominant` | `false` | With two wrist devices and a known `dominant_hand`, use the dominant (`true`) or non-dominant (`false`) wrist |
| `save` | `true` | Write sleep outputs |

### `[modules.gait]`

| Key | Default | Description |
|---|---|---|
| `step_detect_type` | `"gyro"` | `"gyro"` (Fraccaro peak detection) or `"accel"` (state-space algorithm) |
| `vert_accel` | `"Accelerometer x"` | Vertical acceleration signal used in `accel` mode |
| `sag_gyro` | `"Gyroscope z"` | Sagittal-plane gyroscope signal used in `gyro` mode |
| `save` | `true` | Write gait outputs |

### `[modules.collection_report]`

| Key | Default | Description |
|---|---|---|
| `include_supp` | `true` | Include `supplementary_info.xlsx` |
| `supp_path` | not set | Alternative path to the supplementary workbook |
| `include_custom` | `true` | Include custom events from `analytics/events/custom/` |
| `daily_plot` | `true` | Include a daily event plot |
| `fig_size` | `[18, 12]` | Plot size (inches) |
| `top_y` / `bottom_y` | `[0.25, 1.0]` / `[0.0, 0.2]` | Vertical plot areas for detected and logged events |

## Recipes

### Turn off sync (single-device studies)

```toml
[modules.prep]
sync = false
```

### Use accelerometer-based gait detection

```toml
[modules.gait]
step_detect_type = "accel"
vert_accel = "Accelerometer x"
```

### Change activity cutpoints by age

```toml
[[modules.activity.cutpoints]]
min_age = 0
max_age = 999
type = "Powell"
```

Arrays of tables such as `cutpoints` are **replaced** as a whole, not merged. List every age range you need.

### Add device location aliases

```toml
[pipeline.device_locations.lwrist]
aliases = ["LW", "LEFTWRIST", "LWRIST", "L_WRIST"]
```

### Run analytics without a report

```toml
[pipeline]
stages = ["convert", "prep", "analytics"]
```

### Skip the supplementary info in reports

```toml
[modules.collection_report]
include_supp = false
```
