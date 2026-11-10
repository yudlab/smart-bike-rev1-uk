import unittest
from firmware.pico.core import WheelSensor, Lighting, ParkingLock, Alarm

class CoreTests(unittest.TestCase):
    def test_speed_distance_bounce(self):
        w = WheelSensor(2100)
        self.assertTrue(w.pulse(0)); self.assertFalse(w.pulse(2))
        w.pulse(1000)
        self.assertAlmostEqual(w.speed(1000), 7.56)
        self.assertAlmostEqual(w.speed(1000, True), 7.56/1.609344)
        self.assertEqual(w.distance_mm, 4200)
        self.assertEqual(w.speed(5000), 0)
    def test_calibration(self):
        w = WheelSensor()
        for args in [(0,1),(2100,0),(2100,1.5),(float('nan'),1)]:
            with self.assertRaises(ValueError): w.configure(*args)
        w.configure(2200,2); w.pulse(0); w.pulse(1000)
        self.assertAlmostEqual(w.speed(1000),3.96)
    def test_indicators_and_brake(self):
        l = Lighting(); l.turn = 'right'; l.brake = True
        self.assertTrue(l.outputs(0)['front_right'])
        self.assertEqual(l.outputs(0)['front_right'],l.outputs(0)['rear_right'])
        self.assertFalse(l.outputs(500)['rear_right'])
        self.assertTrue(l.outputs(500)['brake'])
    def test_lock_never_connected(self):
        l = ParkingLock(); l.auto = True
        self.assertNotEqual(l.update(999999,True,True,True),'LOCK_REQUEST_ONLY')
    def test_lock_warn_cancel_and_rearm(self):
        l = ParkingLock(); l.auto = True; l.heartbeat(0)
        self.assertEqual(l.update(5000,True,True,True),'WARNING')
        self.assertEqual(l.update(15000,True,True,True),'LOCK_REQUEST_ONLY')
        self.assertEqual(l.update(15001,False,True,True),'INHIBITED')
        self.assertEqual(l.update(15002,True,True,True),'WARNING')
        l.heartbeat(16000)
        self.assertEqual(l.state,'UNLOCKED')
    def test_lock_fault_inhibits(self):
        for permitted in [(False,True,True),(True,False,True),(True,True,False)]:
            l = ParkingLock(); l.auto = True; l.heartbeat(0)
            self.assertEqual(l.update(20000,*permitted),'INHIBITED')
    def test_alarm_bounded(self):
        a = Alarm(); a.trigger(0); self.assertFalse(a.active(0))
        a.trigger(0,True); self.assertTrue(a.active(100)); self.assertFalse(a.active(2000))
if __name__ == '__main__': unittest.main()
