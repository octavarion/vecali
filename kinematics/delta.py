import math
import numpy as np
if __name__ == '__main__':
    import time
    from main import Kinematics
else:
    from . import Kinematics
from scipy.optimize import minimize


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
    def __init__(self, rod_length, radius, endstop_offset, effector_radius=34.0):
        self.rod_length = rod_length
        self.radius = np.array(radius)
        self.effector_radius = effector_radius
        self.endstop_offset = np.array(endstop_offset)
        self.towers = [(math.sin(a*math.pi)*r, math.cos(a*math.pi)*r) for a, r in zip(np.linspace(-2/3, 2/3, 3), self.radius+self.effector_radius)]

    def reverse(self, point):
        px, py, pz = point
        point = np.array(point)
        points = [np.array((math.sin(a*math.pi)*r+px, math.cos(a*math.pi)*r+py)) for a, r in zip(np.linspace(-2/3, 2/3, 3), [self.effector_radius]*3)]
        distance = [np.linalg.norm(t - p) for p, t in zip(points, self.towers)]
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
        initial = trilateration(centers.transpose(), np.array(self.rod_length))

        def func(params):
            px, py, pz = params
            points = [np.array((math.sin(a * math.pi) * r + px, math.cos(a * math.pi) * r + py, pz)) for a, r in
                      zip(np.linspace(-2 / 3, 2 / 3, 3), [self.effector_radius] * 3)]

            err = np.array([np.linalg.norm(np.subtract(p, c))-r for p, c, r in zip(points, centers, self.rod_length)])
            return sum(err**2)

        result = minimize(func, initial, method='SLSQP', tol=1e-10)
        return result.x

if __name__ == '__main__':
    k1 = DeltaKinematics([190]*3, [84]*3, [0*3])
    k2 = DeltaKinematics([190] * 3, [84.5] * 3, [0 * 3])

    x = k1.reverse((10.8, 5.0006, 8))
    t1 = time.perf_counter()
    val = k2.forward(x)
    t2 = time.perf_counter()
    print(t2 - t1)
    print(val)