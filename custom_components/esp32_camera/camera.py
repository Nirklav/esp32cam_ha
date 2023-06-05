"""Support for ESP32 Camera."""
from __future__ import annotations

import asyncio

from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ESP32_CAM_IP, CONF_ESP32_CAM_PORT, DOMAIN, LOGGER

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a ESP32 Camera based on a config entry."""
    async_add_entities(
        [
            ESP32Camera(
                name=entry.title,
                password=entry.options[CONF_PASSWORD],
                ip=entry.options[CONF_ESP32_CAM_IP],
                port=entry.options[CONF_ESP32_CAM_PORT],
                unique_id=entry.entry_id,
                device_info=DeviceInfo(
                    name=entry.title,
                    identifiers={(DOMAIN, entry.entry_id)},
                ),
            )
        ]
    )

def placeholder(width: int, height: int) -> bytes:
    stream = BytesIO()
    img = Image.new('RGB', (width, height), color = 'gray')

    draw = ImageDraw.Draw(img)
    draw.text((width / 2, height / 2), "Connecting ...", (255,255,255), anchor="mm")

    img.save(stream, format="JPEG")

    return stream.getvalue()


class ESP32Camera(Camera):
    """An implementation of ESP32 camera."""

    def __init__(
        self,
        *,
        name: str | None = None,
        ip: str,
        port: int,
        password: str = "",
        unique_id: str | None = None,
        device_info: DeviceInfo | None = None,
    ) -> None:
        """Initialize a ESP32 camera."""
        super().__init__()
        self._attr_name = name
        self._attr_frame_interval = 0.1
        self._ip = ip
        self._port = port
        self._password = password

        self._task = None
        self._placeholder = placeholder(1600, 1200)
        self._image = None
        self._last_datetime = None

        if unique_id is not None:
            self._attr_unique_id = unique_id
        if device_info is not None:
            self._attr_device_info = device_info


    async def async_stream(self):
        method_id = 2
        content_type = 1
        timeout = timedelta(seconds=10)

        request = bytes('{"password":"%s"}' % self._password, 'UTF-8')
        reader, writer = await asyncio.open_connection(self._ip, self._port)

        writer.write(method_id.to_bytes(4, 'little'))
        writer.write(len(request).to_bytes(4, 'little'))
        writer.write(content_type.to_bytes(4, 'little'))
        writer.write(request)

        await writer.drain()

        image = BytesIO()
        while (datetime.now() - self._last_datetime) < timeout:
            size_bytes = await reader.readexactly(4)
            size = int.from_bytes(size_bytes, "little")

            left = size
            while left > 0:
                part = await reader.read(left)
                left -= len(part)
                image.write(part)
                await asyncio.sleep(0)
            
            self._image = image.getvalue()
            image.seek(0)
            image.truncate(0)

        writer.close()
        await writer.wait_closed()


    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""

        self._last_datetime = datetime.now()

        if self._task is None or self._task.done():
            if self._task is not None:
                exc = self._task.exception()
                if exc is not None:
                    LOGGER.error("Error in task: {}".format(exc))

            self._task = asyncio.create_task(self.async_stream())
            return self._placeholder

        if self._image is not None:
            return self._image

        return self._placeholder