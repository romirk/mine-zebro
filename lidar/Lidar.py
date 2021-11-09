

from VL53L1X import VL53L1X
import RPi.GPIO as gpio

from time import sleep

class Lidar(VL53L1X):
    def __init__(self,bus,gpio,num):
        self.bus=bus
        self.num=num
        self.address=0x29
        self.gpio=gpio
        self.xshut_pin=self._xshut_pin()

        #code from library
        """Initialize the VL53L1X ToF Sensor from ST"""
        self._i2c_bus = 1#i2c_bus - 1 was used before, make sure this is the right one
        self.i2c_address = self.address#i2c_address
        self._tca9548a_num = 255#tca9548a_num
        self._tca9548a_addr = 0#tca9548a_addr

        self._i2c = self.bus#SMBus()
        #code to check for sensor moved to init

        self._dev = None
        # Register Address
        self.ADDR_UNIT_ID_HIGH = 0x16  # Serial number high byte
        self.ADDR_UNIT_ID_LOW = 0x17   # Serial number low byte
        self.ADDR_I2C_ID_HIGH = 0x18   # Write serial number high byte for I2C address unlock
        self.ADDR_I2C_ID_LOW = 0x19    # Write serial number low byte for I2C address unlock
        self.ADDR_I2C_SEC_ADDR = 0x8a  # Write new I2C address after unlock

        self.enabled=False

    def init(self):
        #check for proper sensor
        #for this, it needs to be on, so not disabled, but it should not be opened yet - neglect this now, see errors later
##        if self._tca9548a_num == 255:
##            try:
##                self._i2c.open(bus=self._i2c_bus)
##                self._i2c.read_byte_data(self.i2c_address, 0x00)
##            except IOError:
##                raise RuntimeError("VL53L1X not found on adddress: {:02x}".format(self.i2c_address))
##            finally:
##                self._i2c.close()

        self.enable()


    def disable(self):
        self.gpio.setup(self.xshut_pin, self.gpio.OUT, initial=self.gpio.LOW) #pull GPIO xshut low, reset address
        self.address=0x29
        self.i2c_address=self.address

        self.enabled=False
        
    def enable(self):
        self.gpio.setup(self.xshut_pin, self.gpio.IN, pull_up_down=self.gpio.PUD_OFF) #gpio to highZ to turn the chip on

        sleep(.010) #boot time should be <1.2ms
        
        #open channel,turn on reading
        self.open()

        #set address again;
        self.address=self._address()
        self.change_address(self.address)

        #start ranging
        self.start_ranging(1)#use short range for rover
        self.set_inter_measurement_period(100)#ms - lower frequency for lower power consumption

        self.enabled=True
        
    def read(self):
        if self.enabled:
            return self.get_distance()
        else:
            return None

    def _address(self):
        return {
            1:0x39,
            2:0x49,
            3:0x59,
            4:0x69,
            5:0x79
            }[self.num]
    
    def _xshut_pin(self): #xshut, shuts down chip when low. this restores the address to the default (0x29)
        return {
            1:27, #GPIO27
            2:22, #GPIO22
            3:18, #GPIO18
            4:23, #GPIO23
            5:24  #GPIO24
            }[self.num]
