import logging
from .firmware import Firmware, DeltaParameters
from kinematics.main import Position
import numpy as np
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


def _read_param(text, command, param):
    m = re.search(f'{command}.+?{param}(?P<value>[^\s]+)', text)
    return m.group('value')


class MarlinDeltaParameters(DeltaParameters):
    def __init__(self, firmware):
        self.__firmware = firmware
        # TODO initialize delta parameters from eeprom
        text = self.__firmware.send('M501')
        self.__radius = [float(_read_param(text, 'M665', 'R'))]

        rod_length = float(_read_param(text, 'M665', 'L'))
        trim_a = float(_read_param(text, 'M665', 'A'))
        trim_b = float(_read_param(text, 'M665', 'B'))
        trim_c = float(_read_param(text, 'M665', 'C'))
        self.__rod_length = [rod_length+trim_a, rod_length+trim_c, rod_length+trim_b]

        self.__endstops = [
            float(_read_param(text, 'M666', 'X')),
            float(_read_param(text, 'M666', 'Z')),
            float(_read_param(text, 'M666', 'Y'))
        ]

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        self.__radius = round(value, 3)
        self.__firmware.send(f'M665 R{self.__radius}')

    @property
    def endstops(self):
        return self.__endstops

    @endstops.setter
    def endstops(self, value):
        self.__endstops = np.round(value, 3)
        self.__firmware.send(f'M666 X{self.__endstops[0]} Y{self.__endstops[2]} Z{self.__endstops[1]}')

    @property
    def rod_length(self):
        return self.__rod_length

    @rod_length.setter
    def rod_length(self, value):
        self.__rod_length = np.round(value, 3)
        rod_max = max(self.__rod_length)
        trim_a = self.__rod_length[0] - rod_max
        trim_b = self.__rod_length[2] - rod_max
        trim_c = self.__rod_length[1] - rod_max
        self.__firmware.send(f'M666 L{rod_max} A{trim_a} B{trim_b} C{trim_c}')


class MarlinFirmware(Firmware):
    @property
    def parameters(self):
        return self.__parameters

    _position = None

    def __init__(self, serial_writer):
        self._sender = GCodeSender(serial_writer)
        self.__parameters = MarlinDeltaParameters(self)
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
        self.position = position
        return x, y, z
