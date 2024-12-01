import logging

from ..trox import Modbus_Datapoint
from ..trox import COMMANDS,DEVICE_INFO,SENSORS

_LOGGER = logging.getLogger(__name__)

class TVE:
    def __init__(self):
        self.Datapoints = {}

        # Read / Write - Holding registers
        self.Datapoints[COMMANDS] = {}
        self.Datapoints[COMMANDS]["Setpoint"] = Modbus_Datapoint(0, 0.01)
        self.Datapoints[COMMANDS]["Override"] = Modbus_Datapoint(1)
        self.Datapoints[COMMANDS]["Command"] = Modbus_Datapoint(2)


        # Read only - Holding registers
        self.Datapoints[SENSORS] = {}
        self.Datapoints[SENSORS]["Position"] = Modbus_Datapoint(4, 0.01)
        self.Datapoints[SENSORS]["Position_Deg"] = Modbus_Datapoint(5)
        self.Datapoints[SENSORS]["Flowrate_Percent"] = Modbus_Datapoint(6, 0.01)
        self.Datapoints[SENSORS]["Flowrate_Flow"] = Modbus_Datapoint(7, 0.01)
        self.Datapoints[SENSORS]["Analog_SP"] = Modbus_Datapoint(8, 0.001)

        # Read only - Input registers
        self.Datapoints[DEVICE_INFO] = {}
        self.Datapoints[DEVICE_INFO]["FW"] = Modbus_Datapoint(103)
        self.Datapoints[DEVICE_INFO]["Status"] = Modbus_Datapoint(104)
        self.Datapoints[DEVICE_INFO]["Limit_Low"] = Modbus_Datapoint(105)
        self.Datapoints[DEVICE_INFO]["Limit_High"] = Modbus_Datapoint(106)
        self.Datapoints[DEVICE_INFO]["Dummy"] = Modbus_Datapoint(107)
        self.Datapoints[DEVICE_INFO]["Action_Bus_Timeout"] = Modbus_Datapoint(108)

        _LOGGER.debug("Loaded datapoints for Trox TVE")