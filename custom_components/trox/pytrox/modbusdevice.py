from dataclasses import dataclass
from enum import Enum

import logging

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)

class ModbusAccess(Enum):
    R = 1
    RW = 2

class ModbusMode(Enum):
    INPUT = 3
    HOLDING = 4

class ModbusGroup(Enum):
    COMMANDS = (0, ModbusMode.HOLDING)
    DEVICE_INFO = (1, ModbusMode.HOLDING)
    SENSORS = (2, ModbusMode.HOLDING)
    CONFIG = (3, ModbusMode.HOLDING)

    @property
    def unique_id(self):
        return self.value[0]
    
    @property
    def mode(self):
        return self.value[1]

@dataclass
class ModbusDatapoint:
    Address: int                            # 0-indexed address
    Scaling: float = 1                      # Multiplier for raw value
    Value: float = 0                        # Scaled value
    Access: ModbusAccess = ModbusAccess.R   # Read / ReadWrite

class ModbusDevice():
    def __init__(self, device_model:str, host:str, port:int, slave_id:int):
        self._client = ModbusTcpClient(host, port)
        self._slave_id = slave_id
        self._device_model = device_model

        # Load correct datapoints
        self.load_datapoints()

    def load_datapoints(self):
        model_name = f"{self._device_model.lower().replace(' ', '_')}"

        if model_name == 'trox_tve':
            from .devices.tve import TVE
            self.Datapoints = TVE().Datapoints
        else:
            self.Datapoints = {}

    def twos_complement(self, number) -> int:
        if number >> 15:
            return -((number^0xFFFF) + 1)
        else:
            return number

    """ ******************************************************* """
    """ ********************* DEVICE INFO ********************* """
    """ ******************************************************* """
    def getModelName(self):
        return self._device_model
    
    def getFW(self):
        return self.Datapoints[ModbusGroup.DEVICE_INFO]["FW"].Value
    
    """ ******************************************************* """
    """ **************** READ GROUP OF VALUES ***************** """
    """ ******************************************************* """
    async def readCommands(self):
        await self.readGroup(ModbusGroup.COMMANDS)

    async def readDeviceInfo(self):
        await self.readGroup(ModbusGroup.DEVICE_INFO)

    async def readSensors(self):
        await self.readGroup(ModbusGroup.SENSORS)

    """ ******************************************************* """
    """ ******************** READ GROUP *********************** """
    """ ******************************************************* """
    async def readGroup(self, group:ModbusGroup):
        # We read multiple registers in one message
        _LOGGER.debug("Reading group: %s", group)
        n_reg = len(self.Datapoints[group])
        first_key = next(iter(self.Datapoints[group]))
        first_address = self.Datapoints[group][first_key].Address
   
        if group.mode  == ModbusMode.INPUT:
            response = self._client.read_input_registers(first_address,n_reg,self._slave_id)
        elif group.mode  == ModbusMode.HOLDING:
            response = self._client.read_holding_registers(first_address,n_reg,self._slave_id) 
            
        if response.isError():
            _LOGGER.debug("Error: %s", response)
            raise ModbusException('{}'.format(response))
        else:
            _LOGGER.debug("Read group success")
            for (dataPointName, data), newVal in zip(self.Datapoints[group].items(), response.registers):
                newVal_2 = self.twos_complement(newVal)
                
                if data.Scaling == 1.0:
                    data.Value = newVal_2
                else:
                    data.Value = newVal_2 * data.Scaling
                _LOGGER.debug("Key: %s Value: %s", dataPointName, data.Value)
                
    """ ******************************************************* """
    """ **************** READ SINGLE VALUE ******************** """
    """ ******************************************************* """
    async def readValue(self, group:ModbusGroup, key):
        # We read single register
        _LOGGER.debug("Reading value: %s - %s", group, key)

        if group.mode == ModbusMode.INPUT:
            response = self._client.read_input_registers(self.Datapoints[group][key].Address,1,self._slave_id)
        elif group.mode == ModbusMode.HOLDING:
            response = self._client.read_holding_registers(self.Datapoints[group][key].Address,1,self._slave_id)

        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            newVal_2 = self.twos_complement(response.registers[0])
            self.Datapoints[group][key].Value = newVal_2 * self.Datapoints[group][key].Scaling

    """ ******************************************************* """
    """ **************** WRITE SINGLE VALUE ******************* """
    """ ******************************************************* """
    async def writeValue(self, group, key, value):
        # We write single holding register
        _LOGGER.debug("Writing value: %s - %s - %s", group, key, value)
        scaledVal = round(value/self.Datapoints[group][key].Scaling)
        scaledVal = self.twos_complement(scaledVal)
        response = self._client.write_register(self.Datapoints[group][key].Address, scaledVal, self._slave_id)
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            self.Datapoints[group][key].Value = value
