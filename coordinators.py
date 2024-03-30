from datetime import timedelta  # noqa: D100
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import _LOGGER, UPDATE_INTERVAL_CPU
from .idracAPI import idracClient


def idrac_power_coordinator(
    hass: HomeAssistant, idrac: idracClient, host_name: str
) -> DataUpdateCoordinator[dict[str, Any] | None]:
    """Get Powerstate from iDRAC."""

    async def async_update_data() -> dict[str, Any] | None:
        def poll_api() -> dict[str, Any] | None:
            prox = idrac.getPowerState()
            return prox

        result = await hass.async_add_executor_job(poll_api)

        if result == "Unknown":
            _LOGGER.warning("The iDRAC Powerstate not available in: %s", host_name)
            return {"powerstate": "Unknown", "name": "_powerstate"}

        return {"powerstate": result, "name": "_powerstate"}

    return DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"idrac_coordinator_{host_name}_powerstate",
        update_method=async_update_data,
        update_interval=timedelta(seconds=UPDATE_INTERVAL_CPU),
    )
