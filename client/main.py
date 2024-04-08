import time

import pyaudio
import numpy as np
import threading
import collections


# Initialize PyAudio parameters
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 2048

BANDS = {
    'sub_bass': (20, 60),
    'bass': (60, 250),
    'low_midrange': (250, 500),
    'midrange': (500, 2000),
    'upper_midrange': (2000, 4000),
    'presence': (4000, 6000),
    'brilliance': (6000, 20000),
}


def calculate_band_intensity(data, rate, band):
    fft_vals = np.fft.rfft(data)
    fft_freq = np.fft.rfftfreq(len(data), 1.0 / rate)

    low, high = BANDS[band]
    band_indices = np.where((fft_freq >= low) & (fft_freq <= high))[0]
    intensity = np.sum(np.abs(fft_vals[band_indices]))
    return intensity


def process_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Waiting 2 seconds for audio to settle...")
    time.sleep(2)
    try:
        vals = collections.defaultdict(list)
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.float32)
            for band in BANDS:
                intensity = calculate_band_intensity(audio_data, RATE, band)
                vals[band].append(intensity)
                print(f"{band}: {intensity:.2f}", end=" ")
            print()

    finally:
        for band, band_vals in vals.items():
            print(f"{band}: mean: {np.mean(band_vals):.2f}, max: {np.max(band_vals):.2f}, min: {np.min(band_vals):.3f}")
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == '__main__':
    audio_thread = threading.Thread(target=process_audio)
    audio_thread.start()
