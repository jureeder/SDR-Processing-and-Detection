# This portion of the code computes and plots the FFT 

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
