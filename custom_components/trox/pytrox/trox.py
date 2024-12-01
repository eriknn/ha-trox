from dataclasses import dataclass

import logging

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)

@dataclass
class Modbus_Datapoint:
    Address: int
    Scaling: float = 1
    Value: float = 0

# ENUMS FOR GROUPS
COMMANDS = "Commands"
DEVICE_INFO = "Device_Info"
SENSORS = "Sensors"

MODE_INPUT = 3
MODE_HOLDING = 4

class Trox():
    def __init__(self, device_module:str, host:str, port:int, slave_id:int):
        self._client = ModbusTcpClient(host, port)
        self._slave_id = slave_id
        self._device_model = device_module

        # Load correct datapoints
        self.load_datapoints()


    def getModelName(self):
        return self._device_model
    
    def getFW(self):
        return self.Datapoints[DEVICE_INFO]["FW"].Value

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

    def getMode(self, group) -> int:
        # Used to determine if a group is holding registers or input registers
        return MODE_HOLDING    

    """ ******************************************************* """
    """ **************** READ GROUP OF VALUES ***************** """
    """ ******************************************************* """
    async def readCommands(self):
        await self.readGroup(COMMANDS)

    async def readDeviceInfo(self):
        await self.readGroup(DEVICE_INFO)

    async def readSensors(self):
        await self.readGroup(SENSORS)

    """ ******************************************************* """
    """ ******************** READ GROUP *********************** """
    """ ******************************************************* """
    async def readGroup(self, group):
        # We read multiple registers in one message
        _LOGGER.debug("Reading group: %s", group)
        n_reg = len(self.Datapoints[group])
        first_key = next(iter(self.Datapoints[group]))
        first_address = self.Datapoints[group][first_key].Address
        mode = self.getMode(group)     
        if mode == MODE_INPUT:
            response = self._client.read_input_registers(first_address,n_reg,self._slave_id)
        elif mode == MODE_HOLDING:
            response = self._client.read_holding_registers(first_address,n_reg,self._slave_id) 
            
        if response.isError():
            _LOGGER.debug("Error: %s", response)
            raise ModbusException('{}'.format(response))
        else:
            _LOGGER.debug("Success 1")
            for (dataPointName, data), newVal in zip(self.Datapoints[group].items(), response.registers):
                _LOGGER.debug("Success 2")
                newVal_2 = self.twos_complement(newVal)
                _LOGGER.debug("Success 3")
                if data.Scaling == 1.0:
                    _LOGGER.debug("Success 4")
                    data.Value = newVal_2
                else:
                    _LOGGER.debug("Success 5")
                    data.Value = newVal_2 * data.Scaling
                
    """ ******************************************************* """
    """ **************** READ SINGLE VALUE ******************** """
    """ ******************************************************* """
    async def readValue(self, group, key):
        # We read single register
        _LOGGER.debug("Reading value: %s - %s", group, key)

        mode = self.getMode(group)
        if mode == MODE_INPUT:
            response = self._client.read_input_registers(self.Datapoints[group][key].Address,1,self._slave_id)
        elif mode == MODE_HOLDING:
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
