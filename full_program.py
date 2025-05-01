# This program detects a signal from an FM radio station, demodulates it, filters it, and conducts Fourier analysis 
# to output both a filtered and unfiltered signal in a frequency range audible to the human ear.

from rtlsdr import RtlSdr
import numpy as np
from scipy.signal import decimate, butter, lfilter
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
from scipy.signal import firwin, lfilter

# Initialize the SDR device
sdr = RtlSdr()

# SDR Configuration
sdr.sample_rate = 2.4e6       # Sampling rate 2.4 MHz
#sdr.center_freq = 100e6      # Center frequency in Hz, change for each FM station 
#sdr.center_freq = 92.1e6     # The Beat
#sdr.center_freq = 93.7e6     # Hot 93.7
#sdr.center_freq = 96.5e6     # Mixed 96.5
sdr.center_freq = 98.9e6      # KissFM

sdr.gain = 'auto'             # Use automatic gain control 

# Signal Acquisition 
print("Acquiring FM signal...")
samples = sdr.read_samples(256 * 1024)  # Capture 256K samples (~0.1s of data at 2.4 MHz)

# Close the SDR device
sdr.close()

# Save Raw IQ Data
np.save('raw_signal.npy', samples)
print("Signal acquisition complete. Saved as 'raw_signal.npy'")

# Plot raw IQ signal in frequency domain (before demodulation)
def plot_raw_signal_fft(iq_data, fs):
    N = len(iq_data)
    freqs = np.fft.fftfreq(N, d=1/fs)
    fft_signal = np.fft.fft(iq_data)
    fft_magnitude = np.abs(fft_signal)

    plt.figure(figsize=(10, 6))
    plt.plot(freqs[:N//2], fft_magnitude[:N//2])  # Only positive frequencies
    plt.title('Frequency Domain Plot of Raw IQ Signal')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.show()

# Fourier Analysis: Compute and plot FFT of the unfiltered demodulated signal
def plot_unfiltered_fft(signal, fs):
    N = len(signal)
    freqs = np.fft.fftfreq(N, d=1/fs)  # Frequency axis
    fft_signal = np.fft.fft(signal)  # Compute FFT
    fft_magnitude = np.abs(fft_signal)  # Magnitude spectrum

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(freqs[:N//2], fft_magnitude[:N//2])  # Only positive frequencies
    plt.title('FFT of Unfiltered Demodulated Signal')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.show()

# Call the functions to visualize the raw IQ signal
plot_raw_signal_fft(samples, 2400000)

# FM Demodulation -- turn Raw IQ values into Audio
def fm_demodulate(iq_data):
    # Calculate the phase difference between consecutive IQ samples
    angle = np.angle(iq_data[1:] * np.conj(iq_data[:-1]))  # Phase difference
    return angle

demodulated = fm_demodulate(samples)

# Plot FFT of the unfiltered demodulated signal to inspect the frequency content
plot_unfiltered_fft(demodulated,  2400000)

# Downsample the unfiltered signal to audio rate (~24kHz)
demod_audio = decimate(demodulated, 100)  # Downsample by factor of 100

# Output Unfiltered Audio
sd.play(demod_audio, samplerate=24000)
sd.wait()

# Save unfiltered audio
np.save('unfiltered_audio.npy', demod_audio)
print("Unfiltered audio playback complete. Saved as 'unfiltered_audio.npy'")

# Convert float demod_audio to 16-bit PCM format
scaled_demod_audio = np.int16(demod_audio / np.max(np.abs(demod_audio)) * 32767)

# Write to a WAV file
write('unfiltered_audio.wav', 24000, scaled_demod_audio)
print("Saved as 'unfiltered_audio.wav'")


# Apply low-pass Hanning filter to remove noise from demodulated signal 
def hann_lowpass_filter(data, cutoff, fs, order=5):
    normalized_cutoff = cutoff / (fs * 0.5)
    fir_coeff = firwin(101, normalized_cutoff,window='hann')
    filtered = lfilter(fir_coeff, 1.0, data)
    return filtered

# Low-pass filter demodulated signal (remove high-frequency noise)
filtered_demodulated = hann_lowpass_filter(demodulated, 15000, 2400000)  # 15 kHz cutoff, 2.4 MHz sample rate

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

# Output Filtered Audio
sd.play(audio, samplerate=24000)
sd.wait()

# Save filtered audio
np.save('filtered_audio.npy', audio)
print("Filtered audio playback complete. Saved as 'filtered_audio.npy'")

# Convert float audio to 16-bit PCM format
scaled_audio = np.int16(audio / np.max(np.abs(audio)) * 32767)

# Write to a WAV file
write('filtered_audio.wav', 24000, scaled_audio)
print("Saved as 'filtered_audio.wav'")
