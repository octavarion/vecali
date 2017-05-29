from typing import Iterable, Generator
import numpy as np
import math
from scipy.interpolate import interp2d, Rbf
from itertools import count
from firmwares import Firmware
from kinematics.main import Position
from measurers import Measurer
from measurers.main import Point

from tasking import TaskProgress


def _get_outline(positions: Iterable[Position]) -> Iterable[Position]:
    return positions


class GridReader(object):
    def __init__(self, device_index, grid_size, max_radius):
        self.__device_index = device_index
        self.grid_size = grid_size
        self.max_radius = max_radius

        self.grid_rotation = 0


class CameraMeasurer(Measurer):
    __speed = 2000
    __phase = np.pi/2

    def __init__(self, firmware: Firmware, reader: GridReader, camera_height, probe_offset=None):
        if probe_offset is None:
            probe_offset = [0, 0]
        if not hasattr(firmware, 'measure_z'):
            raise Exception('Firmware does not support Z-probing')
        self.__firmware = firmware
        self.__reader = reader
        self.__probe_offset = probe_offset
        self.__height = camera_height

        self.__phase += self.__reader.grid_rotation

        self.__bed_plane = self._get_bed_plane()

    def _generate_points(self, radiuses):
        for i in radiuses:
            if i == 0:
                yield (0, 0)
            else:
                for a in np.linspace(0, 2 * np.pi, num=6*i, endpoint=False):
                    l = i * self.__reader.grid_size
                    x, y = (l * np.cos(a + self.__phase), l * np.sin(a + self.__phase))
                    yield x, y

    def _get_points(self):
        return self._generate_points(range(0, int(self.__reader.max_radius/self.__reader.grid_size)+1))

    def _get_outline(self):
        return self._generate_points([int(self.__reader.max_radius/self.__reader.grid_size)])

    def _get_bed_plane(self):
        points = self._get_outline()
        positions = [Position(x=x, y=y, z=self.__height, speed=2000) for x, y in points]
        measurements = [self.__firmware.measure_z(p) for p in positions]
        A = np.matrix([[x, y]] for x, y, _ in measurements)
        b = [z for _, _, z in measurements]
        x = np.linalg.lstsq(A, b)
        return x

    def measure_z(self, outline=False):
        points = list(self._get_points() if not outline else self._get_outline())
        task = TaskProgress('Measuring bed (z-only)', total=len(points))
        yield task.begin()

        self.__firmware.home()

        offset = self.__probe_offset
        measurements = []
        for x, y in points:
            position = Position(x=x, y=y, z=self.__height, speed=self.__speed)
            x, y, z = self.__firmware.measure_z(position)
            measurements.append((x + offset[0], y + offset[1], z))
            yield task.progress()

        measurements = []

        self.__firmware.position = Position(x=0, y=0)
        yield task.complete()

        return measurements

    def measure_xy(self, outline=False):
        raise NotImplementedError()

    def measure_xyz(self, outline=False):
        raise NotImplementedError()
