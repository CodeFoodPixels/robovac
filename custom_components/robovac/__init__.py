# Copyright 2022 Brendan McCluskey
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""The Eufy Robovac integration."""
from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import HomeAssistant
from .const import CONF_VACS, DOMAIN

from .tuyalocaldiscovery import TuyaLocalDiscovery

PLATFORM = Platform.VACUUM
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, entry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    def update_device(device):
        current_entry = hass.config_entries.async_entries(DOMAIN)[0]
        hass_data = current_entry.data.copy()
        if device["gwId"] in hass_data[CONF_VACS]:
            if hass_data[CONF_VACS][device["gwId"]]["ip_address"] != device["ip"]:
                hass_data[CONF_VACS][device["gwId"]]["ip_address"] = device["ip"]
                hass.config_entries.async_update_entry(current_entry, data=hass_data)
                _LOGGER.debug("Updated ip address of {} to {}".format(device["gwId"], device["ip"]))

    tuyalocaldiscovery = TuyaLocalDiscovery(update_device)
    try:
        await tuyalocaldiscovery.start()
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, tuyalocaldiscovery.close)
    except Exception:  # pylint: disable=broad-except
        _LOGGER.exception("failed to set up discovery")

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eufy Robovac from a config entry."""

    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setup(entry, PLATFORM)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_forward_entry_unload(
        entry, PLATFORM
    ):
        """Nothing"""
    return unload_ok


async def update_listener(hass, entry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
