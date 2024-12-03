import logging

from collections import namedtuple
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .entity import ModbusBaseEntity

from .pytrox.modbusdevice import ModbusGroup

_LOGGER = logging.getLogger(__name__)

DATA_TYPE = namedtuple('DataType', ['deviceClass', 'category', 'icon'])
DATA_TYPES = {
    "Status": DATA_TYPE(BinarySensorDeviceClass.PROBLEM, None, "mdi:bell"),
}

ModbusEntity = namedtuple('ModbusEntity', ['group', 'key', 'data_type'])
ENTITIES = [
    ModbusEntity(ModbusGroup.DEVICE_INFO, "Status", DATA_TYPES["Status"]),
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for modbusentity in ENTITIES:
        ha_entities.append(ModbusBinarySensorEntity(coordinator, modbusentity))

    async_add_devices(ha_entities, True)


class ModbusBinarySensorEntity(ModbusBaseEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, modbusentity):
        super().__init__(coordinator, modbusentity)

        """Sensor Entity properties"""
        self._attr_device_class = modbusentity.data_type.deviceClass

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        attrs = {}

        status = self.coordinator.get_value(self._group, self._key)

        if (status & (1 << 4)) != 0:
            newAttr = {"Mechanical Overload":"ALARM"}
            attrs.update(newAttr)
        if (status & (1 << 7)) != 0:
            newAttr = {"Internal Activity":"WARNING"}
            attrs.update(newAttr)
        if (status & (1 << 9)) != 0:
            newAttr = {"Bus Timeout":"WARNING"}
            attrs.update(newAttr)
        return attrs
        
    @property
    def is_on(self):
        """Return the state of the switch."""
        status = self.coordinator.get_value(self._group, self._key)
        alarm = (status & (1 << 4)) != 0
        return alarm
