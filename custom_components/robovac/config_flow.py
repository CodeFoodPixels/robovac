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

"""Config flow for Eufy Robovac integration."""
from __future__ import annotations
import json

import logging
from typing import Any, Optional
from copy import deepcopy

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import selector

from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_NAME,
    CONF_ID,
    CONF_MODEL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_IP_ADDRESS,
    CONF_DESCRIPTION,
    CONF_MAC,
    CONF_CLIENT_ID,
    CONF_REGION,
    CONF_TIME_ZONE,
    CONF_COUNTRY_CODE,
)

from .countries import (
    get_phone_code_by_country_code,
    get_phone_code_by_region,
    get_region_by_country_code,
    get_region_by_phone_code,
)

from .const import CONF_AUTODISCOVERY, DOMAIN, CONF_VACS

from .tuyawebapi import TuyaAPISession
from .eufywebapi import EufyLogon

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


def get_eufy_vacuums(self):
    """Login to Eufy and get the vacuum details"""

    eufy_session = EufyLogon(self["username"], self["password"])
    response = eufy_session.get_user_info()
    if response.status_code != 200:
        raise CannotConnect

    user_response = response.json()
    if user_response["res_code"] != 1:
        raise InvalidAuth

    response = eufy_session.get_device_info(
        user_response["user_info"]["request_host"],
        user_response["user_info"]["id"],
        user_response["access_token"],
    )

    device_response = response.json()

    response = eufy_session.get_user_settings(
        user_response["user_info"]["request_host"],
        user_response["user_info"]["id"],
        user_response["access_token"],
    )
    settings_response = response.json()

    self[CONF_CLIENT_ID] = user_response["user_info"]["id"]
    if (
        "tuya_home" in settings_response["setting"]["home_setting"]
        and "tuya_region_code"
        in settings_response["setting"]["home_setting"]["tuya_home"]
    ):
        self[CONF_REGION] = settings_response["setting"]["home_setting"]["tuya_home"][
            "tuya_region_code"
        ]
        if user_response["user_info"]["phone_code"]:
            self[CONF_COUNTRY_CODE] = user_response["user_info"]["phone_code"]
        else:
            self[CONF_COUNTRY_CODE] = get_phone_code_by_region(self[CONF_REGION])
    elif user_response["user_info"]["phone_code"]:
        self[CONF_REGION] = get_region_by_phone_code(
            user_response["user_info"]["phone_code"]
        )
        self[CONF_COUNTRY_CODE] = user_response["user_info"]["phone_code"]
    elif user_response["user_info"]["country"]:
        self[CONF_REGION] = get_region_by_country_code(
            user_response["user_info"]["country"]
        )
        self[CONF_COUNTRY_CODE] = get_phone_code_by_country_code(
            user_response["user_info"]["country"]
        )
    else:
        self[CONF_REGION] = "EU"
        self[CONF_COUNTRY_CODE] = "44"

    self[CONF_TIME_ZONE] = user_response["user_info"]["timezone"]

    tuya_client = TuyaAPISession(
        username="eh-" + self[CONF_CLIENT_ID],
        region=self[CONF_REGION],
        timezone=self[CONF_TIME_ZONE],
        phone_code=self[CONF_COUNTRY_CODE],
    )

    items = device_response["items"]
    self[CONF_VACS] = {}
    for item in items:
        if item["device"]["product"]["appliance"] == "Cleaning":
            try:
                device = tuya_client.get_device(item["device"]["id"])

                vac_details = {
                    CONF_ID: item["device"]["id"],
                    CONF_MODEL: item["device"]["product"]["product_code"],
                    CONF_NAME: item["device"]["alias_name"],
                    CONF_DESCRIPTION: item["device"]["name"],
                    CONF_MAC: item["device"]["wifi"]["mac"],
                    CONF_IP_ADDRESS: "",
                    CONF_AUTODISCOVERY: True,
                    CONF_ACCESS_TOKEN: device["localKey"],
                }
                self[CONF_VACS][item["device"]["id"]] = vac_details
            except:
                _LOGGER.debug(
                    "Skipping vacuum {}: found on Eufy but not on Tuya. Eufy details:".format(
                        item["device"]["id"]
                    )
                )
                _LOGGER.debug(json.dumps(item["device"], indent=2))

    return response


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    await hass.async_add_executor_job(get_eufy_vacuums, data)
    return data


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eufy Robovac."""

    data: Optional[dict[str, Any]]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=USER_SCHEMA)
        errors = {}
        try:
            unique_id = user_input[CONF_USERNAME]
            valid_data = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception: {}".format(e))
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            # return await self.async_step_repo(valid_data)
            return self.async_create_entry(title=unique_id, data=valid_data)
        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options flow for the component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry
        self.selected_vacuum = None

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            self.selected_vacuum = user_input["selected_vacuum"]
            return await self.async_step_edit()

        vacuums_config = self.config_entry.data[CONF_VACS]
        vacuum_list = {}
        for vacuum_id in vacuums_config:
            vacuum_list[vacuum_id] = vacuums_config[vacuum_id]["name"]

        devices_schema = vol.Schema(
            {vol.Required("selected_vacuum"): vol.In(vacuum_list)}
        )

        return self.async_show_form(
            step_id="init", data_schema=devices_schema, errors=errors
        )

    async def async_step_edit(self, user_input=None):
        """Manage the options for the custom component."""
        errors = {}

        vacuums = self.config_entry.data[CONF_VACS]

        if user_input is not None:
            updated_vacuums = deepcopy(vacuums)
            updated_vacuums[self.selected_vacuum][CONF_AUTODISCOVERY] = user_input[
                CONF_AUTODISCOVERY
            ]
            if user_input[CONF_IP_ADDRESS]:
                updated_vacuums[self.selected_vacuum][CONF_IP_ADDRESS] = user_input[
                    CONF_IP_ADDRESS
                ]

            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={CONF_VACS: updated_vacuums},
            )

            return self.async_create_entry(title="", data={})

        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_AUTODISCOVERY,
                    default=vacuums[self.selected_vacuum].get(CONF_AUTODISCOVERY, True),
                ): bool,
                vol.Optional(
                    CONF_IP_ADDRESS,
                    default=vacuums[self.selected_vacuum].get(CONF_IP_ADDRESS),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="edit", data_schema=options_schema, errors=errors
        )
