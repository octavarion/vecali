import math
import numpy as np
from . import Kinematics


def unit(v):
    return v / np.linalg.norm(v)


def trilateration(p, r):
    P1 = p[:, 0]
    P2 = p[:, 1]
    P3 = p[:, 2]

    ex = (P2 - P1) / np.linalg.norm(P2 - P1)
    i = np.dot(ex, P3 - P1)
    ey = (P3 - P1 - i*ex) / np.linalg.norm(P3 - P1 - i*ex)
    ez = np.cross(ex, ey)

    d = np.linalg.norm(P2 - P1)
    j = np.dot(ey, P3 - P1)

    x = (r[0]**2 - r[1]**2 + d**2) / (2*d)
    y = (r[0]**2 - r[2]**2 + i**2 + j**2) / (2*j) - ((i/j)*x)
    z = np.sqrt(r[0]**2 - x**2 - y**2)
    triPt = P1 + x*ex + y*ey + z*ez
    return [round(i, 2) for i in triPt]


class DeltaKinematics(Kinematics):
    def __init__(self, rod_length, radius, endstop_offset):
        self.rod_length = rod_length
        self.radius = radius
        self.endstop_offset = np.array(endstop_offset)
        self.towers = [(math.sin(a*math.pi)*r, math.cos(a*math.pi)*r) for a, r in zip(np.linspace(-2/3, 2/3, 3), self.radius)]

    def reverse(self, point):
        point = np.array(point)
        distance = [np.linalg.norm(t - point[:-1]) for t in self.towers]
        try:
            # print(f'rod_length: {self.rod_length} distance: {distance}')
            h = [math.sqrt(r**2 - d**2) + point[-1] for r, d in zip(self.rod_length, distance)]
            return list(np.array(h) + self.endstop_offset)
        except ValueError as e:
            print(self.rod_length)
            print(distance)
            raise e

    def forward(self, x):
        carriage_position = np.array(x) + self.endstop_offset
        centers = np.array([t + (p,) for t, p in zip(self.towers, carriage_position)])
        result = trilateration(centers.transpose(), np.array(self.rod_length))
        return result
