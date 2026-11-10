/* A simulator, deliberately with no hardware/network command transport. */
class BikeModel {
  constructor() {
    this.speed=0; this.trip=0; this.unit='km/h'; this.circumference=2100; this.magnets=1;
    this.night=false; this.main=false; this.brake=false; this.turn='off'; this.backlight=80;
    this.armed=false; this.sirenUntil=0; this.auto=false; this.peer=true; this.seen=true;
    this.lastPeer=0; this.parked=false; this.still=false; this.sensor=true;
    this.warning=null; this.lock='UNLOCKED'; this.time=0; this.lastPulse=null;
    this.pulses=0; this.rejected=0; this.gps=false; this.events=[];
  }
  log(message) { this.events.unshift(`${(this.time/1000).toFixed(1)}s  ${message}`); this.events.length=Math.min(80,this.events.length); }
  calibrate(mm,magnets) {
    if (!Number.isFinite(mm)||mm<500||mm>3500||!Number.isInteger(magnets)||magnets<1||magnets>8) throw Error('Use 500–3500 mm and 1–8 magnets.');
    this.circumference=mm; this.magnets=magnets; this.lastPulse=null; this.speed=0;
    this.log('Calibration saved for this simulation');
  }
  pulse() {
    const period=this.lastPulse===null?null:this.time-this.lastPulse;
    if(period!==null&&period<Math.max(10,this.circumference/this.magnets*3.6/120)){this.rejected++;return;}
    this.speed=period===null||period>10000?0:this.circumference/this.magnets*3.6/period;
    this.lastPulse=this.time;this.trip+=this.circumference/this.magnets/1e6;this.pulses++;
  }
  requestLock() {
    if (!this.parked||!this.still||!this.sensor||this.speed>0) {this.log('Lock inhibited: parked, independent stillness and healthy sensor required');return false;}
    this.lock='REQUEST ONLY';this.log('Simulated lock request — actuator disabled');return true;
  }
  tick(dt) {
    this.time+=dt;
    if(this.peer){this.lastPeer=this.time;this.seen=true;if(this.warning!==null){this.warning=null;this.lock='UNLOCKED';}}
    if(this.lastPulse!==null&&this.time-this.lastPulse>3000)this.speed=0;
    const lost=this.seen&&!this.peer&&this.time-this.lastPeer>=5000;
    const safe=this.parked&&this.still&&this.sensor&&this.speed===0;
    if(!safe){this.warning=null;this.lock='INHIBITED';}
    else if(this.auto&&lost){
      if(this.warning===null){this.warning=this.time;this.log('Remote lost: ten-second parking warning');}
      this.lock=this.time-this.warning>=10000?'REQUEST ONLY':'WARNING';
    }else if(this.warning!==null){this.warning=null;this.lock='UNLOCKED';}
  }
  outputs(){
    const on=this.time%1000<500;
    return {left:on&&['left','hazard'].includes(this.turn),right:on&&['right','hazard'].includes(this.turn),
      brake:this.brake,front:this.main,idle:this.night,siren:this.time<this.sirenUntil};
  }
}
if(typeof module!=='undefined')module.exports=BikeModel;
