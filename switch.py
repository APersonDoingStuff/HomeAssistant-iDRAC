"""iDRAC Switches."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import _LOGGER, DOMAIN, IDRAC_DATA
from .idracAPI import idracClient


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up Switches."""
    if discovery_info is None:
        return

    switches = []
    for host_config in discovery_info["config"][DOMAIN]:
        host_name = host_config["host"]
        if hass.data[IDRAC_DATA][host_name] is None:
            continue

        switch = idracSwitch(
            unique_id=f"idrac_{host_name}_powerstate_switch",
            name=f"idrac_{host_name}_powerstate_switch",
            icon="",
            host_name=host_name,
        )
        switches.append(switch)

    add_entities(switches)


class idracSwitch(SwitchEntity):
    """Node Switch."""

    def __init__(
        self,
        unique_id: str,
        name: str,
        icon: str,
        host_name: str,
    ) -> None:
        """Create A switch for a Node."""
        self.unique_id = unique_id
        self.name = name
        self.icon = icon
        self._host_name = host_name

    @property
    def is_on(self) -> bool:
        """Return True if the entity is on."""
        client: idracClient = self.hass.data[IDRAC_DATA][self._host_name]
        _LOGGER.warning(
            "Switch Status in %s is %d", self._host_name, client.powerState == "On"
        )
        return client.powerState == "On"

    async def async_turn_on(self):
        """Turn the switch on."""
        client: idracClient = self.hass.data[IDRAC_DATA][self._host_name]
        await self.hass.async_add_executor_job(client.TurnOnSystem)
        self.schedule_update_ha_state()

    async def async_turn_off(self):
        """Turn the switch off."""
        client: idracClient = self.hass.data[IDRAC_DATA][self._host_name]
        await self.hass.async_add_executor_job(client.TurnOffSystem)
        self.schedule_update_ha_state()
