from calibrators import MinimizationCalibrator
from firmwares import MarlinFirmware
from kinematics import DeltaKinematics
from measurers.camera import CameraMeasurer, GridReader


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

with SerialMock('/dev/ttyUSB0', baudrate=250000) as port:
    firmware = MarlinFirmware(port)
    reader = GridReader(device_index=0, grid_size=5)
    measurer = CameraMeasurer(firmware, reader)

    parameters = firmware.parameters
    # kinematics = DeltaKinematics(parameters.rod_length,
    #                              parameters.radius,
    #                              parameters.endstops)
    calibrator = MinimizationCalibrator(measurer, DeltaKinematics, [])

    result = calibrator.calibrate()
    level = -1
    for step in result:
        if step.value == 0:
            level += 1

        print('\t'*level + f'{step.description}: {step.value*100}%')

        if step.completed:
            level -= 1
    print(result.value)
