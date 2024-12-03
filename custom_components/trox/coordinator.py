import async_timeout
import datetime as dt
import logging

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .pytrox.modbusdevice import ModbusDevice, ModbusGroup

_LOGGER = logging.getLogger(__name__)

class TroxCoordinator(DataUpdateCoordinator):    
    def __init__(self, hass, device, device_module:str, ip, port, slave_id, scan_interval, scan_interval_fast):
        """Initialize coordinator parent"""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="ModbusDevice: " + device.name,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=dt.timedelta(seconds=scan_interval),
        )

        self._fast_poll_enabled = False
        self._fast_poll_count = 0
        self._normal_poll_interval = scan_interval
        self._fast_poll_interval = scan_interval_fast

        self._device = device
        self._modbusDevice = ModbusDevice(device_module, ip, port, slave_id)

        # Initialize states
        self._measurements = None
        self._setpoints = None
        self._timestamp = dt.datetime(2024, 1, 1)

        # Storage for config selection
        self.config_selection = 0

        # Callback to entities
        self._update_callbacks = {}

    @property
    def device_id(self):
        return self._device.id

    @property
    def devicename(self):
        return self._device.name

    @property
    def identifiers(self):
        return self._device.identifiers

    def setFastPollMode(self):
        _LOGGER.debug("Enabling fast poll mode")
        self._fast_poll_enabled = True
        self._fast_poll_count = 0
        self.update_interval = dt.timedelta(seconds=self._fast_poll_interval)
        self._schedule_refresh()

    def setNormalPollMode(self):
        _LOGGER.debug("Enabling normal poll mode")
        self._fast_poll_enabled = False
        self.update_interval = dt.timedelta(seconds=self._normal_poll_interval)


    async def _async_update_data(self):
        _LOGGER.debug("Coordinator updating data!!")

        """ Counter for fast polling """
        if self._fast_poll_enabled:
            self._fast_poll_count += 1
            if self._fast_poll_count > 5:
                self.setNormalPollMode()

        """ Fetch data """
        try:
            async with async_timeout.timeout(20):
                await self._modbusDevice.readCommands()
                await self._modbusDevice.readDeviceInfo()
                await self._async_update_deviceInfo()
                await self._modbusDevice.readSensors()
                
        except Exception as err:
            _LOGGER.debug("Failed when fetching data: %s", str(err))

    async def _async_update_deviceInfo(self) -> None:
        device_registry = dr.async_get(self.hass)
        device_registry.async_update_device(
            self.device_id,
            manufacturer="Trox",
            model=self._modbusDevice.getModelName(),
            sw_version=self._modbusDevice.getFW(),
        )
        _LOGGER.debug("Updated device data for: %s", self.devicename) 

    ################################
    ######## Configuration #########
    ################################   
    # Register callback to entity
    def registerOnUpdateCallback(self, entity, callbackfunc):
        self._update_callbacks.update({entity: callbackfunc})

    async def config_select(self, key, value):
        _LOGGER.debug("Selected: %s %s", key, value)

        self.config_selection = value
        try:
            await self._modbusDevice.readValue(ModbusGroup.CONFIG, key)
        finally:
            await self._update_callbacks["Config Value"](key)

    def get_config_options(self):
        options = {}
        for i, config in enumerate(self._modbusDevice.Datapoints[ModbusGroup.CONFIG]):
            options.update({i:config})
        return options

    ################################
    ######### Read / Write #########
    ################################   
    def get_value(self, group, key):
        if group in self._modbusDevice.Datapoints:
            if key in self._modbusDevice.Datapoints[group]:
                return self._modbusDevice.Datapoints[group][key].Value
        return None

    async def write_value(self, group, key, value) -> bool:
        _LOGGER.debug("Write_Data: %s - %s - %s", group, key, value)
        await self._modbusDevice.writeValue(group, key, value)
        self.setFastPollMode()
