import time

LED_PIN=18 #gpio18, connected to breakout "3"


LED_HEAT=[
    -1/40,  #power 0 - cool down in 30s from max temp
    -1/90,  #power 1 - slowly cool down in 1m30
     1/25,  #power 2 - max for 25s
     1/15,  #power 3 - max for 12s
     1/10   #power 4 - max for 10s
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
        
    def set_power(self, power):
        self.update_cooldown()

        self.pwm.changeDutyCycle(25*self.power)
        self.update_cooldown() #disallow strong heat when suspecting overheated LEDs

    def update_cooldown(self):
        t=time.time()
        self.cooldown+=LED_HEAT[self.power]*(t-self.t)
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
            if lights.cooldown>0.7:
                time.sleep(10)
            for p in range(5):
                lights.power(p)
                time.sleep(1)
    except KeyboardInterrupt:
        lights.stop()
