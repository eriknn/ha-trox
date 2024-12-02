import logging

from ..trox import Modbus_Datapoint
from ..trox import COMMANDS,DEVICE_INFO,SENSORS,CONFIG

_LOGGER = logging.getLogger(__name__)

class TVE:
  def __init__(self):
    self.Datapoints = {}

    # Read / Write - Holding registers
    self.Datapoints[COMMANDS] = {
      "Setpoint": Modbus_Datapoint(0, 0.01),
      "Override": Modbus_Datapoint(1),
      "Command": Modbus_Datapoint(2),
    }

    self.Datapoints[SENSORS] = {
      "Position": Modbus_Datapoint(4, 0.01),
      "Position_Deg": Modbus_Datapoint(5),
      "Flowrate_Percent": Modbus_Datapoint(6, 0.01),
      "Flowrate_Actual": Modbus_Datapoint(7, 0.01),
      "Analog_SP": Modbus_Datapoint(8, 0.001),
    }

    # Device info - Read only
    self.Datapoints[DEVICE_INFO] = {
      "FW": Modbus_Datapoint(103),
      "Status": Modbus_Datapoint(104),
    }

    # Configuration parameters - R/W
    self.Datapoints[CONFIG] = {
        "105 Q Min Percent": Modbus_Datapoint(105),
        "106 Q Max Percent": Modbus_Datapoint(106),
        "108 Action on Bus Timeout": Modbus_Datapoint(108),
        "109 Bus Timeout": Modbus_Datapoint(109),
        "120 Q Min": Modbus_Datapoint(120),
        "121 Q Max": Modbus_Datapoint(121),
        "130 Modbus Address": Modbus_Datapoint(130),
        "201 Volume Flow Unit": Modbus_Datapoint(201),
        "231 Adjustment Mode": Modbus_Datapoint(231),
        "568 Modbus Parameters": Modbus_Datapoint(568),
        "569 Modbus Response Delay": Modbus_Datapoint(569),
        "572 Switching Threshold": Modbus_Datapoint(572),
    }

    _LOGGER.debug("Loaded datapoints for Trox TVE")