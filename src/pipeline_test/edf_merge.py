from edfio import read_edf, EdfSignal, Edf
import numpy as np
import os
from tqdm import tqdm


def combine_sensor_files(file_list: list,
                         return_raw: bool = False,
                         export_file: bool = False,
                         output_filename: str or None = None):
    """ Merges sensor-specific files (e.g., accelerometer-only, gyroscope-only) that were split using the nimbalwear
        pipeline back into a 'raw' multi-sensor EDF file

        Parameters:
            file_list: list
                list of files that were generated from a single input file
            return_raw: bool
                if True, returns edfio.EdfSignal object of each file listed in file_list
            export_file: bool
                if True, saves merged EDF file to pathway specified by output_filename
            output_filename: str
                pathway and filename of file to save if export_file is True
    """

    # TODO: sort out things related to EDF "records"?

    print(f"\nCombining {len(file_list)} files...")

    objs = []
    for file in file_list:
        print(f"    -{file}")
        objs.append(read_edf(file))

    # combines signals across objs into single EDF
    d = []

    for idx in tqdm(range(len(objs))):

        for sig in range(len(objs[idx].signals)):

            d.append(EdfSignal(data=objs[idx].signals[sig].data,
                               sampling_frequency=objs[idx].signals[sig].sampling_frequency,
                               label=objs[idx].signals[sig].label))

    # ensures signals are all the same duration by zero-padding all signals to match the length of the longest signal
    durs = [len(d[i].data)/d[i].sampling_frequency for i in range(len(d))]
    target_dur = max(durs)

    for i in range(len(d)):
        s = len(d[i].data)/d[i].sampling_frequency

        if s < target_dur:

            n = int((target_dur - s) * d[i].sampling_frequency)
            x = np.concatenate([d[i].data, np.array([0]*n)])

            d[i] = EdfSignal(data=x,
                             sampling_frequency=objs[idx].signals[sig].sampling_frequency,
                             label=objs[idx].signals[sig].label)

    obj_out = Edf(d)

    # sets physical_dimension labels (i.e., measurement unit) from raw signals
    use_idx = 0
    for idx in range(len(objs)):
        for sig in range(len(objs[idx].signals)):
            obj_out.signals[use_idx].physical_dimension = objs[idx].signals[sig].physical_dimension
            use_idx += 1

    # sets start date + time from first item in objs
    # (startdatetime gets automatically updated)
    obj_out.startdate = objs[0].startdate
    obj_out.starttime = objs[0].starttime

    if export_file and output_filename is not None:
        obj_out.write(output_filename)
        print(f"-Combined file saved to '{output_filename}'")

    return obj_out, (objs if return_raw else None)


if __name__ == "__main__":

    os.chdir(r"C:\Users\kweber\Desktop\OND09\sensor_files")
    output_dir = r"C:/Users/kweber/Desktop/OND09/test_project/test_file_recombination"

    files = {"RAnkle": {"files": ["OND09_SBH_0001_01_AXV6_ACCELEROMETER_RAnkle.edf",
                                  "OND09_SBH_0001_01_AXV6_GYROSCOPE_RAnkle.edf",
                                  "OND09_SBH_0001_01_AXV6_LIGHT_RAnkle.edf",
                                  "OND09_SBH_0001_01_AXV6_TEMPERATURE_RAnkle.edf"],
                        "device": "AXV6",
                        "wear_loc": "RAnkle"},
             "RWrist": {"files": ['OND09_SBH_0001_01_AXV6_ACCELEROMETER_RWrist.edf',
                                  'OND09_SBH_0001_01_AXV6_GYROSCOPE_RWrist.edf',
                                  'OND09_SBH_0001_01_AXV6_LIGHT_RWrist.edf',
                                  'OND09_SBH_0001_01_AXV6_TEMPERATURE_RWrist.edf'],
                        "device": "AXV6",
                        "wear_loc": "RWrist"},
             "Chest": {"files": ['OND09_SBH_0001_01_BF36_ACCELEROMETER_Chest.edf',
                                 'OND09_SBH_0001_01_BF36_ECG_Chest.edf',
                                 'OND09_SBH_0001_01_BF36_TEMPERATURE_Chest.edf'],
                       "device": "BF36",
                       "wear_loc": "Chest"}}

    for f in files.keys():

        file_out = f"OND09_SBH0001_01_{files[f]['device']}_{files[f]['wear_loc']}.edf"

        edf_comb, edf_raw = combine_sensor_files(file_list=files[f]['files'],
                                                 export_file=True,
                                                 output_filename=os.path.join(output_dir, file_out),
                                                 return_raw=False)

    # import combined file
    # x = read_edf(os.path.join(output_dir, "OND09_SBH0001_01_AXV6_RAnkle.edf"))
