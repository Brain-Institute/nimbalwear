# Limitations and common pitfalls

[Back to README](../README.md)

These notes describe how the current version (see [CHANGELOG.md](../CHANGELOG.md)) behaves. Following them avoids
most processing failures.

## Device support

- **Axivity:** only the AX6 (`AXV6`) is supported. AX3 files are not.
- **Nonin (`NOWO`):** Nonin support was removed in v0.21.5. `NOWO` still appears in the list of device types
  internally, but the import no longer exists. Do not list `NOWO` devices in `devices.csv`.
- **Sibel:** `nimbalwear.files.SibelFile` can read Sibel `.asc` files, but Sibel is not a pipeline device type.
- **Analytics device types:** activity, sleep and gait only use `GNOR` and `AXV6` devices. Bittium chest devices are
  converted, calibrated and synchronized, and checked for non-wear if they have a temperature signal, but they are
  not used in analytics.
- **Accelerometer required for `prep`:** auto-calibration expects every device to have `Accelerometer x/y/z`. A
  device without them causes `prep` to fail for that collection. Set `[modules.prep] autocal = false` for such
  studies.

## Metadata

- **Location aliases:** a device is only used for analytics if its `device_location` matches one of the aliases in
  `[pipeline.device_locations]`. Otherwise the analysis fails with "No eligible ... devices found".
- **Characters in IDs:** identifiers are packed into EDF header fields that are split on spaces and underscores (see
  [outputs.md](outputs.md#standardized-edf-files)). Do not use spaces in `coll_id` or `device_location`, or
  underscores in `device_type` or `device_id`.
- **Study code:** `study_code` in the CSV files must exactly match the study folder name. Rows that don't match are
  ignored.
- **`age` is required for activity.** It must be an integer that falls within one of the
  `[[modules.activity.cutpoints]]` age ranges.
- **Device order:** the first device listed for a collection in `devices.csv` is the sync reference.
- **Re-open after editing:** `devices.csv` and `collections.csv` are read when `Study(...)` is created. Create the
  `Study` object again after editing them.

## Reports

- **Supplementary info:** with `include_supp = true` (the default), the report expects `study/supplementary_info.xlsx`
  (or the file set in `supp_path`), and the report fails if it is missing. Set `include_supp = false` if you don't
  use one.
- **Custom event types:** with `include_custom = true`, custom events must use one of the event types the report
  knows (`removal`, `in_bed`, `lights_out`, `nap`, `activity`, `meds`). Any other type causes the report to fail.
- **Report paths:** the report finds output folders from `[study.dirs]` in `study/settings/settings.toml`. Folder
  changes made only in an override file or `[study.abs_dirs]` are not used by the report.

## Pipeline behaviour

- **Stage order is not checked:** stages run in the order you give. The first stage decides which EDF folder is read
  (see [running-pipeline.md](running-pipeline.md#re-running-from-a-later-stage)).
- **Analytics depend on each other:** activity uses the gait and sleep results from the same run. If gait or sleep is
  turned off, or fails, activity runs without them.
- **Gait with two ankles:** both ankle devices must have the same sample rate. Only the period when both devices were
  recording is analyzed.
- **Signal orientation:** the default gait signals (`Gyroscope z`, `Accelerometer x`) assume the placement in
  [Wearable device orientation](Wearable%20device%20orientation.docx). For other orientations, change `sag_gyro` or
  `vert_accel`.
- **Dependency versions:** numpy must be below 2.0 and matplotlib below 3.9.
