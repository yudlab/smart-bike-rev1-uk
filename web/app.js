const bike=new BikeModel(), $=id=>document.getElementById(id);
const fields={night:'Night / idle lamps',main:'Main headlamp',brake:'Brake sensor',armed:'Alarm armed',auto:'Auto-lock policy',peer:'Paired remote heartbeat',parked:'Physical PARK selector',still:'Independent standstill input',sensor:'Motion sensor healthy'};
for(const [key,label] of Object.entries(fields)){
 const row=document.createElement('label');row.textContent=label;
 const input=document.createElement('input');input.type='checkbox';input.checked=bike[key];input.id=key;
 input.onchange=()=>{bike[key]=input.checked;bike.log(`${label}: ${input.checked?'on':'off'}`);};
 row.append(input);$(key==='night'||key==='main'||key==='brake'?'lights':'security').append(row);
}
fetch('bike.svg').then(r=>r.text()).then(svg=>{$('visual').innerHTML=svg;}).catch(()=>{$('visual').textContent='Run the local web server to load the vector drawing.';});
$('turn').onchange=e=>{bike.turn=e.target.value;bike.log(`Indicators: ${bike.turn}`);};
$('brightness').oninput=e=>bike.backlight=+e.target.value;
$('calibrate').onclick=()=>{try{bike.calibrate(+$('mm').value,+$('magnets').value);}catch(e){bike.log(e.message);}};
$('units').onclick=()=>bike.unit=bike.unit==='km/h'?'mph':'km/h';
$('pulse').onclick=()=>bike.pulse();
$('noise').onclick=()=>{bike.pulse();bike.pulse();bike.pulse();bike.log('Injected simultaneous contact bounce');};
let spinning=false,nextPulse=0;
$('spin').onclick=()=>{spinning=!spinning;$('spin').textContent=spinning?'Stop wheel pulses':'Start wheel pulses';nextPulse=bike.time;};
$('request').onclick=()=>bike.requestLock();
$('unlock').onclick=()=>{bike.lock='UNLOCKED';bike.warning=null;bike.auto=false;$('auto').checked=false;bike.log('Request cleared; auto-lock disabled');};
$('siren').onclick=()=>{bike.sirenUntil=bike.time+2000;bike.log('Siren: bounded visual bench test');};
$('motion').onclick=()=>{if(bike.armed){bike.sirenUntil=bike.time+2000;bike.log('Alarm motion event');}else bike.log('Motion ignored: alarm disarmed');};
$('gpsToggle').onclick=()=>bike.gps=!bike.gps;
$('colour').oninput=e=>{document.querySelectorAll('#visual [stroke="#43d7c4"]').forEach(p=>p.dataset.frame='true');document.querySelectorAll('[data-frame]').forEach(p=>p.setAttribute('stroke',e.target.value));};
$('reset').onclick=()=>location.reload();
$('export').onclick=()=>{const data={mode:'SIMULATION',tripKm:bike.trip,pulses:bike.pulses,rejected:bike.rejected,events:bike.events,calibration:{mm:bike.circumference,magnets:bike.magnets}};const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='bike-bench-session.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
const menu=['Alarm','Lock request','Auto lock','Night mode'];let selected=0;
function move(d){selected=(selected+d+menu.length)%menu.length;$('remoteItem').textContent=menu[selected];}
$('up').onclick=()=>move(-1);$('down').onclick=()=>move(1);
$('select').onclick=()=>{if(selected===1)bike.requestLock();else{const key=['armed',null,'auto','night'][selected];bike[key]=!bike[key];$(key).checked=bike[key];bike.log(`Remote: ${menu[selected]} ${bike[key]}`);}};
bike.log('Lab ready. All outputs simulated; no radio transmissions.');
setInterval(()=>{
 bike.tick(50);if(spinning&&bike.time>=nextPulse){bike.pulse();nextPulse=bike.time+500;}
 const out=bike.outputs();$('speed').textContent=(bike.speed/(bike.unit==='mph'?1.609344:1)).toFixed(1);$('unitLabel').textContent=bike.unit;$('trip').textContent=bike.trip.toFixed(3);$('lock').textContent=bike.lock;
 $('counts').textContent=`Accepted: ${bike.pulses} · Rejected: ${bike.rejected}`;$('gps').textContent=`GPS: ${bike.gps?'simulated fix available — no coordinates':'no fix (simulated)'}`;
 $('events').textContent=bike.events.join('\n');document.body.classList.toggle('night',bike.night);document.querySelector('.hero').classList.toggle('siren',out.siren);
 if($('front')){$('front').setAttribute('fill',out.front?'#fff4b5':'#60747d');$('beam').setAttribute('opacity',out.front?'.45':'.03');$('rear').setAttribute('fill',out.brake?'#ff525e':out.idle?'#c13d57':'#702d3c');$('left').setAttribute('fill',out.left?'#ffbf4e':'#58452d');$('right').setAttribute('fill',out.right?'#ffbf4e':'#58452d');document.querySelector('#visual text').style.opacity=bike.backlight/100;}
},50);
