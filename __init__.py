"""Support for DELL iDRAC redfish."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_VERSION,
    COORDINATORS,
    DEFAULT_PORT,
    DEFAULT_VERSION,
    DOMAIN,
    IDRAC_DATA,
)
from .coordinators import idrac_power_coordinator
from .idracAPI import idracClient

# PLATFORMS = [Platform.SENSOR, Platform.SWITCH]

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_HOST): cv.string,
                        vol.Required(CONF_USERNAME): cv.string,
                        vol.Required(CONF_PASSWORD): cv.string,
                        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                        vol.Optional(CONF_VERSION, default=DEFAULT_VERSION): cv.string,
                    }
                )
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the platform."""
    hass.data.setdefault(DOMAIN, {})

    def build_client():
        """Build the idrac client connection."""
        hass.data[IDRAC_DATA] = {}

        for entry in config[DOMAIN]:
            host = entry[CONF_HOST]
            port = entry[CONF_PORT]
            user = entry[CONF_USERNAME]
            password = entry[CONF_PASSWORD]

            hass.data[IDRAC_DATA][host] = None

            idrac_client = idracClient(
                host,
                port,
                user,
                password,
            )

            if idrac_client is not None:
                idrac_client.build_client()

            hass.data[IDRAC_DATA][host] = idrac_client

    await hass.async_add_executor_job(build_client)

    coordinators: dict[
        str, dict[str, DataUpdateCoordinator[dict[str, Any] | None]]
    ] = {}
    hass.data[DOMAIN][COORDINATORS] = coordinators

    for host_config in config[DOMAIN]:
        host_name = host_config["host"]
        coordinators[host_name] = {}

        idrac_client: idracClient = hass.data[IDRAC_DATA][host_name]

        # Skip invalid hosts
        if idrac_client is None:
            continue

        coordinator = idrac_power_coordinator(hass, idrac_client, host_name)
        await coordinator.async_refresh()
        coordinators[host_name]["powerstate"] = coordinator

    for component in PLATFORMS:
        await hass.async_create_task(
            async_load_platform(hass, component, DOMAIN, {"config": config}, config)
        )

    return True
