
# This program detects a signal from an FM radio station, demodulates it, filters it, and conducts Fourier analysis 
# to output a signal in a frequency range audible to the human ear.

from rtlsdr import RtlSdr
import numpy as np
from scipy.signal import decimate, butter, lfilter
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.io.wavfile import write

# Initialize the SDR device
sdr = RtlSdr()

# SDR Configuration
sdr.sample_rate = 2.4e6       # Sampling rate in Hz
#sdr.center_freq = 100.1e6    # Center frequency in Hz, change for each FM station 
#sdr.center_freq = 92.1e6     # The Beat
#sdr.center_freq = 93.7e6     # Hot 93.7
#sdr.center_freq = 96.5e6     # Mixed 96.5
sdr.center_freq = 98.9e6     # KissFM

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

# Fourier Analysis: Compute FFT of the filtered demodulated signal
def plot_fft(signal, fs):
    # Perform FFT
    N = len(signal)
    freqs = np.fft.fftfreq(N, d=1/fs)  # Frequency axis
    fft_signal = np.fft.fft(signal)  # Compute FFT
    fft_magnitude = np.abs(fft_signal)  # Magnitude spectrum

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(freqs[:N//2], fft_magnitude[:N//2])  # Only positive frequencies
    plt.title('FFT of Demodulated Signal')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.show()

# Plot FFT of the filtered demodulated signal to inspect the frequency content
plot_fft(filtered_demodulated, 2400000)

# Downsample the filtered signal to audio rate (~24kHz)
audio = decimate(filtered_demodulated, 100)  # Downsample by factor of 100

# Output Audio
sd.play(audio, samplerate=24000)
sd.wait()

# Save filtered audio
np.save('filtered_audio.npy', audio)
print("Audio playback complete. Saved as 'filtered_audio.npy'")

from scipy.io.wavfile import write

# Convert float audio to 16-bit PCM format
scaled_audio = np.int16(audio / np.max(np.abs(audio)) * 32767)

# Write to a WAV file
write('filtered_audio.wav', 24000, scaled_audio)
print("Saved as 'filtered_audio.wav'")

