import pyaudio
import numpy as np
import threading
import collections

# Define the maximum number of data points to display on the graph
MAX_POINTS = 50

# Initialize the queue to hold audio data, using a deque for efficient removal of old data
data_queue = collections.deque(maxlen=MAX_POINTS)

# Initialize PyAudio parameters
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 2048


def calculate_band_intensity(data, rate, band):
    fft_vals = np.fft.rfft(data)
    fft_freq = np.fft.rfftfreq(len(data), 1.0 / rate)
    if band == 'bass':
        low, high = 20, 250
    elif band == 'mid':
        low, high = 250, 4000
    elif band == 'treble':
        low, high = 4000, 20000
    band_indices = np.where((fft_freq >= low) & (fft_freq <= high))[0]
    intensity = np.sum(np.abs(fft_vals[band_indices]))
    return intensity


def process_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.float32)
            bass = calculate_band_intensity(audio_data, RATE, 'bass')
            mid = calculate_band_intensity(audio_data, RATE, 'mid')
            treble = calculate_band_intensity(audio_data, RATE, 'treble')
            data_queue.append((bass, mid, treble))
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == '__main__':
    audio_thread = threading.Thread(target=process_audio)
    audio_thread.start()
