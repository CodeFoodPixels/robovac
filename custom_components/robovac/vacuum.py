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

"""Eufy Robovac sensor platform."""
from __future__ import annotations
from collections.abc import Mapping

from datetime import timedelta
import logging
import asyncio
import base64
import json
import time
import ast

from typing import Any
from enum import IntEnum, StrEnum
from homeassistant.loader import bind_hass
from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumEntityFeature,
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_RETURNING,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
)
from homeassistant.helpers.entity import DeviceInfo

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_MODEL,
    CONF_NAME,
    CONF_ID,
    CONF_IP_ADDRESS,
    CONF_DESCRIPTION,
    CONF_MAC,
    STATE_UNAVAILABLE,
)

from .tuyalocalapi import TuyaException
from .const import CONF_VACS, DOMAIN, REFRESH_RATE

from .errors import getErrorMessage
from .robovac import (
    SUPPORTED_ROBOVAC_MODELS,
    ModelNotSupportedException,
    RoboVac,
    RoboVacEntityFeature,
)

from homeassistant.const import ATTR_BATTERY_LEVEL

ATTR_BATTERY_ICON = "battery_icon"
ATTR_ERROR = "error"
ATTR_FAN_SPEED = "fan_speed"
ATTR_FAN_SPEED_LIST = "fan_speed_list"
ATTR_STATUS = "status"
ATTR_ERROR_CODE = "error_code"
ATTR_MODEL_CODE = "model_code"
ATTR_CLEANING_AREA = "cleaning_area"
ATTR_CLEANING_TIME = "cleaning_time"
ATTR_AUTO_RETURN = "auto_return"
ATTR_DO_NOT_DISTURB = "do_not_disturb"
ATTR_BOOST_IQ = "boost_iq"
ATTR_CONSUMABLES = "consumables"
ATTR_MODE = "mode"

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=REFRESH_RATE)
UPDATE_RETRIES = 3


class TUYA_CODES(StrEnum):
    BATTERY_LEVEL = "104"
    STATE = "15"
    ERROR_CODE = "106"
    MODE = "5"
    FAN_SPEED = "102"
    CLEANING_AREA = "110"
    CLEANING_TIME = "109"
    AUTO_RETURN = "135"
    DO_NOT_DISTURB = "107"
    BOOST_IQ = "118"


