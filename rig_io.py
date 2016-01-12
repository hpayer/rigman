import time
import smbus
import signal
import sys


class FakeBus(object):

    def write_byte_data(self, address, reg_mode1, reg_data):
        print 'FakeBus.write_byte_data:', address, reg_mode1, reg_data

try:
    bus = smbus.SMBus(1)  # /dev/i2c-1 (port I2C1) class
except OSError:
    bus = FakeBus()



class Rig_io():
    global bus

    def __init__(self):
        self.device_address = 0x20  # default for seeed relay board
        self.device_reg_mode1 = 0x06
        self.device_reg_data = 0xff  # note inverted logic - a set bit means output off
        # now initialise the io port
        bus.write_byte_data(self.device_address, self.device_reg_mode1, self.device_reg_data)

    def cl_on(self):
        self.device_reg_data &= ~(0x1 << 0)
        bus.write_byte_data(self.device_address, self.device_reg_mode1, self.device_reg_data)

    def cl_off(self):
        self.device_reg_data |= (0x1 << 0)
        bus.write_byte_data(self.device_address, self.device_reg_mode1, self.device_reg_data)

    def rec_on(self):
        self.device_reg_data &= ~(0x1 << 1)
        bus.write_byte_data(self.device_address, self.device_reg_mode1, self.device_reg_data)

    def rec_off(self):
        self.device_reg_data |= (0x1 << 1)
        bus.write_byte_data(self.device_address, self.device_reg_mode1, self.device_reg_data)

    def mv_all(self):
        """Switch with mv_step, was inversed with mv_all.
        """
    # def mv_step(self):
        self.device_reg_data &= ~(0x1 << 2)
        bus.write_byte_data(self.device_address, self.device_reg_mode1, self.device_reg_data)

    def mv_step(self):
        """
        Switch with mv_all, was inversed with mv_step.
        """
    # def mv_all(self):
        self.device_reg_data &= ~(0x1 << 3)
        bus.write_byte_data(self.device_address, self.device_reg_mode1, self.device_reg_data)

    def mv_idle(self):
        self.device_reg_data |= (0x3 << 2)
        bus.write_byte_data(self.device_address, self.device_reg_mode1, self.device_reg_data)

    # only for graceful exit
    def alloff(self):
        self.device_reg_data |= (0xf << 0)
        bus.write_byte_data(self.device_address, self.device_reg_mode1, self.device_reg_data)


if __name__ == "__main__":
    rig_io = Rig_io()


    # called on process interruption. set all pins to input default mode.
    def endProcess(signalnum=None, handler=None):
        rig_io.alloff()
        sys.exit()


    signal.signal(signal.SIGINT, endProcess)

    while True:
        ct = raw_input("Input: ")
        if ct == 'clon':
            rig_io.cl_on()
        elif ct == 'cloff':
            rig_io.cl_off()
        elif ct == 'recon':
            rig_io.rec_on()
        elif ct == 'recoff':
            rig_io.rec_off()
        elif ct == 'mvstep':
            rig_io.mv_step()
        elif ct == 'mvall':
            rig_io.mv_all()
        elif ct == 'mvidle':
            rig_io.mv_idle()
        elif ct == 'alloff':
            rig_io.alloff()
