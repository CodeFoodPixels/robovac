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
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform, CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from .const import CONF_VACS, DOMAIN

from .tuyalocaldiscovery import TuyaLocalDiscovery

PLATFORMS = [Platform.VACUUM, Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, entry) -> bool:
    hass.data.setdefault(DOMAIN, {CONF_VACS:{}})

    async def update_device(device):
        entry = async_get_config_entry_for_device(hass, device["gwId"])

        if entry == None:
            return

        if not entry.state.recoverable:
            return

        hass_data = entry.data.copy()
        if (
            device["gwId"] in hass_data[CONF_VACS]
            and device.get("ip") is not None
            and hass_data[CONF_VACS][device["gwId"]].get("autodiscovery", True)
        ):
            if hass_data[CONF_VACS][device["gwId"]][CONF_IP_ADDRESS] != device["ip"]:
                hass_data[CONF_VACS][device["gwId"]][CONF_IP_ADDRESS] = device["ip"]
                hass.config_entries.async_update_entry(entry, data=hass_data)
                await hass.config_entries.async_reload(entry.entry_id)
                _LOGGER.debug(
                    "Updated ip address of {} to {}".format(
                        device["gwId"], device["ip"]
                    )
                )

    tuyalocaldiscovery = TuyaLocalDiscovery(update_device)
    try:
        await tuyalocaldiscovery.start()
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, tuyalocaldiscovery.close)
    except Exception:
        _LOGGER.exception("failed to set up discovery")

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eufy Robovac from a config entry."""
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    ):
        """Nothing"""
    return unload_ok


async def update_listener(hass, entry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


def async_get_config_entry_for_device(hass, device_id):
    current_entries = hass.config_entries.async_entries(DOMAIN)
    for entry in current_entries:
        if device_id in entry.data[CONF_VACS]:
            return entry
    return None
