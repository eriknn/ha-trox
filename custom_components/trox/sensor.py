import logging

from collections import namedtuple
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import CONF_DEVICES, PERCENTAGE, DEGREE
from homeassistant.const import UnitOfPressure, UnitOfTemperature, UnitOfVolumeFlowRate, UnitOfElectricPotential
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, CONF_IP
from .entity import TroxBaseEntity

_LOGGER = logging.getLogger(__name__)

DATA_TYPE = namedtuple('DataType', ['units', 'deviceClass', 'category', 'icon'])
DATA_TYPES = {}
DATA_TYPES["degrees"] = DATA_TYPE(DEGREE, None, None, None)
DATA_TYPES["flow"] = DATA_TYPE(UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR, None, None, "mdi:weather-windy")
DATA_TYPES["percent"] = DATA_TYPE(PERCENTAGE, None, None, None)
DATA_TYPES["voltage"] = DATA_TYPE(UnitOfElectricPotential.VOLT, None, None, None)

TroxEntity = namedtuple('TroxEntity', ['group', 'key', 'entityName', 'data_type'])
ENTITIES = [
    TroxEntity("Sensors", "Position", "Damper position", DATA_TYPES["percent"]),
    TroxEntity("Sensors", "Position_Deg", "Damper position degrees", DATA_TYPES["degrees"]),
    TroxEntity("Sensors", "Flowrate_Percent", "Flowrate Percent", DATA_TYPES["percent"]),
    TroxEntity("Sensors", "Flowrate_Actual", "Flowrate Actual", DATA_TYPES["flow"]),
    TroxEntity("Sensors", "Analog_SP", "Analog Setpoint", DATA_TYPES["voltage"]),
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for troxentity in ENTITIES:
        ha_entities.append(TroxSensorEntity(coordinator, troxentity))

    async_add_devices(ha_entities, True)


class TroxSensorEntity(TroxBaseEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, troxentity):
        super().__init__(coordinator, troxentity)

        """Sensor Entity properties"""
        self._attr_device_class = troxentity.data_type.deviceClass
        self._attr_native_unit_of_measurement = troxentity.data_type.units

    @property
    def native_value(self):
        """Return the value of the sensor."""
        val = self.coordinator.get_value(self._group, self._key)
        return val
