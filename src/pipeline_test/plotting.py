import edfio
import matplotlib.pyplot as plt
import numpy as np


def plot_signals(edf_obj: edfio.Edf,
                 signals: list,
                 ds_ratio: int = 1):

    fig, ax = plt.subplots(ncols=1, nrows=len(signals), sharex='col')

    if len(signals) > 1:
        for idx, sigs in enumerate(signals):
            for sig in sigs:
                d = edf_obj.get_signal(label=sig)
                t = np.arange(0, d.data.shape[0]) / d.sampling_frequency / 86400

                ax[idx].plot(t[::ds_ratio], d.data[::ds_ratio], label=sig)

            ax[idx].set_ylabel(d.physical_dimension)
            ax[idx].legend(loc='upper right')

        ax[-1].set_xlabel("Time (days)")

    else:
        for sig in signals[0]:
            d = edf_obj.get_signal(label=sig)
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