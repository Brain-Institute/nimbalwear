# Advanced features

[Back to README](../README.md)

## Custom events

Events logged by participants or staff, such as device removals, time in bed or medication, can be imported from a
CSV file. They are stored for each collection in `analytics/events/custom/` and shown in the collection report.

```python
study.add_custom_events("/data/MYSTUDY_diary_events.csv")
```

**Input format.** Each event is identified by `study_code`, `subject_id`, `coll_id`, `event` and `id`, and that
combination must be unique within the file.

| Column | Required | Description |
|---|---|---|
| `study_code` | yes | Must match the current study |
| `subject_id` | yes | Participant ID |
| `coll_id` | yes | Collection ID |
| `event` | yes | Event type (see below) |
| `id` | yes | Integer, unique within each event type for a collection |
| `start_time` | yes | Date and time, for example `2024-05-01 22:15:00` |
| `end_time` | no | Date and time. If blank, the report uses the event type's default duration. |
| `details` | no | Free text |
| `notes` | no | Free text |

```csv
study_code,subject_id,coll_id,event,id,start_time,end_time,details,notes
MYSTUDY,0001,01,in_bed,1,2024-05-01 22:15:00,2024-05-02 06:40:00,,
MYSTUDY,0001,01,removal,1,2024-05-02 18:00:00,2024-05-02 18:45:00,shower,
MYSTUDY,0001,01,meds,1,2024-05-02 08:00:00,,levodopa 100mg,
```

**Replace behaviour.** Importing replaces all existing events of the same `event` type for that collection. Other
event types are kept. To correct one event type, re-import the full list for that type.

**Event types the collection report can display:**

| `event` | Label in report |
|---|---|
| `removal` | Device removal (logged) |
| `in_bed` | In bed (logged) |
| `lights_out` | Lights out (logged) |
| `nap` | Nap (logged) |
| `activity` | Activity (logged) |
| `meds` | Medication (5-minute default duration) |

Use only these types if `include_custom = true`. See [limitations.md](limitations.md).

## Per-collection settings

To override settings for specific collections (for example, a different gait signal because of a known device
orientation), create a TOML file named `study/settings/{study_code}_{subject_id}_{coll_id}_settings.toml`:

```toml
# study/settings/MYSTUDY_0001_01_settings.toml
[modules.gait]
vert_accel = "Accelerometer y"
```

Then run with `settings_path='auto'`:

```python
study.run_pipeline(settings_path="auto")
```

For each collection, the per-collection file is merged over the study settings if it exists. Collections without a
file use the study settings.

## One-off setting overrides

Pass any TOML file to apply it to a single run:

```python
study.run_pipeline(stages=["prep", "analytics"], settings_path="/path/to/strict_nonwear.toml")
```

Or to every run of a `Study` object:

```python
study = Study("/data/MYSTUDY", settings_path="/path/to/overrides.toml")
```

See [configuration.md](configuration.md#how-settings-are-layered) for how the layers are merged.

## Adjusting device start times

If a device clock was set wrong (for example, the wrong time zone or daylight saving time), shift all device start
times in a collection by an ISO 8601 duration during `prep`:

```toml
[modules.prep]
adj_start = "-PT1H"     # subtract 1 hour; "+PT30M" adds 30 minutes, "P1D" adds 1 day
```

The shift is applied before calibration and synchronization. Because it applies to every device in the collection,
it is usually set in a per-collection settings file.

## Tuning synchronization

Sync accuracy depends on clear flip events. If sync points are missed or rejected:

- Increase `search_radius` (minutes) when device clocks drift a lot between visits.
- Lower `req_tgt_corr` (for example to `0.7`) to accept weaker matches in the target device.
- Lower `min_flips` if fewer flips were done during collection.
- Raise `reject_above_ae` if reference flips are noisy.
- Set `sync_at_config = false` if the device configuration times are unreliable.

Check `analytics/sync/events/` and the sync markers in the collection report to confirm the result.

## Syncing raw files from a source folder

If raw files are uploaded to a separate location (such as a shared drive), `sync_raw()` copies any files that are
not already in `wearables/raw/`:

```python
# one-off copy from a folder
study.sync_raw("/mnt/incoming/MYSTUDY")

# copy, and save this folder as the study's default source
study.sync_raw("/mnt/incoming/MYSTUDY", update_default=True)

# later: copy from the saved default source
study.sync_raw()
```

- `update_default=True` writes the folder to `[study.abs_dirs] raw_source` in `study/settings/settings.toml`.
- `update_source=True` uses the folder for the current `Study` object only.
- Existing files are never overwritten. Hidden files (names starting with `.`) are skipped.

## Storing data outside the study folder

Any folder in `[study.dirs]` can be redirected to an absolute path with `[study.abs_dirs]`:

```toml
[study.abs_dirs]
device_raw = "/mnt/secure/MYSTUDY/raw"
device_edf_raw = "/mnt/fast/MYSTUDY/edf_raw"
```

## Per-sensor EDF files

To share or archive data by sensor, turn on `save_sensors`:

```toml
[modules.prep]
save_sensors = true
```

After cropping, each device is also saved as one EDF file per sensor type in `wearables/sensor_edf/`, for example
`MYSTUDY_0001_01_AXV6_LWRIST_ACCELEROMETER.edf`. Sensor groups are defined in `[pipeline.sensors]`.

## Logging and verbosity

```python
import logging

study.run_pipeline(quiet=True, log=True, log_level=logging.DEBUG)
```

- `quiet=True` hides console messages. Log files are still written if `log=True`.
- `log=False` turns off log files. The settings dump is still written.

## Running subsets

```python
# all collections for one participant
colls = [c for c in study.get_collections() if c[0] == "0001"]
study.run_pipeline(collections=colls)

# turn off specific analytics for one run
# no_sleep.toml:
#   [modules.analytics]
#   sleep = false
study.run_pipeline(stages=["analytics"], settings_path="no_sleep.toml")
```

When gait or sleep is turned off, activity has no gait or sleep results to use in that run. Sedentary epochs are
not labelled `sedentary_gait`, and sleep windows are not excluded.
