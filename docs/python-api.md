# Python API: using nimbalwear without the pipeline

[Back to README](../README.md)

The `Study` pipeline is built from smaller pieces that you can use directly in your own scripts or notebooks. This
is useful for exploring single files, testing parameters, or building custom workflows.

```python
from nimbalwear import Device                    # device data container
from nimbalwear import nonwear, activity, gait, sleep
from nimbalwear.utils import autocal, sync_devices, read_excel_pwd
from nimbalwear.files import GENEActivFile, CWAFile, EDFFile, SibelFile
```

## `Device`: reading, preparing and writing device data

A `Device` holds one recording in an EDF-like structure:

- `header`: a dict with `study_code`, `subject_id`, `coll_id`, `start_datetime`, `config_datetime`, `device_type`,
  `device_id`, `device_location`, and other fields
- `signal_headers`: a list of dicts with `label`, `dimension` (units), `sample_rate`, `physical_min/max`, and other
  fields
- `signals`: a list of numpy arrays, in the same order as `signal_headers`

### Import

| Method | File | Notes |
|---|---|---|
| `import_geneactiv(file_path, parse_data=True, start=1, end=-1, downsample=1, calibrate=True, correct_drift=True, quiet=False)` | GENEActiv `.bin` | Sets `device_type = 'GNOR'`. `correct_drift` corrects clock drift recorded at extraction. |
| `import_axivity(file_path, resample=True, quiet=False)` | Axivity `.cwa` | AX6 only. Sets `device_type = 'AXV6'`. `resample` corrects for the difference between actual and nominal sample rate. |
| `import_bittium(file_path, quiet=False)` | Bittium Faros `.edf` | Sets `BF18`, `BF36` or `BFXX`. Accelerometer is converted to g. |
| `import_edf(file_path, quiet=False)` | nimbalwear EDF | Reads files written by `export_edf` |

Each method returns `True` on success and `False` on failure.

### Prepare

| Method | Description |
|---|---|
| `autocal(use_temp=True, epoch_secs=10, detect_only=False, plot=False, quiet=False)` | Auto-calibrates the accelerometer in place. Returns `(pre_err, post_err, iterations, offset, scale, tempoffset)`. |
| `sync(ref, sig_labels=(...), sync_type='flip', sync_at_config=True, search_radius=None, ...)` | Synchronizes this device to `ref` in place. Returns `(syncs, segments)` DataFrames. |
| `crop(new_start_time=None, new_end_time=None, inplace=False)` | Crops all signals to a time window. Returns a new `Device` unless `inplace=True`. |
| `rotate_z(deg)` | Rotates the accelerometer and gyroscope axes about z |
| `deidentify()` | Clears name, sex and birthdate |

### Inspect

| Method | Description |
|---|---|
| `get_signal_index(label)` | Index of a signal by label, for example `'Accelerometer x'`, or `None` |
| `get_timestamps(sig, ts_type='timestamp')` | Timestamps for a signal (by index or label). `ts_type` is `'timestamp'`, `'datetime'`, `'mdate'` or `'unix'`. |
| `get_day_idxs(day_offset)` | Day boundary times and sample indices for each signal |
| `get_idxs_from_date(date)` | Sample index for a given datetime, for each signal |

### Export

`export_edf(file_path, sig_nums_out=None, quiet=False)` writes a standardized EDF file. To export a subset of
signals, pass their indices in `sig_nums_out`.

### Example: convert a raw file to standardized EDF

```python
from nimbalwear import Device

dev = Device()
dev.import_axivity("0001_01_LW.cwa", resample=True)
dev.deidentify()

dev.header.update({"study_code": "MYSTUDY", "subject_id": "0001", "coll_id": "01", "device_location": "LWRIST"})

pre, post, n_iter, offset, scale, tempoffset = dev.autocal()
print(f"Calibration error {pre} mg -> {post} mg")

dev.export_edf("MYSTUDY_0001_01_AXV6_LWRIST.edf")
```

