from typing import Iterable

from firmwares import Firmware
from kinematics.main import Position
from measurers import Measurer


class GridReader(object):
    def __init__(self, device_index, grid_size):
        pass


class CameraMeasurer(Measurer):
    @property
    def available_positions(self) -> Iterable[Position]:
        raise NotImplementedError()

    def __init__(self, firmware: Firmware, reader: GridReader, probe_offset=[0, 0]):
        if not hasattr(firmware, 'measure_z'):
            raise Exception('Firmware does not support Z-probing')
        self.__firmware = firmware
        self.__reader = reader
        self.__probe_offset = probe_offset

    def measure_z(self, positions: Iterable[Position]):
        measures = [self.__firmware.measure_z(position) for position in positions]
        offset = self.__probe_offset
        measures = [(x+offset[0], y+offset[1], z) for x, y, z in measures]
        return measures

    def measure_xy(self, positions: Iterable[Position]):
        raise NotImplementedError()

    def measure_xyz(self, position: Iterable[Position]):
        raise NotImplementedError()
