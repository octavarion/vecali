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

    def _generate_points(self, radiuses, scale=False):
        mR = radiuses[-1]
        R = mR * self.__reader.grid_size
        a = 2*R * np.sin(np.pi/(6))
        r = a/2 * (1/np.tan(np.pi/(6)))
        ratio = ((r/R) * 0.9) if scale else 1
        print(f'ratio: {ratio}')
        for i in radiuses:
            if i == 0:
                yield (0, 0)
            else:
                for a in np.linspace(0, 2 * np.pi, num=6, endpoint=False):
                    l = i * self.__reader.grid_size * ratio
                    x, y = (l * np.cos(a + self.__phase), l * np.sin(a + self.__phase))
                    yield x, y

    def get_points(self, scale=False):
        return self._generate_points(range(0, int(self.__reader.max_radius/self.__reader.grid_size)+1), scale=scale)

    def get_outline(self, scale=False):
        return self._generate_points([int(self.__reader.max_radius/self.__reader.grid_size)], scale=scale)

    def measure_z(self, outline=False):
        points = list(self.get_points() if not outline else self.get_outline())
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

        self.__firmware.position = Position(x=0, y=0)
        yield task.complete()

        measurements2 = None
        if not outline:
            x = [x for x, y, z in measurements]
            y = [y for x, y, z in measurements]
            z = [z for x, y, z in measurements]
            f = Rbf(x, y, z, function='cubic', smooth=0)

            scaled_points = list(self.get_points(scale=True) if not outline else self.get_outline(scale=True))
            measurements2 = [(sp[0], sp[1], f(*sp)) for sp in scaled_points]

        return measurements, measurements2

    def measure_xy(self, outline=False):
        raise NotImplementedError()

    def measure_xyz(self, outline=False):
        raise NotImplementedError()
