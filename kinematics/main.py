from abc import ABC, abstractmethod
from collections import namedtuple

PositionBase = namedtuple('PositionBase', ['x', 'y', 'z', 'speed'])
PositionBase.__new__.__defaults__ = (None,) * len(PositionBase._fields)


class Position(PositionBase):
    _params = {'x': 'X', 'y': 'Y', 'z': 'Z', 'speed': 'F'}

    def to_gcode(self):
        gcode_elements = []
        for k, v in self._asdict().items():
            if v is None:
                continue
            gcode_elements.append(f'{self._params[k]}{v}')

        return ' '.join(gcode_elements)


class Kinematics(ABC):
    @abstractmethod
    def reverse(self, point): pass

    @abstractmethod
    def forward(self, x): pass
