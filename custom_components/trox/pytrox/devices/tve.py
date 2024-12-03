import logging

from ..modbusdevice import ModbusDatapoint, ModbusAccess, ModbusGroup

_LOGGER = logging.getLogger(__name__)

class TVE:
  def __init__(self):
    self.Datapoints = {}

    # COMMANDS - Read/Write
    self.Datapoints[ModbusGroup.COMMANDS] = {
        "Setpoint Flowrate": ModbusDatapoint(Address=0, Scaling=0.01, Access=ModbusAccess.RW),
        "Override": ModbusDatapoint(Address=1, Access=ModbusAccess.RW),
        "Command": ModbusDatapoint(Address=2, Access=ModbusAccess.RW),
    }

    # SENSORS - Read-only
    self.Datapoints[ModbusGroup.SENSORS] = {
        "Position": ModbusDatapoint(Address=4, Scaling=0.01, Access=ModbusAccess.R),
        "Position Degrees": ModbusDatapoint(Address=5, Access=ModbusAccess.R),
        "Flowrate Percent": ModbusDatapoint(Address=6, Scaling=0.01, Access=ModbusAccess.R),
        "Flowrate Actual": ModbusDatapoint(Address=7, Scaling=0.01, Access=ModbusAccess.R),
        "Analog Setpoint": ModbusDatapoint(Address=8, Scaling=0.001, Access=ModbusAccess.R),
    }

    # DEVICE_INFO - Read-only
    self.Datapoints[ModbusGroup.DEVICE_INFO] = {
        "FW": ModbusDatapoint(Address=103, Access=ModbusAccess.R),
        "Status": ModbusDatapoint(Address=104, Access=ModbusAccess.R),
    }

    # CONFIGURATION - Read/Write
    self.Datapoints[ModbusGroup.CONFIG] = {
        "105 Q Min Percent": ModbusDatapoint(Address=105, Access=ModbusAccess.RW),
        "106 Q Max Percent": ModbusDatapoint(Address=106, Access=ModbusAccess.RW),
        "108 Action on Bus Timeout": ModbusDatapoint(Address=108, Access=ModbusAccess.RW),
        "109 Bus Timeout": ModbusDatapoint(Address=109, Access=ModbusAccess.RW),
        "120 Q Min": ModbusDatapoint(Address=120, Access=ModbusAccess.RW),
        "121 Q Max": ModbusDatapoint(Address=121, Access=ModbusAccess.RW),
        "130 Modbus Address": ModbusDatapoint(Address=130, Access=ModbusAccess.RW),
        "201 Volume Flow Unit": ModbusDatapoint(Address=201, Access=ModbusAccess.RW),
        "231 Adjustment Mode": ModbusDatapoint(Address=231, Access=ModbusAccess.RW),
        "568 Modbus Parameters": ModbusDatapoint(Address=568, Access=ModbusAccess.RW),
        "569 Modbus Response Delay": ModbusDatapoint(Address=569, Access=ModbusAccess.RW),
        "572 Switching Threshold": ModbusDatapoint(Address=572, Access=ModbusAccess.RW),
    }

    _LOGGER.debug("Loaded datapoints for Trox TVE")