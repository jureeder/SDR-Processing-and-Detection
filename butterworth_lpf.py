# This code is just the filtering portion. In this case a Butterworth filter is used as a placeholder, but can be replaced.

from scipy.signal import decimate, butter, lfilter

# Apply low-pass filter to remove noise from demodulated signal (e.g., use a cutoff of 15kHz)
def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order)
    y = lfilter(b, a, data)
    return y

# Low-pass filter demodulated signal (remove high-frequency noise)
filtered_demodulated = butter_lowpass_filter(demodulated, 15000, 2400000)  # 15 kHz cutoff, 2.4 MHz sample rate
