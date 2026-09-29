import edfio
import matplotlib.pyplot as plt
import numpy as np


def plot_signals(edf_obj: edfio.Edf,
                 signals: list,
                 ds_ratio: int = 1):
    """ Given a nested list of signal channel names, generates a series of subplots that contain data from each
        nested list.

        Parameters:
            edf_obj: edfio.Edf instance
                EDF file imported by edfio.read_edf()
            signals: list (nested)
                nested list of signals that match labels contained within edf_obj. Labels in the same list will be
                plotted on the same subplot
                    e.g., [['Accelerometer x', 'Accelerometer y', 'Accelerometer z'], ['Temperature']] will generate
                        2 subplots with 3 accelerometer signals on the first subplot and temperature on the second
            ds_ratio: int
                "downsample ratio" - plots every nth datapoint
    """

    fig, ax = plt.subplots(ncols=1, nrows=len(signals), sharex='col')

    # if multiple subplots to be generated
    if len(signals) > 1:
        for idx, sigs in enumerate(signals):
            for sig in sigs:

                # signal data
                d = edf_obj.get_signal(label=sig)

                # timestamps in days since start of collection
                t = np.arange(0, d.data.shape[0]) / d.sampling_frequency / 86400

                ax[idx].plot(t[::ds_ratio], d.data[::ds_ratio], label=sig)

            ax[idx].set_ylabel(d.physical_dimension)  # measurement unit
            ax[idx].legend(loc='upper right')

        ax[-1].set_xlabel("Time (days)")

    else:
        for sig in signals[0]:

            # signal data
            d = edf_obj.get_signal(label=sig)

            # time in days since start of collection
            t = np.arange(0, d.data.shape[0]) / d.sampling_frequency / 86400

            ax.plot(t[::ds_ratio], d.data[::ds_ratio], label=sig)

        ax.set_ylabel(d.physical_dimension)
        ax.legend(loc='upper right')

        ax.set_xlabel("Time (days)")

    plt.tight_layout()
    plt.show(block=True)


"""
plot_signals(edf_obj=x,
             signals=[['Accelerometer x', 'Accelerometer y', 'Accelerometer z'],
                      ['Gyroscope x', 'Gyroscope y', 'Gyroscope z'],
                      ['Temperature'],
                      ['Light']],
             ds_ratio=5)
"""