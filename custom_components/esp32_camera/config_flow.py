"""Config flow to configure the ESP32 Camera integration."""
from __future__ import annotations

from types import MappingProxyType
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_ESP32_CAM_IP, CONF_ESP32_CAM_PORT, DOMAIN, LOGGER


@callback
def async_get_schema(
    defaults: dict[str, Any] | MappingProxyType[str, Any], show_name: bool = False
) -> vol.Schema:
    """Return ESP32 Camera schema."""
    schema = {
        vol.Required(CONF_ESP32_CAM_IP, default=defaults.get(CONF_ESP32_CAM_IP)): str,
        vol.Required(CONF_ESP32_CAM_PORT, default=defaults.get(CONF_ESP32_CAM_PORT)): int,
        vol.Optional(
            CONF_PASSWORD,
            default=defaults.get(CONF_PASSWORD, ""),
        ): str,
    }

    if show_name:
        schema = {
            vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME)): str,
            **schema,
        }

    return vol.Schema(schema)


class ESP32CameraFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for ESP32 Camera."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> ESP32CameraOptionsFlowHandler:
        """Get the options flow for this handler."""
        return ESP32CameraOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match({
                    CONF_ESP32_CAM_IP: user_input[CONF_ESP32_CAM_IP],
                    CONF_ESP32_CAM_PORT: user_input[CONF_ESP32_CAM_PORT],
                }
            )

            # Storing data in option, to allow for changing them later
            # using an options flow.
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, user_input[CONF_ESP32_CAM_IP]),
                data={},
                options={
                    CONF_ESP32_CAM_IP: user_input[CONF_ESP32_CAM_IP],
                    CONF_ESP32_CAM_PORT: user_input[CONF_ESP32_CAM_PORT],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                },
            )
        else:
            user_input = {}

        return self.async_show_form(
            step_id="user",
            data_schema=async_get_schema(user_input, show_name=True),
            errors=errors,
        )


class ESP32CameraOptionsFlowHandler(OptionsFlow):
    """Handle ESP32 Camera options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize ESP32 Camera options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage ESP32 Camera options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME, user_input[CONF_ESP32_CAM_IP]),
                data={
                    CONF_ESP32_CAM_IP: user_input[CONF_ESP32_CAM_IP],
                    CONF_ESP32_CAM_PORT: user_input[CONF_ESP32_CAM_PORT],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                },
            )
        else:
            user_input = {}

        return self.async_show_form(
            step_id="init",
            data_schema=async_get_schema(user_input or self.config_entry.options),
            errors=errors,
        )