## Non-wear: `nimbalwear.nonwear`

| Function | Description |
|---|---|
| `detach_nonwear(x_values, y_values, z_values, temperature_values, accel_freq, temperature_freq, std_thresh_mg, low_temperature_cutoff, high_temperature_cutoff, temp_dec_roc, temp_inc_roc, quiet=False)` | DETACH algorithm (from the `nimbaldetach` package), as used by the pipeline. Returns `(bouts_df, nonwear_array)`, where bouts use `Start Datapoint` / `End Datapoint` sample indices. |
| `vanhees_nonwear(x_values, y_values, z_values, non_wear_window=60.0, window_step_size=15, std_thresh_mg=13.0, value_range_thresh_mg=50.0, num_axes_required=2, freq=75.0, quiet=False)` | van Hees accelerometer-only method. Returns a boolean array. |
| `zhou_nonwear(x_values, y_values, z_values, temperature_values, ...)` | Zhou accelerometer plus temperature method. Returns a boolean array. |
| `nonwear_stats(nonwear_bouts, sum_type='daily')` | Daily wear and non-wear seconds from a DataFrame with `id`, `event` (`wear`/`nonwear`), `start_time`, `end_time` columns |

## Activity: `nimbalwear.activity`

| Function | Description |
|---|---|
| `activity_wrist_avm(x, y, z, sample_rate, start_datetime, lowpass=20, epoch_length=15, cutpoint='Powell', dominant=False, sedentary_gait=False, gait=..., nonwear=..., sptw=..., sleep_bouts=..., quiet=False)` | Classifies epoch intensity from wrist accelerometer data. Returns `(epochs, bouts, avm, vm, avm_sec)`. Epochs overlapping `nonwear` bouts, or `sptw` windows that contain `sleep_bouts`, are set to `none`. |
| `avm_cutpoints(cutpoint_type='Powell', dominant=False)` | Returns the cutpoint thresholds (g) |
| `activity_stats(activity_epochs, stat_type='daily')` | Daily minutes for each intensity. Takes an epochs or bouts DataFrame with `start_time`, `end_time`, `intensity`. |
| `sum_total_activity(epoch_intensity, epoch_length)` | Total minutes for each intensity |

## Gait: `nimbalwear.gait`

| Function | Description |
|---|---|
| `detect_steps(right_data=None, left_data=None, loc='ankle', data_type='accel', start_time=None, freq=None, orient_signal=True, low_pass=12)` | Detects steps from one or both ankles. With `data_type='gyro'`, pass the sagittal gyroscope signal (Fraccaro method). With `'accel'`, pass the vertical acceleration (state-space method). |
| `define_bouts(steps, freq, start_time=None, max_break=2, min_steps=2, remove_unbouted=True)` | Groups steps into bouts. Returns `(steps, bouts)`. |
| `gait_stats(bouts, stat_type='daily', single_leg=False)` | Daily gait summary |

The lower-level detectors are `nimbalwear.gait_gyro.fraccaro_gyro_steps(gyro, freq, start_time=None)` and
`nimbalwear.gait_accel.state_space_accel_steps(vert_accel, freq, start_time, ...)`.

## Sleep: `nimbalwear.sleep`

| Function | Description |
|---|---|
| `detect_sptw(x_values, y_values, z_values, sample_rate, start_datetime, nonwear=None, day_offset=12, ...)` | Sleep period time windows. Returns `(sptw, z_angle, z_angle_diff, z_sample_rate)`. |
| `detect_sleep_bouts(z_angle_diff, sptw, z_sample_rate, start_datetime, raw_epoch_length=5, z_abs_threshold=5, min_sleep_length=5)` | Sleep bouts within each window |
| `detect_sleep(...)` | Runs both steps. Returns `(sptw, sleep_bouts, z_angle, z_angle_diff, z_sample_rate)`. |
| `sptw_stats(sptw, sleep_bouts, type='daily', sptw_inc='long')` | Daily sleep summary. `sptw_inc` can be a list. |

