import logging

from collections import namedtuple
from homeassistant.components.number import NumberEntity
from homeassistant.const import PERCENTAGE

from .const import DOMAIN, CONF_IP
from .entity import TroxBaseEntity

_LOGGER = logging.getLogger(__name__)

LimitsTuple = namedtuple('limits', ['min_value', 'max_value', 'step'])
LIMITS = {}
LIMITS["percent"] = LimitsTuple(0, 100, 0.1)

DATA_TYPE = namedtuple('DataType', ['units', 'deviceClass', 'category', 'icon'])
DATA_TYPES = {}
DATA_TYPES["percent"] = DATA_TYPE(PERCENTAGE, None, None, None)

TroxEntity = namedtuple('TroxEntity', ['group', 'key', 'entityName', 'data_type', 'limits'])
ENTITIES = [
    TroxEntity("Commands", "Setpoint", "Flow Rate Setpoint", DATA_TYPES["percent"], LIMITS["percent"])
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup number from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for troxentity in ENTITIES:
        ha_entities.append(TroxNumberEntity(coordinator, troxentity))

    async_add_devices(ha_entities, True)

class TroxNumberEntity(TroxBaseEntity, NumberEntity):
    """Representation of a Number."""

    def __init__(self, coordinator, troxentity):
        """Pass coordinator to PaxCalimaEntity."""
        super().__init__(coordinator, troxentity)

        """Number Entity properties"""
        self._attr_device_class = troxentity.data_type.deviceClass
        self._attr_mode = "box"
        self._attr_native_min_value = troxentity.limits.min_value
        self._attr_native_max_value = troxentity.limits.max_value
        self._attr_native_step = troxentity.limits.step
        self._attr_native_unit_of_measurement = troxentity.data_type.units

        """Callback for updated value"""
        coordinator.registerOnUpdateCallback(self._key, self.update_callback)

    async def update_callback(self, newKey):
        self._key = newKey
        self.async_schedule_update_ha_state(force_refresh=False)

    @property
    def native_value(self) -> float | None:
        """Return number value."""
        val = self.coordinator.get_value(self._group, self._key)
        return val

    async def async_set_native_value(self, value):
        """ Write value to device """
        try:
            await self.coordinator.write_value(self._group, self._key, value)
        except Exception as err:
            _LOGGER.debug("Error writing command: %s %s", self._group, self._key)
        finally:
            self.async_schedule_update_ha_state(force_refresh=False)
            
