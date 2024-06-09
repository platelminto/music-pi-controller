import os
import threading
import time

from dotenv import load_dotenv
from syrics.api import Spotify

from client.controller import Controller

load_dotenv()

SPOTIFY_CHECK_INTERVAL = 5

sp = Spotify(os.getenv("SP_DC"))
#
# x = sp.get_current_song()
# print(x)
# lyr = sp.get_lyrics(x["item"]["id"])
# print(lyr)


# lyrics object is None if no lyrics available, or has a 'syncType' key: can be 'UNSYNCED', 'LINE_SYNCED'
class LyricsDisplayManager:
    def __init__(self, controller: Controller, shutdown_flag):
        self.last_song_id = None
        self.last_lyrics = None
        self.shutdown_flag = shutdown_flag
        self.update_flag = threading.Event()
        self.lyrics_thread = None
        self.controller = controller

    def check_spotify(self):
        """This thread checks for song changes/pauses and controls the lyrics display."""
        while not self.shutdown_flag.is_set():
            time.sleep(5)  # Check every 5 seconds
            current_song = sp.get_current_song()
            if not current_song['is_playing']:
                if self.lyrics_thread:
                    self.update_flag.set()  # Signal to stop the current lyrics thread
                    self.lyrics_thread.join()  # Ensure the thread has stopped
                    self.update_flag.clear()  # Reset the flag
                    continue

            current_song_id = current_song["item"]["id"]
            if current_song_id != self.last_song_id:
                self.last_song_id = current_song_id
                self.last_lyrics = sp.get_lyrics(current_song_id)

            if self.lyrics_thread:
                self.update_flag.set()  # Signal to stop the current lyrics thread
                self.lyrics_thread.join()  # Ensure the thread has stopped
                self.update_flag.clear()  # Reset the flag
            self.lyrics_thread = threading.Thread(target=self.display_lyrics, args=(current_song,))
            self.lyrics_thread.start()

    def display_lyrics(self, song):
        """This thread displays the lyrics synchronized with song progress."""
        current_progress = song["progress_ms"]
        if self.last_lyrics is None or self.last_lyrics["lyrics"]["syncType"] != "LINE_SYNCED":
            self.controller.show_text("♪")
            return

        lines = self.last_lyrics["lyrics"]['lines']
        i = 0
        while i < len(lines) and not self.update_flag.is_set():
            if self.update_flag.is_set():
                break  # Stop if there's an update
            line = lines[i]
            start_time = int(line["startTimeMs"])
            if start_time > current_progress:
                time_to_sleep = (start_time - current_progress) / 1000
                time.sleep(time_to_sleep)
                self.controller.show_text(line["words"])
                current_progress = start_time
            i += 1

    def start(self):
        print("CALLED?")
        """Start the main Spotify checking thread."""
        check_thread = threading.Thread(target=self.check_spotify)
        check_thread.start()

    def stop(self):
        """Stop all running threads."""
        self.shutdown_flag.set()
        if self.lyrics_thread:
            self.update_flag.set()


# def process_lyrics(controller: Controller, shutdown_flag):
#     try:
#         last_lyrics = {}
#         last_song_id = ""
#         while not shutdown_flag.is_set():
#             current_song = sp.get_current_song()
#
#             # If no song is playing, clear the display and continue (i.e. sleep again)
#             if not current_song['is_playing']:
#                 controller.clear_text()
#                 continue
#
#             # If the song has changed, get the new lyrics, and update the last_song_id
#             if current_song["item"]["id"] != last_song_id:
#                 last_song_id = current_song["item"]["id"]
#                 last_lyrics = sp.get_lyrics(last_song_id)
#
#             # Can't really do much if lyrics aren't synced, treat as if no lyrics
#             if last_lyrics is None or last_lyrics["lyrics"]["syncType"] == "UNSYNCED":
#                 controller.show_text("♪")
#                 continue
#
#             if last_lyrics["lyrics"]["syncType"] != "LINE_SYNCED":
#                 print("Unknown sync type")
#                 continue
#
#             current_progress = current_song["progress_ms"]
#             internal_time_start = time.time()
#             for line in last_lyrics["lyrics"]['lines']:
#                 if int(line["startTimeMs"]) > current_progress:
#                     controller.show_text(line["words"])
#                     if time.time() - internal_time_start > SPOTIFY_CHECK_INTERVAL:
#                         break
#                     time.sleep((int(line["startTimeMs"]) - current_progress) / 1000)
#
#     except KeyboardInterrupt:
#         pass
