import machine
import time

from machine import Pin

def init():
    global led
    led = Pin("LED", Pin.OUT)
    
def di():
    led.on()
    time.sleep(0.1)
    led.off()
    time.sleep(0.2)

def dah():
    led.on()
    time.sleep(0.3)
    led.off()
    time.sleep(0.5)

def tick():
    #di()
    #di()
    #di()
    #dah()
    #dah()
    #dah()
    #di()
    #di()
    #di()
    led.toggle()
    time.sleep(2)