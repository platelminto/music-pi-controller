import os
import threading
import time

from dotenv import load_dotenv

from client.audio_output import process_audio
from client.controller import Controller
from client.lyrics import LyricsDisplayManager

DEBUG = True

load_dotenv()

pi_ip = os.getenv("PI_IP")
pi_port = int(os.getenv("PI_PORT"))


shutdown_flag = threading.Event()


if __name__ == '__main__':
    controller = Controller(pi_ip, pi_port, debug=DEBUG)

    audio_thread = threading.Thread(target=process_audio, args=(controller, shutdown_flag))
    audio_thread.start()

    lyrics_manager = LyricsDisplayManager(controller, shutdown_flag)
    # lyrics_manager.start()
    # lyrics_thread = threading.Thread(target=process_lyrics, args=(controller, shutdown_flag))
    # lyrics_thread.start()

    try:
        lyrics_manager.start()
        while True:
            time.sleep(0.5)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Stopping main process...")
        shutdown_flag.set()  # Signal the thread to shut down
        audio_thread.join()  # Wait for the thread to finish
        lyrics_manager.stop()

        controller.cleanup()
