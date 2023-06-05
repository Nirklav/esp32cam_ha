"""Constants for the ESP32 Camera integration."""

import logging
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "esp32_camera"
PLATFORMS: Final = [Platform.CAMERA]

LOGGER = logging.getLogger(__package__)

CONF_ESP32_CAM_IP: Final = "esp32_cam_ip"
CONF_ESP32_CAM_PORT: Final = "esp32_cam_port"