"""MicroPython breadboard input demo. No high-current or lock outputs."""
from machine import Pin, UART
from time import ticks_ms, ticks_diff, sleep_ms
import json
import sys
import select

BENCH_LED_OUTPUTS = False  # Only resistor-limited LEDs on GP17/18
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
        self.test_side = 'off'
        self.test_started = 0
        self.command_errors = 0
        self.command_buffer = ''
        self.poller = select.poll()
        self.poller.register(sys.stdin, select.POLLIN)
        self.led_left = Pin(17, Pin.OUT, value=0) if BENCH_LED_OUTPUTS else None
        self.led_right = Pin(18, Pin.OUT, value=0) if BENCH_LED_OUTPUTS else None

    def read_commands(self, now):
        for _ in range(64):
            if not self.poller.poll(0):
                break
            ch = sys.stdin.read(1)
            if ch == '\n':
                try:
                    command = json.loads(self.command_buffer)
                    if command.get('cmd') == 'stop_test':
                        self.test_side = 'off'
                        print(json.dumps(dict(type='ack', ok=True, result='stopped')))
                    elif (command.get('cmd') == 'test_indicator'
                          and command.get('side') in ('left', 'right', 'hazard')
                          and command.get('duration_ms') == 10000):
                        self.test_side = command['side']
                        self.test_started = now
                        print(json.dumps(dict(type='ack', ok=True, result='test_started')))
                    else:
                        self.command_errors += 1
                        print(json.dumps(dict(type='ack', ok=False, result='unsupported')))
                except (ValueError, TypeError, AttributeError):
                    self.command_errors += 1
                    print(json.dumps(dict(type='ack', ok=False, result='bad_json')))
                self.command_buffer = ''
            elif len(self.command_buffer) < 256:
                self.command_buffer += ch
            else:
                self.command_buffer = ''
                self.command_errors += 1
    def run(self):
        while True:
            now = self.clock.update()
            value = self.reed.value()
            if self.previous and not value:
                self.wheel.pulse(now)
            self.previous = value
            self.lights.brake = not self.brake.value()
            left, right = not self.left.value(), not self.right.value()
            self.read_commands(now)
            if self.test_side != 'off' and now - self.test_started >= 10000:
                self.test_side = 'off'
            physical_turn = 'hazard' if left and right else 'left' if left else 'right' if right else 'off'
            self.lights.turn = self.test_side if self.test_side != 'off' else physical_turn
            outputs = self.lights.outputs(now)
            if self.led_left:
                self.led_left.value(int(outputs['front_left']))
                self.led_right.value(int(outputs['front_right']))
            if now - self.last_report >= 250:
                self.seq += 1
                data = dict(v=1, seq=self.seq, ms=now, kmh=self.wheel.speed(now),
                            trip_mm=self.wheel.distance_mm, rejected=self.wheel.rejected,
                            outputs=outputs, mode='BENCH_ONLY',
                            input_reed=value, input_brake=int(not self.brake.value()),
                            input_left=int(left), input_right=int(right),
                            test_side=self.test_side,
                            test_remaining_ms=max(0, 10000-(now-self.test_started)) if self.test_side != 'off' else 0,
                            bench_led_outputs=BENCH_LED_OUTPUTS, command_errors=self.command_errors)
                line = json.dumps(data) + '\n'
                print(line, end='')
                self.uart.write(line)
                self.last_report = now
            sleep_ms(1)

Bike().run()
