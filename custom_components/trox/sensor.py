import logging

from collections import namedtuple
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import CONF_DEVICES, PERCENTAGE, DEGREE
from homeassistant.const import UnitOfPressure, UnitOfTemperature, UnitOfVolumeFlowRate, UnitOfElectricPotential
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, CONF_IP
from .entity import ModbusBaseEntity

from .pytrox.modbusdevice import ModbusGroup

_LOGGER = logging.getLogger(__name__)

DATA_TYPE = namedtuple('DataType', ['units', 'deviceClass', 'category', 'icon'])
DATA_TYPES = {
    "degrees": DATA_TYPE(DEGREE, None, None, None),
    "flow": DATA_TYPE(UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR, None, None, "mdi:weather-windy"),
    "percent": DATA_TYPE(PERCENTAGE, None, None, None),
    "voltage": DATA_TYPE(UnitOfElectricPotential.VOLT, None, None, None),
}

ModbusEntity = namedtuple('ModbusEntity', ['group', 'key', 'data_type'])
ENTITIES = [
    ModbusEntity(ModbusGroup.SENSORS, "Position", DATA_TYPES["percent"]),
    ModbusEntity(ModbusGroup.SENSORS, "Position Degrees", DATA_TYPES["degrees"]),
    ModbusEntity(ModbusGroup.SENSORS, "Flowrate Percent", DATA_TYPES["percent"]),
    ModbusEntity(ModbusGroup.SENSORS, "Flowrate Actual", DATA_TYPES["flow"]),
    ModbusEntity(ModbusGroup.SENSORS, "Analog Setpoint", DATA_TYPES["voltage"]),
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for modbusentity in ENTITIES:
        ha_entities.append(ModbusSensorEntity(coordinator, modbusentity))

    async_add_devices(ha_entities, True)


class ModbusSensorEntity(ModbusBaseEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, modbusentity):
        super().__init__(coordinator, modbusentity)

        """Sensor Entity properties"""
        self._attr_device_class = modbusentity.data_type.deviceClass
        self._attr_native_unit_of_measurement = modbusentity.data_type.units

    @property
    def native_value(self):
        """Return the value of the sensor."""
        val = self.coordinator.get_value(self._group, self._key)
        return val
