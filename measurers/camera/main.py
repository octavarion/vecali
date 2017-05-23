from typing import Iterable

from firmwares import Firmware
from kinematics.main import Position
from measurers import Measurer


class GridReader(object):
    def __init__(self, device_index, grid_size):
        pass


class CameraMeasurer(Measurer):
    def __init__(self, firmware: Firmware, reader: GridReader):
        if not hasattr(firmware, 'measure_z'):
            raise Exception('Firmware does not support Z-probing')
        self.__firmware = firmware
        self.__reader = reader

    def measure_z(self, positions: Iterable[Position]):
        measures = self.__firmware.measure_z(position)

    def measure_xy(self, positions: Iterable[Position]):
        pass

    def measure_xyz(self, position: Iterable[Position]):
        pass