## Utilities

| Function | Description |
|---|---|
| `nimbalwear.utils.autocal(x, y, z, accel_fs, temp=None, temp_fs=None, use_temp=True, epoch_secs=10, ...)` | Array-level auto-calibration. Returns calibrated `x, y, z` and calibration statistics. |
| `nimbalwear.utils.sync_devices(tgt_device, ref_device, ...)` | Function-level form of `Device.sync` |
| `nimbalwear.utils.read_excel_pwd(file_path, password, **kwargs)` | Reads a password-protected Excel file into a DataFrame |
| `nimbalwear.utils.convert_json_to_toml(json_path, toml_path)` | Converts old `settings.json` files |
| `nimbalwear.files.EDF.edf_header_summary(edf_path='', csv_path='', quiet=False)` | Summarizes the headers of EDF files in a folder, optionally writing a CSV |

The low-level file readers `GENEActivFile`, `CWAFile`, `EDFFile` and `SibelFile` (Sibel `.asc` tab-separated
files) are in `nimbalwear.files`. Each has a `read()` method.

## End-to-end example: one wrist file

```python
import pandas as pd
from nimbalwear import Device
from nimbalwear.nonwear import detach_nonwear
from nimbalwear.activity import activity_wrist_avm, activity_stats
from nimbalwear.sleep import detect_sleep, sptw_stats

dev = Device()
dev.import_geneactiv("wrist.bin")
dev.autocal()

ix, iy, iz = (dev.get_signal_index(f"Accelerometer {a}") for a in "xyz")
it = dev.get_signal_index("Temperature")
x, y, z, temp = dev.signals[ix], dev.signals[iy], dev.signals[iz], dev.signals[it]
fs = dev.signal_headers[ix]["sample_rate"]
temp_fs = dev.signal_headers[it]["sample_rate"]
start = dev.header["start_datetime"]

# non-wear (wrist thresholds from the default settings)
nw, _ = detach_nonwear(x_values=x, y_values=y, z_values=z, temperature_values=temp,
                       accel_freq=fs, temperature_freq=temp_fs, std_thresh_mg=8,
                       low_temperature_cutoff=26, high_temperature_cutoff=30,
                       temp_dec_roc=-0.2, temp_inc_roc=0.1, quiet=True)
nw["start_time"] = [start + pd.Timedelta(seconds=s / fs) for s in nw["Start Datapoint"]]
nw["end_time"] = [start + pd.Timedelta(seconds=e / fs) for e in nw["End Datapoint"]]

# sleep
sptw, sleep_bouts, *_ = detect_sleep(x, y, z, round(fs), start, nonwear=nw)
daily_sleep = sptw_stats(sptw, sleep_bouts, type="daily", sptw_inc="long")

# activity
epochs, bouts, *_ = activity_wrist_avm(x, y, z, fs, start, cutpoint="Powell", dominant=False,
                                       nonwear=nw, sptw=sptw, sleep_bouts=sleep_bouts)
daily_activity = activity_stats(bouts)
```

## Algorithms and references

| Module | Method | Reference |
|---|---|---|
| Auto-calibration | Iterative gravity-based calibration with temperature | van Hees et al. (2014), *J Appl Physiol* |
| Non-wear | DETACH (accelerometer and temperature) | `nimbaldetach` package (NiMBaL lab) |
| Activity | Average vector magnitude with cutpoints | Powell et al.; Fraysse et al. (2021), *Front Sports Act Living*, doi:10.3389/fspor.2020.579278 |
| Gait (gyro) | Adaptive-threshold peak detection | Fraccaro et al. (2014) |
| Gait (accel) | State-space step detection with a push-off template ([pushoff_df.csv](../src/nimbalwear/data/pushoff_df.csv)) | See [gait_accel.py](../src/nimbalwear/gait_accel.py) |
| Sleep | HDCZA (heuristic based on the distribution of change in z-angle) | van Hees et al. (2018), *Sci Rep* |
