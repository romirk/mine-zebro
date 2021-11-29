
import RPi.GPIO as gpio
import time

LED_PIN=18 #gpio18, connected to breakout "3"


LED_HEAT=[
    -1/40,  #power 0 - cool down in 30s from max temp
    -1/60,  #power 1
    -1/80,  #power 2
    -1/90,  #power 3 - slowly cool down in 1m30
        0,  #power 4
     1/25,  #power 5 - max for 25s
     1/22,  #power 6
     1/18,  #power 7
     1/15,  #power 8 - max for 12s
     1/12,  #power 9
     1/10   #power 10 - max for 10s
]

gpio.setmode(gpio.BCM)

class LEDs:
    def __init__(self):
        self.power=0#0 off, 1 for 300mA, 4 for 1200mA
        self.cooldown=0#once this reaches 1, the system needs to cool down a bit
        self.t=time.time()

        gpio.setup(LED_PIN,gpio.OUT)
        self.pwm=gpio.PWM(LED_PIN,10000)

    def start(self):
        self.pwm.start(0)
    def stop(self):
        self.pwm.stop()
        
    def set_power(self,power):
        self.update_cooldown()

        power=max(0,min(100,power))
        
        self.power=power
        self.pwm.ChangeDutyCycle(self.power)
        
        self.keep_safe() #disallow strong heat when suspecting overheated LEDs

    def update_cooldown(self):
        t=time.time()
        self.cooldown+=LED_HEAT[round(self.power/10)]*(t-self.t)
        self.t=t

        self.cooldown=max(0,self.cooldown)


    def keep_safe(self):
        self.update_cooldown()
        if self.power>1 and self.cooldown>=1:
            self.set_power(1)
            return True
        return False

if __name__=="__main__":
    lights=LEDs()
    lights.start()
    try:
        while True:
            for p in [0,1,10,100]:
                while lights.cooldown>0.7:
                    lights.set_power(0)
                    print("cooldown",lights.cooldown)
                    time.sleep(10)
                print("power",p,"cooldown",lights.cooldown)
                lights.set_power(p)
                time.sleep(1)
    except KeyboardInterrupt:
        lights.stop()
