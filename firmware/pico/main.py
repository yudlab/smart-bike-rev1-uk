"""MicroPython breadboard input demo. No high-current or lock outputs."""
from machine import Pin, UART
from time import ticks_ms, ticks_diff, sleep_ms
import json
from core import WheelSensor, Lighting

class Clock:
    def __init__(self):
        self.previous = ticks_ms()
        self.now = 0
    def update(self):
        current = ticks_ms()
        self.now += ticks_diff(current, self.previous)
        self.previous = current
        return self.now

class Bike:
    def __init__(self):
        self.clock = Clock()
        self.wheel = WheelSensor()
        self.lights = Lighting()
        self.reed = Pin(2, Pin.IN, Pin.PULL_UP)
        self.brake = Pin(3, Pin.IN, Pin.PULL_UP)
        self.left = Pin(4, Pin.IN, Pin.PULL_UP)
        self.right = Pin(5, Pin.IN, Pin.PULL_UP)
        self.uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
        self.previous = 1
        self.last_report = 0
        self.seq = 0
    def run(self):
        while True:
            now = self.clock.update()
            value = self.reed.value()
            if self.previous and not value:
                self.wheel.pulse(now)
            self.previous = value
            self.lights.brake = not self.brake.value()
            left, right = not self.left.value(), not self.right.value()
            self.lights.turn = 'hazard' if left and right else 'left' if left else 'right' if right else 'off'
            if now - self.last_report >= 250:
                self.seq += 1
                data = dict(v=1, seq=self.seq, ms=now, kmh=self.wheel.speed(now),
                            trip_mm=self.wheel.distance_mm, rejected=self.wheel.rejected,
                            outputs=self.lights.outputs(now), mode='INPUT_ONLY')
                self.uart.write(json.dumps(data) + '\n')
                self.last_report = now
            sleep_ms(1)

Bike().run()
