import logging

from collections import namedtuple
from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_DEVICES
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, CONF_IP
from .entity import TroxBaseEntity

_LOGGER = logging.getLogger(__name__)

# Creating nested dictionary of key/pairs
OPTIONS = {
    "Override": {0: "none", 1: "open", 2: "closed", 3: "q_min", 4: "q_max"},
    "Command": {0: "none", 1: "synchronization", 2: "test", 4: "reset"},
}

DATA_TYPE = namedtuple('DataType', ['category', 'icon'])

TroxEntity = namedtuple('TroxEntity', ['group', 'key', 'entityName', 'data_type', 'options'])
ENTITIES = [
    TroxEntity("Commands", "Override", "Override", DATA_TYPE(None, None), OPTIONS["Override"]),
    TroxEntity("Commands", "Command", "Command", DATA_TYPE(None, None), OPTIONS["Command"]),
    TroxEntity(None, "Config_Selection", "Config Selection", DATA_TYPE(EntityCategory.CONFIG, None), None),
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup selects from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for troxentity in ENTITIES:
        ha_entities.append(TroxSelectEntity(coordinator, troxentity))

    async_add_devices(ha_entities, True)


class TroxSelectEntity(TroxBaseEntity, SelectEntity):
    """Representation of a Select."""

    def __init__(self, coordinator, troxentity):
        """Pass coordinator to TroxEntity."""
        super().__init__(coordinator, troxentity)

        """Select Entity properties"""
        if self._key == "Config_Selection":
            self._options = self.coordinator.get_config_options()
        else:
            self._options = troxentity.options
            self._attr_translation_key = self._key

    @property
    def current_option(self):
        try:
            if self._key == "Config_Selection":
                optionIndex = self.coordinator.config_selection
                option = self._options[optionIndex]
            else:
                optionIndex = self.coordinator.get_value(self._group, self._key)
                option = self._options[optionIndex]
        except Exception as e:
            option = "Unknown"
        return option

    @property
    def options(self):
        return list(self._options.values())

    async def async_select_option(self, option):
        """ Find new value """
        value = None

        for key, val in self._options.items():
            if val == option:
                value = key
                break

        if value is None:
            return

        """ Write value to device """
        try:
            if self._key == "Config_Selection":
                await self.coordinator.config_select(option, value)
            else:           
                await self.coordinator.write_value(self._group, self._key, value)
        except Exception as err:
            _LOGGER.debug("Error writing command: %s %s", self._group, self._key)
        finally:
            self.async_schedule_update_ha_state(force_refresh=False)
