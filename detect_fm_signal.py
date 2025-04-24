# This portion of the program only detects the IQ signals, saves the raw IQ data, then demodulates the singal.

from rtlsdr import RtlSdr
import numpy as np

# Initialize the SDR device
sdr = RtlSdr()

# SDR Configuration
sdr.sample_rate = 2.4e6       # Sampling rate in Hz
#sdr.center_freq = 100.1e6    # Center frequency in Hz, change for each FM station 
sdr.center_freq = 92.1e6      # The Beat
#sdr.center_freq = 93.7e6     # Hot 93.7
#sdr.center_freq = 96.5e6     # Mixed 96.5
#sdr.center_freq = 98.9e6     # KissFM

sdr.gain = 'auto'            # Use automatic gain control 

# Signal Acquisition 
print("Acquiring FM signal...")
samples = sdr.read_samples(256 * 1024)  # Capture 256K samples (~0.1s of data at 2.4 MHz)

# Close the SDR device
sdr.close()

# Save Raw IQ Data
np.save('raw_signal.npy', samples)
print("Signal acquisition complete. Saved as 'raw_signal.npy'")

# Visualize raw IQ signal in frequency domain (before demodulation)
def plot_raw_signal_fft(iq_data, fs):
    N = len(iq_data)
    freqs = np.fft.fftfreq(N, d=1/fs)
    fft_signal = np.fft.fft(iq_data)
    fft_magnitude = np.abs(fft_signal)

    plt.figure(figsize=(10, 6))
    plt.plot(freqs[:N//2], fft_magnitude[:N//2])  # Only positive frequencies
    plt.title('FFT of Raw IQ Signal')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.show()

# Call the function to visualize the raw IQ signal
plot_raw_signal_fft(samples, 2400000)

# FM Demodulation -- turn Raw IQ values into Audio
def fm_demodulate(iq_data):
    # Calculate the phase difference between consecutive IQ samples
    angle = np.angle(iq_data[1:] * np.conj(iq_data[:-1]))  # Phase difference
    return angle

demodulated = fm_demodulate(samples)

# Save demodulated signal
np.save('demodulated_signal.npy', demodulated)
print("Demodulation complete. Saved as 'demodulated_signal.npy'")


# Filtering, function to get to filtered_demodulated

# FFT, function get to audio

# Output audio, something like this:
# Downsample the filtered signal to audio rate (~24kHz)
#audio = decimate(filtered_demodulated, 100)  # Downsample by factor of 100

# Output Audio
#sd.play(audio, samplerate=24000)
#sd.wait()


