"""iDRAC Sensors."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import COORDINATORS, DOMAIN, IDRAC_DATA
from .entity import SENSOR_DESCRIPTIONS, iDRACsensor


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up sensors."""
    if discovery_info is None:
        return

    sensors = []
    for host_config in discovery_info["config"][DOMAIN]:
        host_name = host_config["host"]
        host_name_coordinators = hass.data[DOMAIN][COORDINATORS][host_name]
        power_coordinator = host_name_coordinators["powerstate"]
        if hass.data[IDRAC_DATA][host_name] is None:
            continue
        sensor = get_powerstate_sensor(
            power_coordinator,
            host_name,
            f"iDRAC_{host_name}_powerstate_status",
            SENSOR_DESCRIPTIONS[0],
        )
        if sensor is not None:
            sensors.append(sensor)
    add_entities(sensors)


def get_powerstate_sensor(coordinator, host_name, name, description):
    """Create Sensor for dependency in host."""

    if (coordinator.data) is None:
        return None

    dep_sensor = iDRACsensor(
        coordinator=coordinator,
        unique_id=f"{name}",
        name=f"{name}",
        icon="",
        host_name=host_name,
        description=description,
    )
    return dep_sensor
