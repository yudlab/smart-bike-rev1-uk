(()=>{'use strict';
const $=id=>document.getElementById(id);
const key=$('diagnosticToken'); key.value=sessionStorage.getItem('bikeToken')||'';
let refreshing=false, commandBusy=false, previousEvents='', lastLink=null;
function status(message,connected=false){
 const el=$('diagStatus'); if(el.textContent!==message)el.textContent=message;
 el.classList.toggle('connected',connected);
}
async function api(path,options={}){
 const response=await fetch(path,{cache:'no-store',...options,headers:{'X-Bike-Token':key.value,...(options.headers||{})}});
 const data=await response.json(); if(!response.ok)throw Error(data.error||response.status);
 return data;
}
function setCommands(enabled){
 for(const id of ['diagLeft','diagRight','diagHazard','diagStop'])$(id).disabled=!enabled||commandBusy;
}
async function refresh(){
 if(refreshing)return;refreshing=true;
 try{
  const data=await api('/api/diagnostics'),t=data.telemetry;
  const connected=!!data.connected;
  status(connected?'Pico connected · '+data.port:'Pico offline'+(data.error?' · '+data.error:''),connected);
  setCommands(connected);
  const badge=document.querySelector('header .badge');
  if(badge){badge.textContent=connected?'SIMULATION + LIVE PICO TELEMETRY':'SIMULATION · PICO OFFLINE';badge.classList.toggle('live',connected)}
  if(connected&&t){
   $('diagSpeed').textContent=Number(t.kmh||0).toFixed(1);
   $('diagTrip').textContent=(Number(t.trip_mm||0)/1000000).toFixed(3);
   $('diagBounce').textContent=String(t.rejected||0);
   $('diagFaults').textContent=String(t.command_errors||0);
   const remaining=Math.max(0,Number(t.test_remaining_ms||0));
   $('diagTimer').textContent=(remaining/1000).toFixed(1)+'s';
   $('diagProgress').style.setProperty('--remaining',((remaining/10000)*100)+'%');
   $('diagActive').textContent=t.test_side==='off'?'No active test':t.test_side.toUpperCase()+' indicator test';
   $('diagInputs').textContent='Reed '+t.input_reed+' · Brake '+t.input_brake+' · Left '+t.input_left+' · Right '+t.input_right;
   $('diagOutputs').textContent=JSON.stringify(t.outputs||{},null,2);
   $('diagOutputMode').textContent=t.bench_led_outputs?'GP17/GP18 bench LEDs enabled':'Virtual outputs only — GPIO disabled';
   if(lastLink===false)status('Pico reconnected · '+data.port,true);
  }else{
   $('diagActive').textContent='No active connection';$('diagTimer').textContent='—';
   $('diagProgress').style.setProperty('--remaining','0%');
   $('diagOutputMode').textContent='No current hardware telemetry';
  }
  const events=(data.events||[]).map(e=>JSON.stringify(e)).join('\n');
  if(events!==previousEvents){$('diagEvents').textContent=events||'No commands yet';previousEvents=events;}
  lastLink=connected;
 }catch(error){
  status('Diagnostic bridge unavailable · '+error.message);setCommands(false);lastLink=false;
  const badge=document.querySelector('header .badge');
  if(badge){badge.textContent='SIMULATION · NO HARDWARE CONNECTED';badge.classList.remove('live')}
 }
 finally{refreshing=false}
}
async function send(command,side){
 if(commandBusy)return;commandBusy=true;setCommands(false);
 try{
  await api('/api/test',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cmd:command,...(side?{side}:{})})});
  status('Command sent · awaiting Pico acknowledgement',true);
 }catch(error){status('Command failed · '+error.message)}
 finally{commandBusy=false;await refresh()}
}
$('saveToken').onclick=()=>{sessionStorage.setItem('bikeToken',key.value);refresh()};
$('diagLeft').onclick=()=>send('test_indicator','left');
$('diagRight').onclick=()=>send('test_indicator','right');
$('diagHazard').onclick=()=>send('test_indicator','hazard');
$('diagStop').onclick=()=>send('stop_test');
setCommands(false);refresh();setInterval(refresh,500);
})();