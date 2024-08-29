#!/usr/bin/python

import time
import math
import smbus

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class Motor:

    # Registers/etc.
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD

    def __init__(self, address=0x40, debug=False, channel=0, min_pulse=500, max_pulse=2500, min_angle=0, max_angle=180, freq=50):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if (self.debug):
            print("Reseting PCA9685")
        self.write(self.__MODE1, 0x20)
        self.min_pulse, self.max_pulse, self.min_angle, self.max_angle, self.freq = min_pulse, max_pulse, min_angle, max_angle, freq
        self.channel = channel
        self.set_pwm_freq()
        self.reset()


    def __repr__(self) -> str:
        return f"Channel = {self.channel}\nFrequency = {self.freq} Hz"

    def write_block(self, reg, buffer):
        "Writes an Nx8-bit value to the specified register/address"
        self.bus.write_i2c_block_data(self.address, reg, buffer)
        # self.bus.write_byte_data(self.address, reg, value)
        if (self.debug):
            print("I2C: Write 0x%02X to register 0x%02X" % (buffer, reg))

    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if (self.debug):
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
	  
    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if (self.debug):
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result
	
    def set_pwm_freq(self):
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(self.freq)
        prescaleval -= 1.0
        if (self.debug):
            print("Setting PWM frequency to %d Hz" % self.freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def set_pwm(self, on, off):
        "Sets a single PWM channel"
        b_array = []
        b_array.append(on & 0xFF)
        b_array.append(on >> 8)
        b_array.append(off & 0xFF)
        b_array.append(off >> 8)

        self.write_block(self.__LED0_ON_L+4*self.channel, b_array)

        #self.write(self.__LED0_ON_L+4*self.channel, on & 0xFF)
        #self.write(self.__LED0_ON_H+4*self.channel, on >> 8)
        #self.write(self.__LED0_OFF_L+4*self.channel, off & 0xFF)
        #self.write(self.__LED0_OFF_H+4*self.channel, off >> 8)
        if (self.debug):
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (self.channel,on,off))
	  
    def set_servo_pulse(self, pulse):
        "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us
        self.set_pwm(0, int(pulse))

    def move_servo_by_angle(self, angle):
        "Moves the servo to a specified angle"
        # Convert the angle to pulse width
        pulse_width = self.min_pulse + (self.max_pulse - self.min_pulse) * ((angle-self.min_angle) / (self.max_angle-self.min_angle))
        self.set_servo_pulse(pulse_width)

    def reset(self):
        self.move_servo_by_angle(0)

class MotorsController:
    """
    This class Control 2 servo motors

    Description: This class will both servos
    First it will rotate the azimuth angle and then the pitch angle
    Adaptions were made to reach each point on the upper half of the sphere  

    Arguments:
        engine1   First engine to control.
        engine2   Second engine to control.
    """

    def __init__(self, channel1=0, channel2=1):
        """
        Initialize motors and put the system on point (0, 0, 0).
        """
        self.motor1 = Motor(min_angle=0, max_angle=180, channel=channel1, min_pulse=500, max_pulse=2500, freq=50)
        self.motor2 = Motor(min_angle=0, max_angle=180, channel=channel2, min_pulse=500, max_pulse=2500, freq=50)


    def __repr__(self):
        """
        Description: Prints system's info.
        """
        return f"Motor 1 status: {self.motor1}\nMotor 2 status: {self.motor2}"

    def default(self):
        """
        Description: This method reset the engines to point(0, 0, 0)
        """
        self.motor1.reset()
        self.motor2.reset()

    def run(self, azimuth: float, pitch: float) -> None:
        """
        Description: Change position of the system for both engines
        The engines are limited to maxium of 180 degrees and can't reach 360 degrees
        We adjusted the calculations so that we would cover the entire 360 degrees of the azimuth angle
        Drawing "imaginary" stright line from theta 45 degrees to 225 degrees we can adjust the pitch to reach the 225 degrees
        So we "Limited" the pitch to 90 degrees

        Arguments:
        alpha: float  Azimuth angle
        beta: float   Pitch angle
        """
        self.motor2.move_servo_by_angle(pitch)
        time.sleep(0.35)
        
        self.motor1.move_servo_by_angle(azimuth)
        time.sleep(0.35)


    def stop(self):
        self.motor2.set_pwm(0, 0)
        self.motor1.set_pwm(0, 0)


if __name__=='__main__':
 
     mcs = MotorsController(0, 1)
     for a in range(0, 181, 30):
         for b in range(0, 91, 15):
             mcs.run(a, b)
             print(f" a = {a}, b = {b}")
             #mcs.stop()