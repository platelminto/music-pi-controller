# Controller for music thing

## To-do

- [x] Set up basic server on pi with high level API to control outputs from main computer
- [x] Start with ~~10~~ 7 LEDs for frequency bands
- [x] Set up main computer to send frequency data to pi
- [x] Set up debug mode to test LEDs on a webpage
- [ ] Add LED for beat from Spotify
- [ ] Add considering tempo/velocity/whatever from Spotify for persistance and stuff
- [ ] Show all LEDs when changing Spotify section? Or maybe when loudness big changes from segments? Investigate by graphing different things from known songs and see what feels right to visualise.
- [ ] Investigate if that beat/segment/etc. stuff could also be used to reset the average vals thing faster (since sometimes there are obvious beats we miss cos the average was higher, but some silence happened in the middle)
- [ ] What if we hook up the timbre stuff to the LEDs?
- [ ] Add screen to include lyrics
- [ ] Possibly also an indicator of how much time is left in the song
- [ ] Is input stuff useful from pi to Spotify?


## Installation

Most things are needed just for the debug server, rPI has few requirements. To get debug output working from speakers on (some) Linux, had to run:
- `sudo modprobe snd_aloop`

## Known issues

- main client thread doesn't close because lyrics thread doesn't close correctly
- text doesn't get cleared when new text is shown
- if text doesn't fit it simply gets cut off.