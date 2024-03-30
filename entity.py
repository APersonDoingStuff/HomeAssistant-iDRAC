"""Setuo for iDRAC entity."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)


@dataclass(frozen=True)
class iDRACSensorEntityDescription(SensorEntityDescription):
    """Return Values."""

    value_fn: Callable[[str], str] = None


SENSOR_DESCRIPTIONS: list[SensorEntityDescription] = [
    iDRACSensorEntityDescription(
        value_fn=lambda data: cast(str, data),
        key="powerstate",
        translation_key="powerstate",
    ),
]


class idracEntity(CoordinatorEntity):
    """Represents any entity created for iDRAC redfish API."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        unique_id: str,
        name: str,
        icon: str,
        host_name: str,
    ) -> None:
        """Initialize the idrac entity."""
        super().__init__(coordinator)

        self.coordinator = coordinator
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._host_name = host_name
        self._attr_icon = icon
        self._available = True

        self._state = None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self._available


class iDRACsensor(idracEntity, SensorEntity):
    """Sensor fro iDRAC data."""

    entity_description: iDRACSensorEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        unique_id: str,
        name: str,
        icon: str,
        host_name: str,
        description: iDRACSensorEntityDescription,
    ) -> None:
        """Create the sensor for iDRAC."""
        super().__init__(coordinator, unique_id, name, icon, host_name)
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the state."""
        build: str | None = self.coordinator.data[self.entity_description.key]
        if build is None:
            return "Unknon"

        return self.entity_description.value_fn(build)
