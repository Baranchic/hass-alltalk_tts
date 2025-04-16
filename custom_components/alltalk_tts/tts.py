"""Support for the alltalk_tts speech service."""

from __future__ import annotations

from io import BytesIO
import logging
from typing import Any
import requests

import voluptuous as vol

from homeassistant.const import CONF_LANGUAGE, CONF_URL
from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA as TTS_PLATFORM_SCHEMA,
    Provider,
    TextToSpeechEntity,
    TtsAudioType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from urllib.parse import urlunparse, urlparse, urlencode
from .const import (
    CONF_VOICE,
    DEFAULT_LANG,
    LANGS
)

_LOGGER = logging.getLogger(__name__)

SUPPORT_OPTIONS = [CONF_VOICE, "lang"]

PLATFORM_SCHEMA = TTS_PLATFORM_SCHEMA


async def async_get_engine(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> AlltalkTTSProvider:
    """Set up alltalk_tts speech component."""
    return AlltalkProvider(hass, config[CONF_LANG], config[CONF_URL], config[CONF_VOICE])


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up alltalk_tts speech platform via config entry."""
    async_add_entities([AlltalkTTSEntity(config_entry)])


class AlltalkTTSEntity(TextToSpeechEntity):
    """The alltalk_tts API entity."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Init alltalk_tts service."""

        lang = config_entry.data[CONF_LANG]
        voice = config_entry.data[CONF_VOICE]
        self._url = config_entry.data[CONF_URL]
        self._lang = lang
        self._voice = voice
        self._attr_name = f"alltalk_tts {self._lang} {self._voice}"
        self._attr_unique_id = config_entry.entry_id

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return self._lang

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return LANGS

    @property
    def supported_options(self) -> list[str]:
        """Return a list of supported options."""
        return SUPPORT_OPTIONS

    def get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
        """Load TTS."""
        if language is None:
            language = self._lang
        voice = self._voice
        if CONF_VOICE in options:
            voice = options[CONF_VOICE]
        if "lang" in options:
            language = options["lang"]
        if language == 'sk':
            language = 'cs'                

        _LOGGER.info(f"Request TTS LANG: {language} | VOICE: {voice} | OPTS: {options} | msg: {message}")
        return get_voice(self._url, self._lang, self._voice, message);


class AlltalkTTSProvider(Provider):
    """The alltalk_tts provider."""

    def __init__(self, hass: HomeAssistant, lang: str, url: str, voice: str) -> None:
        """Init alltalk_tts service."""
        self.hass = hass
        self._lang = lang
        self._url = url
        self._voice = voice
        self.name = f"alltalk_tts {self._lang} {self._voice}"

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return DEFAULT_LANG

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return LANGS

    @property
    def supported_options(self) -> list[str]:
        """Return a list of supported options."""
        return SUPPORT_OPTIONS

    def get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Load TTS."""
        if language is None:
            language = self._lang
        voice = self._voice
        if CONF_VOICE in options:
            voice = options[CONF_VOICE]
        if "lang" in options:
            language = options["lang"]
        if language == 'sk':
            language = 'cs'    

        _LOGGER.info(f"Request TTS LANG: {language} | VOICE: {voice} | OPTS: {options} | msg: {message}")
        return get_voice(self._url, language, voice, message);

def get_voice(url, lang, voice, msg):
    data = {
        "text": msg,
        "language": lang,
        "voice": voice,
        "output_file": "tts_hass"
    }
    api_parts = urlparse(url)
    whole_path = (
        api_parts.scheme,
        api_parts.netloc,
        f"{api_parts.path}/tts-generate-streaming",
        '',
        urlencode(data),
        '',
    )
    try:
        headers = {'Content-type': "application/x-www-form-urlencoded"}
        r = requests.get(urlunparse(whole_path), headers=headers)
        if r.status_code != 200:
            _LOGGER.exception(f"Request POST {urlunparse(whole_path)} to generate TTS failed with code {r.status_code}")
            return None, None
        wav_data = BytesIO(r.content)
        return "wav", wav_data.getvalue()

    except Exception as e:
        _LOGGER.exception(f"Error during processing of TTS request: {e}")
        return None, None

