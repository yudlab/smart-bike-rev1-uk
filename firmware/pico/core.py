"""Portable domain logic: CPython tests and MicroPython. Times are monotonic ms."""
class WheelSensor:
    def __init__(self, circumference_mm=2100, magnets=1):
        self.configure(circumference_mm, magnets)
        self.last = None
        self.period = None
        self.distance_mm = 0
        self.rejected = 0

    def configure(self, circumference_mm, magnets=1):
        if not 500 <= circumference_mm <= 3500 or not isinstance(magnets, int) or not 1 <= magnets <= 8:
            raise ValueError('Invalid wheel calibration')
        self.circumference_mm = circumference_mm
        self.magnets = magnets
        self.last = None
        self.period = None

    def pulse(self, now):
        # 120 km/h plausibility ceiling; reject bounce without advancing timestamp.
        minimum = max(10, self.circumference_mm / self.magnets * 3.6 / 120)
        if self.last is not None and now - self.last < minimum:
            self.rejected += 1
            return False
        self.period = None if self.last is None or now - self.last > 10000 else now - self.last
        self.last = now
        self.distance_mm += self.circumference_mm / self.magnets
        return True

    def speed(self, now, mph=False):
        if self.period is None or self.last is None or now - self.last > max(3000, 2 * self.period):
            return 0.0
        kmh = self.circumference_mm / self.magnets * 3.6 / max(self.period, now - self.last)
        return kmh / 1.609344 if mph else kmh

class Lighting:
    def __init__(self):
        self.night = False
        self.main = False
        self.brake = False
        self.turn = 'off'
        self.backlight = 0.8

    def outputs(self, now):
        phase = now % 1000 < 500
        return dict(front_main=self.main, front_idle=self.night,
                    rear_idle=self.night, brake=self.brake,
                    front_left=phase and self.turn in ('left', 'hazard'),
                    rear_left=phase and self.turn in ('left', 'hazard'),
                    front_right=phase and self.turn in ('right', 'hazard'),
                    rear_right=phase and self.turn in ('right', 'hazard'),
                    backlight=self.backlight)

class ParkingLock:
    """REQUEST policy only. Never drives a solenoid. Independent interlock required."""
    def __init__(self):
        self.auto = False
        self.seen_peer = False
        self.last_peer = None
        self.warning_since = None
        self.state = 'UNLOCKED'

    def heartbeat(self, now):
        self.seen_peer = True
        self.last_peer = now
        self.warning_since = None
        self.state = 'UNLOCKED'

    def update(self, now, parked=False, independent_still=False, sensor_ok=False):
        permitted = parked and independent_still and sensor_ok
        lost = self.seen_peer and now - self.last_peer >= 5000
        if not self.auto or not permitted or not lost:
            self.warning_since = None
            self.state = 'INHIBITED' if lost else 'UNLOCKED'
        elif self.warning_since is None:
            self.warning_since = now
            self.state = 'WARNING'
        elif now - self.warning_since >= 10000:
            self.state = 'LOCK_REQUEST_ONLY'
        return self.state

class Alarm:
    def __init__(self):
        self.armed = False
        self.until = 0

    def trigger(self, now, bench_test=False):
        if self.armed or bench_test:
            self.until = now + 2000

    def active(self, now):
        return now < self.until
