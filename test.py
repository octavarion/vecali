from calibrators import MinimizationCalibrator
from firmwares import MarlinFirmware
from kinematics import DeltaKinematics
from measurers.camera import CameraMeasurer, GridReader

from serial import Serial

import numpy as np
from scipy.interpolate import griddata
import matplotlib
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


def plot(X, Y, Z, num=None):
    fig = plt.figure()
    xi = np.linspace(np.min(X), np.max(X), 100)
    yi = np.linspace(np.min(Y), np.max(Y), 100)
    zi = griddata((X, Y), Z, (xi[None, :], yi[:, None]), method='cubic')
    cp = plt.contourf(xi, yi, zi)
    plt.colorbar(cp)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()
    # filename = f'fig{num}.png' if num is not None else 'fig.png'
    # fig.savefig(filename)


def plot_bed(bed_level, num=None):
    X, Y, Z = zip(*bed_level)
    plot(X, Y, Z, num)


class SerialMock(object):
    ok_line = b'ok\n'

    def __init__(self, port=None, baudrate=9000):
        self._lines = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def write(self, value):
        value = value.decode('utf-8')
        if value.startswith('M501'):
            self._lines = [
                b'M665 L194 R84 A0 B0 C0\n',
                b'M666 X0 Y0 Z0\n',
                self.ok_line
            ]
        if value.startswith('M113'):
            self._lines = [self.ok_line]

    def readline(self):
        if len(self._lines) == 0:
            return self.ok_line

        line = self._lines[0]
        self._lines = self._lines[1:]
        return line

with Serial('/dev/ttyUSB0', baudrate=250000) as port:
    firmware = MarlinFirmware(port)
    reader = GridReader(device_index=0, grid_size=5, max_radius=70)
    measurer = CameraMeasurer(firmware, reader, camera_height=124, probe_offset=[15.5, -3.5])

    parameters = firmware.parameters
    # kinematics = DeltaKinematics(parameters.rod_length,
    #                              parameters.radius,
    #                              parameters.endstops)
    calibrator = MinimizationCalibrator(measurer, DeltaKinematics, [])

    result = calibrator.calibrate()
    level = -1
    last_level = -1
    for step in result:
        last_level = level
        if step.value == 0:
            level += 1

        if type(step.value) == float or type(step.value) == int:
            start = '\r' if last_level == level else '\n'
            print(start + '\t'*level + f'{step.description}: {round(step.value, 4)*100}%', end='')
        else:
            # print('\n' + '\t'*level + str(step.value))
            plot_bed(step.value[0])
            plot_bed(step.value[1])

        if step.completed:
            level -= 1
    print('\n')
    print(result.value)
