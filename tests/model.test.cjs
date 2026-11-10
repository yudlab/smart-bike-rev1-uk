const test=require('node:test'),assert=require('node:assert/strict'),Bike=require('../web/model.js');
test('speed units, bounce and trip',()=>{const b=new Bike();b.pulse();b.pulse();b.tick(1000);b.pulse();assert.equal(b.speed,7.56);assert.equal(b.pulses,2);assert.equal(b.rejected,1);assert.equal(b.trip,.0042);});
test('moving and unhealthy lock requests denied',()=>{const b=new Bike();assert.equal(b.requestLock(),false);b.parked=b.still=true;b.sensor=false;assert.equal(b.requestLock(),false);b.sensor=true;b.speed=2;assert.equal(b.requestLock(),false);});
test('disconnect warns only when parked then cancels on motion',()=>{const b=new Bike();b.auto=true;b.peer=false;b.parked=b.still=true;b.tick(5000);assert.equal(b.lock,'WARNING');b.tick(10000);assert.equal(b.lock,'REQUEST ONLY');b.speed=5;b.tick(1);assert.equal(b.lock,'INHIBITED');});
test('invalid calibration rejected',()=>{const b=new Bike();assert.throws(()=>b.calibrate(NaN,1));assert.throws(()=>b.calibrate(2100,0));});

test('returning heartbeat clears a pending automatic request',()=>{const b=new Bike();b.auto=true;b.peer=false;b.parked=b.still=true;b.tick(5000);b.tick(10000);b.peer=true;b.tick(50);assert.equal(b.lock,'UNLOCKED');});