TUYA_CONSUMABLES_CODES = ["142", "116"]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize my test integration 2 config entry."""
    vacuums = config_entry.data[CONF_VACS]
    for item in vacuums:
        item = vacuums[item]
        entity = RoboVacEntity(item)
        hass.data[DOMAIN][CONF_VACS][item[CONF_ID]] = entity
        async_add_entities([entity])


class RoboVacEntity(StateVacuumEntity):
    """Eufy Robovac version of a Vacuum entity"""

    _attr_should_poll = True

    _attr_access_token: str | None = None
    _attr_ip_address: str | None = None
    _attr_model_code: str | None = None
    _attr_cleaning_area: str | None = None
    _attr_cleaning_time: str | None = None
    _attr_auto_return: str | None = None
    _attr_do_not_disturb: str | None = None
    _attr_boost_iq: str | None = None
    _attr_consumables: str | None = None
    _attr_mode: str | None = None
    _attr_robovac_supported: str | None = None

    @property
    def robovac_supported(self) -> str | None:
        """Return the supported features of the vacuum cleaner."""
        return self._attr_robovac_supported

    @property
    def mode(self) -> str | None:
        """Return the cleaning mode of the vacuum cleaner."""
        return self._attr_mode

    @property
    def consumables(self) -> str | None:
        """Return the consumables status of the vacuum cleaner."""
        return self._attr_consumables

    @property
    def cleaning_area(self) -> str | None:
        """Return the cleaning area of the vacuum cleaner."""
        return self._attr_cleaning_area

    @property
    def cleaning_time(self) -> str | None:
        """Return the cleaning time of the vacuum cleaner."""
        return self._attr_cleaning_time

    @property
    def auto_return(self) -> str | None:
        """Return the auto_return mode of the vacuum cleaner."""
        return self._attr_auto_return

    @property
    def do_not_disturb(self) -> str | None:
        """Return the do not disturb mode of the vacuum cleaner."""
        return self._attr_do_not_disturb

    @property
    def boost_iq(self) -> str | None:
        """Return the boost iq mode of the vacuum cleaner."""
        return self._attr_boost_iq

    @property
    def model_code(self) -> str | None:
        """Return the model code of the vacuum cleaner."""
        return self._attr_model_code

    @property
    def access_token(self) -> str | None:
        """Return the fan speed of the vacuum cleaner."""
        return self._attr_access_token

    @property
    def ip_address(self) -> str | None:
        """Return the ip address of the vacuum cleaner."""
        return self._attr_ip_address

    @property
    def state(self) -> str | None:
        if self.tuya_state is None:
            return STATE_UNAVAILABLE
        elif (
            type(self.error_code) is not None
            and self.error_code
            and self.error_code
            not in [
                0,
                "no_error",
            ]
        ):
            _LOGGER.debug(
                "State changed to error. Error message: {}".format(
                    getErrorMessage(self.error_code)
                )
            )
            return STATE_ERROR
        elif self.tuya_state == "Charging" or self.tuya_state == "completed":
            return STATE_DOCKED
        elif self.tuya_state == "Recharge":
            return STATE_RETURNING
        elif self.tuya_state == "Sleeping" or self.tuya_state == "standby":
            return STATE_IDLE
        else:
            return STATE_CLEANING

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the device-specific state attributes of this vacuum."""
        data: dict[str, Any] = {}

        if type(self.error_code) is not None and self.error_code not in [0, "no_error"]:
            data[ATTR_ERROR] = getErrorMessage(self.error_code)
        if (
            self.robovac_supported & RoboVacEntityFeature.CLEANING_AREA
            and self.cleaning_area
        ):
            data[ATTR_CLEANING_AREA] = self.cleaning_area
        if (
            self.robovac_supported & RoboVacEntityFeature.CLEANING_TIME
            and self.cleaning_time
        ):
            data[ATTR_CLEANING_TIME] = self.cleaning_time
        if (
            self.robovac_supported & RoboVacEntityFeature.AUTO_RETURN
            and self.auto_return
        ):
            data[ATTR_AUTO_RETURN] = self.auto_return
        if (
            self.robovac_supported & RoboVacEntityFeature.DO_NOT_DISTURB
            and self.do_not_disturb
        ):
            data[ATTR_DO_NOT_DISTURB] = self.do_not_disturb
        if self.robovac_supported & RoboVacEntityFeature.BOOST_IQ and self.boost_iq:
            data[ATTR_BOOST_IQ] = self.boost_iq
        if (
            self.robovac_supported & RoboVacEntityFeature.CONSUMABLES
            and self.consumables
        ):
            data[ATTR_CONSUMABLES] = self.consumables
        if self.mode:
            data[ATTR_MODE] = self.mode
        return data

    def __init__(self, item) -> None:
        """Initialize Eufy Robovac"""
        super().__init__()
        self._attr_battery_level = 0
        self._attr_name = item[CONF_NAME]
        self._attr_unique_id = item[CONF_ID]
        self._attr_model_code = item[CONF_MODEL]
        self._attr_ip_address = item[CONF_IP_ADDRESS]
        self._attr_access_token = item[CONF_ACCESS_TOKEN]

        self.update_failures = 0

        try:
            self.vacuum = RoboVac(
                device_id=self.unique_id,
                host=self.ip_address,
                local_key=self.access_token,
                timeout=2,
                ping_interval=REFRESH_RATE / 2,
                model_code=self.model_code[0:5],
                update_entity_state=self.pushed_update_handler,
            )
        except ModelNotSupportedException:
            self.error_code = "UNSUPPORTED_MODEL"

        self._attr_supported_features = self.vacuum.getHomeAssistantFeatures()
        self._attr_robovac_supported = self.vacuum.getRoboVacFeatures()
        self._attr_fan_speed_list = self.vacuum.getFanSpeeds()

        self._attr_mode = None
        self._attr_consumables = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, item[CONF_ID])},
            name=item[CONF_NAME],
            manufacturer="Eufy",
            model=item[CONF_DESCRIPTION],
            connections=[
                (CONNECTION_NETWORK_MAC, item[CONF_MAC]),
            ],
        )

        self.error_code = None
        self.tuya_state = None
        self.tuyastatus = None

    async def async_update(self):
        """Synchronise state from the vacuum."""
        if self.error_code == "UNSUPPORTED_MODEL":
            return

        if self.ip_address == "":
            self.error_code = "IP_ADDRESS"
            return

        try:
            await self.vacuum.async_get()
            self.update_failures = 0
            self.update_entity_values()
        except TuyaException as e:
            self.update_failures += 1
            _LOGGER.debug(
                "Update errored. Current failure count: {}. Reason: {}".format(
                    self.update_failures, e
                )
            )
            if self.update_failures == UPDATE_RETRIES:
                self.update_failures = 0
                self.error_code = "CONNECTION_FAILED"
                raise e

    async def pushed_update_handler(self):
        self.update_entity_values()
        self.async_write_ha_state()

    def update_entity_values(self):
        self.tuyastatus = self.vacuum._dps

        # for 15C
        self._attr_battery_level = self.tuyastatus.get(TUYA_CODES.BATTERY_LEVEL)
        self.tuya_state = self.tuyastatus.get(TUYA_CODES.STATE)
        self.error_code = self.tuyastatus.get(TUYA_CODES.ERROR_CODE)
        self._attr_mode = self.tuyastatus.get(TUYA_CODES.MODE)
        self._attr_fan_speed = self.tuyastatus.get(TUYA_CODES.FAN_SPEED)
        if self.fan_speed == "No_suction":
            self._attr_fan_speed = "No Suction"
        elif self.fan_speed == "Boost_IQ":
            self._attr_fan_speed = "Boost IQ"
        elif self.fan_speed == "Quiet":
            self._attr_fan_speed = "Pure"
        # for G30
        self._attr_cleaning_area = self.tuyastatus.get(TUYA_CODES.CLEANING_AREA)
        self._attr_cleaning_time = self.tuyastatus.get(TUYA_CODES.CLEANING_TIME)
        self._attr_auto_return = self.tuyastatus.get(TUYA_CODES.AUTO_RETURN)
        self._attr_do_not_disturb = self.tuyastatus.get(TUYA_CODES.DO_NOT_DISTURB)
        self._attr_boost_iq = self.tuyastatus.get(TUYA_CODES.BOOST_IQ)
        # self.map_data = self.tuyastatus.get("121")
        # self.erro_msg? = self.tuyastatus.get("124")
        if self.robovac_supported & RoboVacEntityFeature.CONSUMABLES:
            for CONSUMABLE_CODE in TUYA_CONSUMABLES_CODES:
                if (
                    CONSUMABLE_CODE in self.tuyastatus
                    and self.tuyastatus.get(CONSUMABLE_CODE) is not None
                ):
                    consumables = ast.literal_eval(
                        base64.b64decode(self.tuyastatus.get(CONSUMABLE_CODE)).decode(
                            "ascii"
                        )
                    )
                    if "consumable" in consumables and "duration" in consumables:
                        self._attr_consumables = consumables["consumable"]["duration"]

    async def async_locate(self, **kwargs):
        """Locate the vacuum cleaner."""
        _LOGGER.info("Locate Pressed")
        if self.tuyastatus.get("103"):
            await self.vacuum.async_set({"103": False})
        else:
            await self.vacuum.async_set({"103": True})

    async def async_return_to_base(self, **kwargs):
        """Set the vacuum cleaner to return to the dock."""
        _LOGGER.info("Return home Pressed")
        await self.vacuum.async_set({"101": True})

    async def async_start(self, **kwargs):
        self._attr_mode = "auto"
        await self.vacuum.async_set({"5": self.mode})

    async def async_pause(self, **kwargs):
        await self.vacuum.async_set({"2": False})

    async def async_stop(self, **kwargs):
        await self.async_return_to_base()

    async def async_clean_spot(self, **kwargs):
        """Perform a spot clean-up."""
        _LOGGER.info("Spot Clean Pressed")
        await self.vacuum.async_set({"5": "Spot"})

    async def async_set_fan_speed(self, fan_speed, **kwargs):
        """Set fan speed."""
        _LOGGER.info("Fan Speed Selected")
        if fan_speed == "No Suction":
            fan_speed = "No_suction"
        elif fan_speed == "Boost IQ":
            fan_speed = "Boost_IQ"
        elif fan_speed == "Pure":
            fan_speed = "Quiet"
        await self.vacuum.async_set({"102": fan_speed})

    async def async_send_command(
        self, command: str, params: dict | list | None = None, **kwargs
    ) -> None:
        """Send a command to a vacuum cleaner."""
        _LOGGER.info("Send Command %s Pressed", command)
        if command == "edgeClean":
            await self.vacuum.async_set({"5": "Edge"})
        elif command == "smallRoomClean":
            await self.vacuum.async_set({"5": "SmallRoom"})
        elif command == "autoClean":
            await self.vacuum.async_set({"5": "auto"})
        elif command == "autoReturn":
            if self.auto_return:
                await self.vacuum.async_set({"135": False})
            else:
                await self.vacuum.async_set({"135": True})
        elif command == "doNotDisturb":
            if self.do_not_disturb:
                await self.vacuum.async_set({"139": "MEQ4MDAwMDAw"})
                await self.vacuum.async_set({"107": False})
            else:
                await self.vacuum.async_set({"139": "MTAwMDAwMDAw"})
                await self.vacuum.async_set({"107": True})
        elif command == "boostIQ":
            if self.boost_iq:
                await self.vacuum.async_set({"118": False})
            else:
                await self.vacuum.async_set({"118": True})
        elif command == "roomClean":
            roomIds = params.get("roomIds", [1])
            count = params.get("count", 1)
            clean_request = {"roomIds": roomIds, "cleanTimes": count}
            method_call = {
                "method": "selectRoomsClean",
                "data": clean_request,
                "timestamp": round(time.time() * 1000),
            }
            json_str = json.dumps(method_call, separators=(",", ":"))
            base64_str = base64.b64encode(json_str.encode("utf8")).decode("utf8")
            _LOGGER.info("roomClean call %s", json_str)
            await self.vacuum.async_set({"124": base64_str})

    async def async_will_remove_from_hass(self):
        await self.vacuum.async_disconnect()
