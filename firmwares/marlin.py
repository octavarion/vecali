import logging
from .firmware import Firmware, DeltaParameters
from kinematics.main import Position
import re
import time

logger = logging.getLogger(__name__)


class GCodeSender(object):
    def __init__(self, serial_writer):
        self.s = serial_writer
        time.sleep(4)
        self.send('M113 S0')

    def send(self, gcode):
        gcode += '\n'
        self.s.write(str.encode(gcode))
        command_output = ''
        while True:
            line = self.s.readline()
            if line == b'ok\n':
                break
            if line != b'':
                command_output += line.decode('utf-8')
        output = command_output.strip() if command_output != '' else None
        return output


class MarlinDeltaParameters(DeltaParameters):
    def __init__(self, firmware):
        self.__firmware = firmware
        # TODO initialize delta parameters from eeprom
        self.__radius = None

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        self.__radius = round(value, 3)
        self.__firmware.send(f'M665 R{self.__radius}')

    @property
    def endstops(self):
        return [0, 0, 0]

    @property
    def rod_length(self):
        return [194, 194, 194]


class MarlinFirmware(Firmware):
    @property
    def parameters(self):
        return self.__parameters

    _position = None

    def __init__(self, serial_writer):
        self.__parameters = MarlinDeltaParameters(self)
        self._sender = GCodeSender(serial_writer)
        super().__init__()

    def send(self, gcode):
        return self._sender.send(gcode)

    def home(self):
        self._sender.send('G28')
        self._position = Position(0, 0, None)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: Position):
        value = value.to_gcode()
        gcode = f'G1 {value}'
        self._sender.send(gcode)
        self._position = value

    def measure_z(self, position: Position):
        self.position = position
        line = self._sender.send('G30').split('\n')[0]
        m = re.search('X:\s+(?P<x>[-.\d]+)\s+Y:\s+(?P<y>[-.\d]+)\s+Z:\s+(?P<z>[-.\d]+)', line)
        x = position.x
        y = position.y
        z = float(m.group('z'))
        return x, y, z
