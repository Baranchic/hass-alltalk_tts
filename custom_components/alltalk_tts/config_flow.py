"""Config flow for alltalk_tts integration."""

from __future__ import annotations

from typing import Any

import logging
import aiohttp
import voluptuous as vol

from homeassistant.const import CONF_URL
from homeassistant.components.tts import CONF_LANG
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
import homeassistant.helpers.config_validation as cv
from urllib.parse import urlunparse, urlparse, urlencode

from .const import (
    CONF_VOICE,
    DOMAIN,
    LANGS,
    DEFAULT_LANG,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str #cv.string_with_no_html
    }
)

_LOGGER = logging.getLogger(__name__)

async def poke_url(url):
    # find the api url (the one that ends in /api, for example:
    # - http://localhost:1234 -> return http://localhost:1234/api
    # - http://localhost:1234/api -> return http://localhost:1234/api

    raw_url = url
    parts = urlparse(raw_url)
    path = parts.path
    if path.endswith("/"):
        path = ""
    api_url = urlunparse(
        (
            parts.scheme,
            parts.netloc,
            f"{path}/api",
            '',
            '',
            '',
        )
    )

    async def _try(try_url):
        async with aiohttp.ClientSession() as session:
            try:
                _LOGGER.info(f"testing URL: {try_url}")
                async with session.get(f"{try_url}/voices") as r:
                    j = await r.json()
                    voices = j['voices']

                    if r.status == 200:
                        return voices, None
                    else:
                        return [], {CONF_URL: f"Got status code {r.status}"}
            except Exception as e:
                return [], {CONF_URL: str(e)}

    voices, errs = await _try(raw_url)
    if voices:
        return raw_url, voices, errs

    voices2, errs2 = await _try(api_url)
    if voices2:
        return api_url, voices2, errs2

    # yes, return the *original* URL's errors
    return raw_url, [], errs


class AlltalkTTSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for alltalk_tts."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""

        errors = {}

        if user_input is not None:
            _LOGGER.info(user_input)
            new_url, voices, errors = await poke_url(user_input[CONF_URL])
            if voices:
                self._url = new_url
                self._voices = voices
                return await self.async_step_voice()

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)

    async def async_step_voice(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            _LOGGER.info(user_input)
            user_input[CONF_URL] = self._url
            self._async_abort_entries_match(user_input)
            return self.async_create_entry(
                title=f"alltalk_tts {user_input[CONF_VOICE]}-{user_input[CONF_LANG]}", data=user_input
            )

        schema = vol.Schema({
                vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(LANGS),
                vol.Required(CONF_VOICE): vol.In(self._voices)
        })

        return self.async_show_form(step_id="voice", data_schema=schema)






