let deptData=[];
let currentEvent=null;
let hospitalData=null;
let specialtyList=[];
let pollingTimer=null;
const API_BASE='/api';

async function apiRequest(path, options={}){
  const response=await fetch(`${API_BASE}${path}`,{
    headers:{'Content-Type':'application/json',...(options.headers||{})},
    ...options
  });
  const data=await response.json().catch(()=>({}));
  if(!response.ok) throw new Error(data.detail || data.message || 'Backend request failed');
  return data;
}
function openModal(id){document.getElementById(id).classList.add('show')}
function closeModal(id){document.getElementById(id).classList.remove('show')}
function toast(msg,type='success'){
  const t=document.getElementById('toast');t.textContent=msg;t.className='toast show '+type;
  setTimeout(()=>t.classList.remove('show'),3200);
}
function clock(){document.getElementById('clock').textContent=new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'})}
setInterval(clock,1000);clock();

function groupDashboard(data){
  const map=new Map();
  for(const s of data.specialties) map.set(s.id,{id:s.id,name:s.name,doctor:'OPD Doctor',avg:15,patients:[]});
  for(const a of data.appointments){
    if(!map.has(a.specialty_id)) map.set(a.specialty_id,{id:a.specialty_id,name:'Department',doctor:a.doctor_name||'OPD Doctor',avg:15,patients:[]});
    const d=map.get(a.specialty_id);
    d.doctor=a.doctor_name||d.doctor;
    d.patients.push(a);
  }
  return Array.from(map.values()).filter(d=>d.patients.length);
}

async function loadDashboard(){
  try{
    const [data,stats]=await Promise.all([
      apiRequest('/admin/dashboard'),
      apiRequest('/admin/stats')
    ]);
    hospitalData=data.hospital;
    specialtyList=data.specialties||[];
    deptData=groupDashboard(data);
    renderDepartments();
    document.getElementById('totalPatients').textContent=stats.waiting;
    document.getElementById('emergencyCount').textContent=stats.emergency_waiting;
    const total=stats.waiting||0;
    const weighted=deptData.reduce((sum,d)=>sum+d.patients.reduce((a,p)=>a+p.waiting_minutes,0),0);
    document.getElementById('avgWait').textContent=(total?Math.round(weighted/total):0)+' min';
  }catch(err){
    addLog('system','Backend connection error: '+err.message);
    toast(err.message,'error');
  }
}

function renderDepartments(){
  const grid=document.getElementById('deptGrid');
  grid.innerHTML=deptData.map((d,i)=>`
  <article class="dept-card">
    <div class="dept-head"><div><span class="dept-icon">✚</span><div><h3>${d.name}</h3><p>${d.doctor} · live forecast</p></div></div><span class="queue-count">${d.patients.length} waiting</span></div>
    <div class="queue-table">
      <div class="queue-header"><span>Token</span><span>Patient</span><span>ETA</span><span>Status</span></div>
      ${d.patients.map(p=>`<div class="queue-row"><span class="token-chip">${p.token_number}</span><span><b>${p.patient_name}</b></span><span>${formatTime(p.appointment_time)}</span><span class="status ${p.status.toLowerCase()}">${p.status}</span></div>`).join('')}
    </div>
    <button class="view-queue" onclick="simulateNext(${i})">Call next patient →</button>
  </article>`).join('');
}
function formatTime(value){
  if(!value)return '-';
  const d=new Date(value);
  return isNaN(d.getTime())?String(value):d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}
async function simulateNext(i){
  const d=deptData[i];
  if(!d?.patients?.length)return;
  const p=d.patients[0];
  await performAction(
    ()=>apiRequest(`/admin/appointments/${p.id}/serve`,{method:'POST'}),
    `${d.name}: ${p.token_number} marked as served. Queue moved forward.`
  );
}
async function recalculateAll(){
  try{
    const result=await apiRequest('/admin/reforecast-all',{method:'POST'});
    document.getElementById('updateCount').textContent=Number(document.getElementById('updateCount').textContent)+Number(result.updated||0);
    addLog('system','Live re-forecast completed. All affected patients were notified.');
    await loadDashboard();
    toast('All queue ETAs re-forecasted');
  }catch(err){toast(err.message,'error')}
}

function openEvent(type){
  currentEvent=type;
  const deptOptions=deptData.map((d,i)=>`<option value="${i}">${d.name}</option>`).join('');
  const configs={
    cancel:{
      eyebrow:'EVENT 01 · CANCELLATION',
      title:'Patient cancellation',
      desc:'Remove a waiting patient. Everyone behind them receives a new ETA by email and SMS.',
      fields:`<label>Department<select id="eventDept">${deptOptions}</select></label><label>Token to cancel<select id="eventToken"></select></label>`
    },
    emergency:{
      eyebrow:'EVENT 02 · PRIORITY INSERTION',
      title:'Emergency walk-in',
      desc:'Insert a priority patient and immediately re-forecast the affected patients.',
      fields:`<label>Department<select id="eventDept">${deptOptions}</select></label><label>Estimated emergency handling time (minutes)<input id="eventMinutes" type="number" min="1" value="20"></label><label>Priority token / ID<input id="eventPatient" value="ER-${Math.floor(100+Math.random()*900)}"></label>`
    },
    doctor:{
      eyebrow:'EVENT 03 · DOCTOR AVAILABILITY',
      title:'Doctor unavailable',
      desc:'Switch the affected queue to an alternative doctor. Patients receive email + SMS about the doctor change.',
      fields:`<label>Department<select id="eventDept">${deptOptions}</select></label><label>Alternative doctor<select id="eventDoctor"><option>Dr. Aisha Desai</option><option>Dr. Rahul Mehta</option><option>Dr. Kavya Shah</option><option>Dr. Neel Deshmukh</option></select></label><label>Reason (internal note)<input id="eventReason" placeholder="e.g. Doctor unavailable"></label>`
    }
  }[type];
  eventEyebrow.textContent=configs.eyebrow;
  eventTitle.textContent=configs.title;
  eventDescription.textContent=configs.desc;
  eventFields.innerHTML=configs.fields;
  if(type==='cancel'){eventDept.onchange=populateTokens;populateTokens();}
  openModal('eventModal');
}
function populateTokens(){
  const d=deptData[Number(eventDept.value)];
  eventToken.innerHTML=(d?.patients||[]).map((p,i)=>`<option value="${p.id}">${p.token_number} — ${p.patient_name}</option>`).join('');
}
async function submitEvent(e){
  e.preventDefault();
  const i=Number(eventDept.value),d=deptData[i];
  if(!d){toast('Select a department.','error');return;}
  try{
    if(currentEvent==='cancel'){
      const id=Number(eventToken.value);
      await apiRequest(`/admin/appointments/${id}/cancel`,{method:'POST'});
      addLog('cancel',`${d.name}: selected patient cancelled. Remaining patients received new ETA notifications.`);
      toast('Cancellation applied — queue moved forward');
    }
    if(currentEvent==='emergency'){
      const mins=Number(eventMinutes.value)||20;
      const id=eventPatient.value||'Walk-in Emergency';
      if(!hospitalData){throw new Error('Hospital record not found.');}
      await apiRequest('/queue/emergency',{
        method:'POST',
        body:JSON.stringify({hospital_id:hospitalData.id,specialty_id:d.id,name:id,minutes:mins})
      });
      addLog('emergency',`${d.name}: ${id} inserted as priority. Affected patients notified of the +${mins} minute emergency delay.`);
      toast('Emergency inserted — affected ETAs updated');
    }
    if(currentEvent==='doctor'){
      if(!hospitalData)throw new Error('Hospital record not found.');
      const doc=eventDoctor.value;
      const reason=eventReason.value||'Doctor unavailable';
      await apiRequest(`/admin/doctor-unavailable?hospital_id=${hospitalData.id}&specialty_id=${d.id}&alternative_doctor=${encodeURIComponent(doc)}`,{method:'POST'});
      addLog('doctor',`${d.name}: doctor unavailable (${reason}). Queue transferred to ${doc}; patients notified by email + SMS.`);
      toast('Doctor switched — patients notified');
    }
    closeModal('eventModal');
    await loadDashboard();
  }catch(err){toast(err.message,'error')}
}
async function performAction(fn,successText){
  try{
    await fn(); addLog('complete',successText); await loadDashboard(); toast(successText);
  }catch(err){toast(err.message,'error')}
}
function addLog(type,text){
  const log=document.getElementById('activityLog');
  const icons={cancel:'↘',emergency:'⚡',doctor:'⚕',complete:'✓',system:'↻'};
  const div=document.createElement('div');div.className='activity-item';
  div.innerHTML=`<span class="activity-icon ${type}">${icons[type]||'•'}</span><div><b>${text}</b><small>${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})} · Notifications processed by backend</small></div>`;
  log.prepend(div);
  while(log.children.length>8)log.lastChild.remove();
}

loadDashboard();
pollingTimer=setInterval(loadDashboard,5000);
addLog('system','Dashboard connected. Queue data is now coming from the live backend.');
