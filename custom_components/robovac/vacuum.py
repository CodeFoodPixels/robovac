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
from enum import IntEnum
from homeassistant.components.vacuum import StateVacuumEntity, VacuumEntityFeature
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
)

from .const import CONF_VACS, DOMAIN

from .tuyalocalapi import TuyaDevice

from homeassistant.const import ATTR_BATTERY_LEVEL


class RoboVacEntityFeature(IntEnum):
    """Supported features of the RoboVac entity."""

    EDGE = 1
    SMALL_ROOM = 2
    CLEANING_TIME = 4
    CLEANING_AREA = 8
    DO_NOT_DISTURB = 16
    AUTO_RETURN = 32
    CONSUMABLES = 64
    ROOM = 128
    ZONE = 256
    MAP = 512
    BOOST_IQ = 1024


ATTR_BATTERY_ICON = "battery_icon"
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
# Time between updating data from GitHub
REFRESH_RATE = 20
SCAN_INTERVAL = timedelta(seconds=REFRESH_RATE)


class robovac(TuyaDevice):
    """"""


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize my test integration 2 config entry."""
    # print("vacuum:async_setup_entry")
    vacuums = config_entry.data[CONF_VACS]
    # print("Vac:", vacuums)
    for item in vacuums:
        item = vacuums[item]
        # print("item")
        async_add_entities([RoboVacEntity(item)])


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
        """Return the cleaning mode of the vacuum cleaner."""
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
    def state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the vacuum cleaner."""
        data: dict[str, Any] = {}
        if self.supported_features & VacuumEntityFeature.BATTERY:
            data[ATTR_BATTERY_LEVEL] = self.battery_level
            data[ATTR_BATTERY_ICON] = self.battery_icon
        if self.supported_features & VacuumEntityFeature.FAN_SPEED:
            data[ATTR_FAN_SPEED] = self.fan_speed
        if self.supported_features & VacuumEntityFeature.STATUS:
            data[ATTR_STATUS] = self.status
        data[ATTR_MODE] = self.mode
        if self.robovac_supported & RoboVacEntityFeature.CLEANING_AREA:
            data[ATTR_CLEANING_AREA] = self.cleaning_area
        if self.robovac_supported & RoboVacEntityFeature.CLEANING_TIME:
            data[ATTR_CLEANING_TIME] = self.cleaning_time
        if self.robovac_supported & RoboVacEntityFeature.AUTO_RETURN:
            data[ATTR_AUTO_RETURN] = self.auto_return
        if self.robovac_supported & RoboVacEntityFeature.DO_NOT_DISTURB:
            data[ATTR_DO_NOT_DISTURB] = self.do_not_disturb
        if self.robovac_supported & RoboVacEntityFeature.BOOST_IQ:
            data[ATTR_BOOST_IQ] = self.boost_iq
        if self.robovac_supported & RoboVacEntityFeature.CONSUMABLES:
            data[ATTR_CONSUMABLES] = self.consumables
        return data

    @property
    def capability_attributes(self) -> Mapping[str, Any] | None:
        """Return capability attributes."""
        if self.supported_features & VacuumEntityFeature.FAN_SPEED:
            return {
                ATTR_FAN_SPEED_LIST: self.fan_speed_list,
                # CONF_ACCESS_TOKEN: self.access_token,
                CONF_IP_ADDRESS: self.ip_address,
                ATTR_MODEL_CODE: self.model_code,
            }
        else:
            return {
                # CONF_ACCESS_TOKEN: self.access_token,
                CONF_IP_ADDRESS: self.ip_address,
                ATTR_MODEL_CODE: self.model_code,
            }

    def __init__(self, item) -> None:
        # print("vacuum:RoboVacEntity")
        # print("init_item", item)
        """Initialize mytest2 Sensor."""
        super().__init__()
        self._attr_name = item[CONF_NAME]
        self._attr_unique_id = item[CONF_ID]
        self._attr_supported_features = 4084
        self._attr_model_code = item[CONF_MODEL]
        self._attr_ip_address = item[CONF_IP_ADDRESS]
        self._attr_access_token = item[CONF_ACCESS_TOKEN]
        self._attr_robovac_supported = 0
        if self.model_code[0:5] in [
            "T2103",
            "T2117",
            "T2118",
            "T2119",
            "T2120",
            "T2123",
            "T2128",
            "T2130",
        ]:  # C
            self._attr_fan_speed_list = ["No Suction", "Standard", "Boost IQ", "Max"]
            self._attr_robovac_supported = (
                RoboVacEntityFeature.EDGE | RoboVacEntityFeature.SMALL_ROOM
            )
        elif self.model_code[0:5] in ["T1250", "T2250", "T2251", "T2252", "T2253"]:  # G
            self._attr_fan_speed_list = ["Standard", "Turbo", "Max", "Boost IQ"]
            self._attr_robovac_supported = (
                RoboVacEntityFeature.CLEANING_TIME
                | RoboVacEntityFeature.CLEANING_AREA
                | RoboVacEntityFeature.DO_NOT_DISTURB
                | RoboVacEntityFeature.AUTO_RETURN
                | RoboVacEntityFeature.CONSUMABLES
            )
        elif self.model_code[0:5] in ["T2262"]:  # X
            self._attr_fan_speed_list = ["Pure", "Standard", "Turbo", "Max"]
            self._attr_robovac_supported = (
                RoboVacEntityFeature.CLEANING_TIME
                | RoboVacEntityFeature.CLEANING_AREA
                | RoboVacEntityFeature.DO_NOT_DISTURB
                | RoboVacEntityFeature.AUTO_RETURN
                | RoboVacEntityFeature.CONSUMABLES
                | RoboVacEntityFeature.ROOM
                | RoboVacEntityFeature.ZONE
                | RoboVacEntityFeature.MAP
                | RoboVacEntityFeature.BOOST_IQ
            )
        else:
            self._attr_fan_speed_list = ["Standard"]
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
            access_token=item[CONF_ACCESS_TOKEN],
            ip_address=item[CONF_IP_ADDRESS],
        )
        self.vacuum = robovac(
            device_id=self.unique_id,
            host=self.ip_address,
            local_key=self.access_token,
            timeout=2,
            ping_interval=10
            # ping_interval=REFRESH_RATE / 2,
        )
        self.error_code = None
        self.tuya_state = None
        self.tuyastatus = None
        print("vac:", self.vacuum)

    async def async_update(self):
        """Synchronise state from the vacuum."""
        print("update:", self.name)
        if self.ip_address == "":
            return
        await self.vacuum.async_get()
        self.tuyastatus = self.vacuum._dps
        print("Tuya local API Result:", self.tuyastatus)
        # for 15C
        self._attr_battery_level = self.tuyastatus.get("104")
        self.tuya_state = self.tuyastatus.get("15")
        self.error_code = self.tuyastatus.get("106")
        self._attr_mode = self.tuyastatus.get("5")
        self._attr_fan_speed = self.tuyastatus.get("102")
        if self.fan_speed == "No_suction":
            self._attr_fan_speed = "No Suction"
        elif self.fan_speed == "Boost_IQ":
            self._attr_fan_speed = "Boost IQ"
        elif self.fan_speed == "Quiet":
            self._attr_fan_speed = "Pure"
        # for G30
        self._attr_cleaning_area = self.tuyastatus.get("110")
        self._attr_cleaning_time = self.tuyastatus.get("109")
        self._attr_auto_return = self.tuyastatus.get("135")
        self._attr_do_not_disturb = self.tuyastatus.get("107")
        if self.tuyastatus.get("142") is not None:
            self._attr_consumables = ast.literal_eval(
                base64.b64decode(self.tuyastatus.get("142")).decode("ascii")
            )["consumable"]["duration"]
            print(self.consumables)
        # For X8
        self._attr_boost_iq = self.tuyastatus.get("118")
        # self.map_data = self.tuyastatus.get("121")
        # self.erro_msg? = self.tuyastatus.get("124")
        if self.tuyastatus.get("116") is not None:
            self._attr_consumables = ast.literal_eval(
                base64.b64decode(self.tuyastatus.get("116")).decode("ascii")
            )["consumable"]["duration"]
            print(self.consumables)

    @property
    def status(self):
        """Return the status of the vacuum cleaner."""
        print("status:", self.error_code, self.tuya_state)
        if self.ip_address == "":
            return "Error: Set the IP Address"
        if type(self.error_code) is not None and self.error_code not in [0, "no_error"]:
            if self.error_code == 1:
                return "Error: Front bumper stuck"
            elif self.error_code == 2:
                return "Error: Wheel stuck"
            elif self.error_code == 3:
                return "Error: Side brush"
            elif self.error_code == 4:
                return "Error: Rolling brush bar stuck"
            elif self.error_code == 5:
                return "Error: Device trapped"
            elif self.error_code == 6:
                return "Error: Device trapped"
            elif self.error_code == 7:
                return "Error: Wheel suspended"
            elif self.error_code == 8:
                return "Error: Low battery"
            elif self.error_code == 9:
                return "Error: Magnetic boundary"
            elif self.error_code == 12:
                return "Error: Right wall sensor"
            elif self.error_code == 13:
                return "Error: Device tilted"
            elif self.error_code == 14:
                return "Error: Insert dust collector"
            elif self.error_code == 17:
                return "Error: Restricted area detected"
            elif self.error_code == 18:
                return "Error: Laser cover stuck"
            elif self.error_code == 19:
                return "Error: Laser sesor stuck"
            elif self.error_code == 20:
                return "Error: Laser sensor blocked"
            elif self.error_code == 21:
                return "Error: Base blocked"
            elif self.error_code == "S1":
                return "Error: Battery"
            elif self.error_code == "S2":
                return "Error: Wheel Module"
            elif self.error_code == "S3":
                return "Error: Side Brush"
            elif self.error_code == "S4":
                return "Error: Suction Fan"
            elif self.error_code == "S5":
                return "Error: Rolling Brush"
            elif self.error_code == "S8":
                return "Error: Path Tracking Sensor"
            elif self.error_code == "Wheel_stuck":
                return "Error: Wheel stuck"
            elif self.error_code == "R_brush_stuck":
                return "Error: Rolling brush stuck"
            elif self.error_code == "Crash_bar_stuck":
                return "Error: Front bumper stuck"
            elif self.error_code == "sensor_dirty":
                return "Error: Sensor dirty"
            elif self.error_code == "N_enough_pow":
                return "Error: Low battery"
            elif self.error_code == "Stuck_5_min":
                return "Error: Device trapped"
            elif self.error_code == "Fan_stuck":
                return "Error: Fan stuck"
            elif self.error_code == "S_brush_stuck":
                return "Error: Side brush stuck"
            else:
                return "Error: " + str(self.error_code)
        elif self.tuya_state == "Running":
            return "Cleaning"
        elif self.tuya_state == "Locating":
            return "Locating"
        elif self.tuya_state == "remote":
            return "Cleaning"
        elif self.tuya_state == "Charging":
            return "Charging"
        elif self.tuya_state == "completed":
            return "Docked"
        elif self.tuya_state == "Recharge":
            return "Returning"
        elif self.tuya_state == "Sleeping":
            return "Sleeping"
        elif self.tuya_state == "standby":
            return "Standby"
        else:
            return "Cleaning"

    async def async_locate(self, **kwargs):
        """Locate the vacuum cleaner."""
        print("Locate Pressed")
        _LOGGER.info("Locate Pressed")
        if self.tuyastatus.get("103"):
            await self.vacuum.async_set({"103": False}, None)
        else:
            await self.vacuum.async_set({"103": True}, None)

    async def async_return_to_base(self, **kwargs):
        """Set the vacuum cleaner to return to the dock."""
        print("Return home Pressed")
        _LOGGER.info("Return home Pressed")
        await self.vacuum.async_set({"101": True}, None)
        await asyncio.sleep(1)
        self.async_update

    async def async_start_pause(self, **kwargs):
        """Pause the cleaning task or resume it."""
        print("Start/Pause Pressed")
        _LOGGER.info("Start/Pause Pressed")
        if self.tuyastatus.get("2") or self.tuya_state == "Recharge":
            await self.vacuum.async_set({"2": False}, None)
        else:
            if self.mode == "Nosweep":
                self._attr_mode = "auto"
            elif self.mode == "room" and (
                self.status == "Charging" or self.status == "completed"
            ):
                self._attr_mode = "auto"
            await self.vacuum.async_set({"5": self.mode}, None)
        await asyncio.sleep(1)
        self.async_update

    async def async_clean_spot(self, **kwargs):
        """Perform a spot clean-up."""
        print("Spot Clean Pressed")
        _LOGGER.info("Spot Clean Pressed")
        await self.vacuum.async_set({"5": "Spot"}, None)
        await asyncio.sleep(1)
        self.async_update

    async def async_set_fan_speed(self, fan_speed, **kwargs):
        """Set fan speed."""
        print("Fan Speed Selected", fan_speed)
        _LOGGER.info("Fan Speed Selected")
        if fan_speed == "No Suction":
            fan_speed = "No_suction"
        elif fan_speed == "Boost IQ":
            fan_speed = "Boost_IQ"
        elif fan_speed == "Pure":
            fan_speed = "Quiet"
        await self.vacuum.async_set({"102": fan_speed}, None)
        await asyncio.sleep(1)
        self.async_update

    async def async_send_command(
        self, command: str, params: dict | list | None = None, **kwargs
    ) -> None:
        """Send a command to a vacuum cleaner."""
        _LOGGER.info("Send Command %s Pressed", command)
        if command == "edgeClean":
            await self.vacuum.async_set({"5": "Edge"}, None)
        elif command == "smallRoomClean":
            await self.vacuum.async_set({"5": "SmallRoom"}, None)
        elif command == "autoClean":
            await self.vacuum.async_set({"5": "auto"}, None)
        elif command == "autoReturn":
            if self.auto_return:
                await self.vacuum.async_set({"135": False}, None)
            else:
                await self.vacuum.async_set({"135": True}, None)
        elif command == "doNotDisturb":
            if self.do_not_disturb:
                await self.vacuum.async_set({"139": "MEQ4MDAwMDAw"}, None)
                await self.vacuum.async_set({"107": False}, None)
            else:
                await self.vacuum.async_set({"139": "MTAwMDAwMDAw"}, None)
                await self.vacuum.async_set({"107": True}, None)
        elif command == "boostIQ":
            if self.boost_iq:
                await self.vacuum.async_set({"118": False}, None)
            else:
                await self.vacuum.async_set({"118": True}, None)
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
            await self.vacuum.async_set({"124": base64_str}, None)
        await asyncio.sleep(1)
        self.async_update
