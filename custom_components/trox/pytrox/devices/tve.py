import logging

from ..trox import ModbusDatapoint
from ..trox import ModbusGroup

_LOGGER = logging.getLogger(__name__)

class TVE:
  def __init__(self):
    self.Datapoints = {}

    # Read / Write - Holding registers
    self.Datapoints[ModbusGroup.COMMANDS] = {
      "Setpoint": ModbusDatapoint(0, 0.01),
      "Override": ModbusDatapoint(1),
      "Command": ModbusDatapoint(2),
    }

    self.Datapoints[ModbusGroup.SENSORS] = {
      "Position": ModbusDatapoint(4, 0.01),
      "Position_Deg": ModbusDatapoint(5),
      "Flowrate_Percent": ModbusDatapoint(6, 0.01),
      "Flowrate_Actual": ModbusDatapoint(7, 0.01),
      "Analog_SP": ModbusDatapoint(8, 0.001),
    }

    # Device info - Read only
    self.Datapoints[ModbusGroup.DEVICE_INFO] = {
      "FW": ModbusDatapoint(103),
      "Status": ModbusDatapoint(104),
    }

    # Configuration parameters - R/W
    self.Datapoints[ModbusGroup.CONFIG] = {
        "105 Q Min Percent": ModbusDatapoint(105),
        "106 Q Max Percent": ModbusDatapoint(106),
        "108 Action on Bus Timeout": ModbusDatapoint(108),
        "109 Bus Timeout": ModbusDatapoint(109),
        "120 Q Min": ModbusDatapoint(120),
        "121 Q Max": ModbusDatapoint(121),
        "130 Modbus Address": ModbusDatapoint(130),
        "201 Volume Flow Unit": ModbusDatapoint(201),
        "231 Adjustment Mode": ModbusDatapoint(231),
        "568 Modbus Parameters": ModbusDatapoint(568),
        "569 Modbus Response Delay": ModbusDatapoint(569),
        "572 Switching Threshold": ModbusDatapoint(572),
    }

    _LOGGER.debug("Loaded datapoints for Trox TVE")