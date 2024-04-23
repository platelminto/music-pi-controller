import os
import time

import pyaudio
import numpy as np
import threading
import collections

from dotenv import load_dotenv

from client.commands import Controller, MAIN_LEDS

DEBUG = True

load_dotenv()

pi_ip = os.getenv("PI_IP")
pi_port = int(os.getenv("PI_PORT"))

FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# In CHUNK/RATE samples. (Currently around 10Hz)
PERSIST_TIME = 6
AVERAGE_SAMPLES_KEEP = 80

FREQ_MEAN_THRESHOLD = 1.66

BANDS = {
    'sub_bass': (20, 40),
    'bass': (40, 80),
    'high_bass': (80, 200),
    'low_midrange': (200, 650),
    'midrange': (650, 1500),
    'upper_midrange': (1500, 3500),
    'brilliance': (3500, 15000),
}

LED_BANDS = dict(zip(BANDS.keys(), MAIN_LEDS))


def calculate_band_intensity(data, rate, band):
    fft_vals = np.fft.rfft(data)
    fft_freq = np.fft.rfftfreq(len(data), 1.0 / rate)

    low, high = BANDS[band]
    bandwidth = high - low
    band_indices = np.where((fft_freq >= low) & (fft_freq <= high))[0]
    intensity = np.sum(np.abs(fft_vals[band_indices])) / bandwidth  # Normalization
    return intensity


shutdown_flag = threading.Event()


def handle_intensity(controller, intensity, led_id, recent_vals, persist_counter):
    reset = False

    recent_mean = np.mean(recent_vals)
    if intensity > recent_mean * FREQ_MEAN_THRESHOLD:
        controller.turn_led_on(led_id, power_percentage=100)
        reset = True
    elif persist_counter >= PERSIST_TIME:
        controller.turn_led_off(led_id)

    return reset


def find_loopback_device(p):
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    possible_devices = []
    for i in range(num_devices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            name = p.get_device_info_by_host_api_device_index(0, i).get('name')
            if 'loopback' in name.lower() or 'stereo mix' in name.lower():
                possible_devices.append(i)

    if possible_devices:
        return possible_devices[-1]

    return None


def process_audio():
    controller = Controller(pi_ip, pi_port, debug=DEBUG)
    p = pyaudio.PyAudio()

    device_index = find_loopback_device(p)
    if device_index is None:
        print("No loopback device found. Check your sound settings. (Not always an issue)")
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    else:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=device_index,
                        frames_per_buffer=CHUNK)
        print("Recording from speakers...")
    print("Waiting 2 seconds for audio to settle...")
    time.sleep(2)
    try:
        vals = collections.defaultdict(list)
        recent_vals = collections.defaultdict(lambda: collections.deque(maxlen=AVERAGE_SAMPLES_KEEP))
        persist_counters = {band: 0 for band in BANDS.keys()}
        while not shutdown_flag.is_set():
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.float32)
            for band in BANDS:
                intensity = calculate_band_intensity(audio_data, RATE, band) * 100
                recent_vals[band].append(intensity)
                reset = handle_intensity(controller, intensity, LED_BANDS[band],
                                 recent_vals[band], persist_counters[band])
                persist_counters[band] += 1
                if reset:
                    persist_counters[band] = 0

                vals[band].append(intensity)
                print(f"{band}: {intensity:.4f}", end=" ")
            print()
    except KeyboardInterrupt:
        pass
    finally:
        for band, band_vals in vals.items():
            print(f"{band}: mean: {np.mean(band_vals):.2f}, max: {np.max(band_vals):.2f}, min: {np.min(band_vals):.3f}")
        stream.stop_stream()
        stream.close()
        p.terminate()

        for led in MAIN_LEDS:
            controller.turn_led_off(led)

        controller.close()


if __name__ == '__main__':
    audio_thread = threading.Thread(target=process_audio)
    audio_thread.start()

    try:
        while True:
            time.sleep(0.1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Stopping audio processing...")
        shutdown_flag.set()  # Signal the thread to shut down
        audio_thread.join()  # Wait for the thread to finish
