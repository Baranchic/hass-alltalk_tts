# alltalk_tts Home Assistant Plugin

This is a Home Assistant plugin to allow [alltalk_tts](https://github.com/erew123/alltalk_tts) to be used as a text-to-speech provider in Home Assistant. You are responsible for setting that up. Note the URL for accessing the alltalk_tts API for Installation.

## Installation

Install this plugin with [HACS](https://hacs.xyz/docs/use/).

1. Inside of HACS, click the three dots -> Custom Repositories -> Add 'richardsamuels/hass-alltalk_tts' Type Integration -> Click Add.
2. Restart Home Assistant, Click Settings -> Devices & Services -> Add Integration -> Search for and click on alltalk_tts.
3. In the first window, enter to URL to the alltalk_tts API, such has `http://localhost:7815/api`.
4. In the second window, confirm the voice and language. Click Add
5. Open Settings -> Voice Assistants -> Select your pipeline -> Scroll to "Text to Speech" -> Select `alltalk ...` -> Click Try Voice.
6. If you heard a test voice, Click update and you're done. If not, check the logs and fix the problems.
