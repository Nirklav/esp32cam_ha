"""The ESP32 Camera integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .camera import ESP32Camera
from .const import CONF_ESP32_CAM_IP, CONF_ESP32_CAM_PORT, PLATFORMS
from .util import filter_urllib3_logging

__all__ = [
    "CONF_ESP32_CAM_IP",
    "CONF_ESP32_CAM_PORT",
    "ESP32Camera",
    "filter_urllib3_logging",
]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the ESP32 Camera integration."""
    filter_urllib3_logging()
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload entry when it's updated.
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when it changed."""
    await hass.config_entries.async_reload(entry.entry_id)