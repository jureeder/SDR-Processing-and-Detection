# detect_fm_signal.py

from rtlsdr import RtlSdr
import numpy as np

# Initialize the SDR device
sdr = RtlSdr()

# SDR Configuration
sdr.sample_rate = 2.4e6      # Sampling rate in Hz
sdr.center_freq = 100.1e6    # Center frequency in Hz, change for each FM station 

sdr.center_freq = 92.1e6     # The Beat
sdr.center_freq = 93.7e6     # Hot 93.7
sdr.center_freq = 96.5e6     # Mixed 96.5
sdr.center_freq = 98.9e6     # KissFM

sdr.gain = 'auto'            # Use automatic gain control 

# Signal Acquisition 
print("Acquiring FM signal...")
samples = sdr.read_samples(256 * 1024)  # Capture 256K samples (~0.1s of data at 2.4 MHz)

# Close the SDR device
sdr.close()

# === Save Raw IQ Data ===
np.save('raw_signal.npy', samples)
print("Signal acquisition complete. Saved as 'raw_signal.npy'")
