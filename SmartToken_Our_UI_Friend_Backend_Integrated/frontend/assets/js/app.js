const specialties = [
  {name:'Gynaecology', icon:'♀', desc:'Women’s health & reproductive care', mins:15},
  {name:'Physiotherapy', icon:'◌', desc:'Movement, rehabilitation & pain care', mins:20},
  {name:'Psychology', icon:'◉', desc:'Mental wellbeing & counselling', mins:30},
  {name:'General Medicine', icon:'✚', desc:'General health & common conditions', mins:12},
  {name:'Paediatrics', icon:'♧', desc:'Healthcare for children', mins:15},
  {name:'Orthopaedics', icon:'⌁', desc:'Bones, joints & mobility', mins:18},
  {name:'Dermatology', icon:'✦', desc:'Skin, hair & nail care', mins:12},
  {name:'ENT', icon:'◒', desc:'Ear, nose & throat care', mins:12}
];

const hospitals = [
  {id:1,name:'Shivaji Government Hospital',locality:'Dadar',city:'Mumbai',state:'Maharashtra',pin:'400014',address:'Dr Babasaheb Ambedkar Road, Dadar East, Mumbai',lat:19.0178,lon:72.8478,specialties:['Gynaecology','Physiotherapy','Psychology','General Medicine','Paediatrics','Orthopaedics','Dermatology','ENT'],wait:34,queue:7},
  {id:2,name:'Lokmanya Tilak Municipal Hospital',locality:'Sion',city:'Mumbai',state:'Maharashtra',pin:'400022',address:'Sion, Mumbai',lat:19.0433,lon:72.8610,specialties:['Gynaecology','Physiotherapy','General Medicine','Paediatrics','Orthopaedics','ENT'],wait:48,queue:10},
  {id:3,name:'Rajawadi Government Hospital',locality:'Ghatkopar',city:'Mumbai',state:'Maharashtra',pin:'400077',address:'Rajawadi, Ghatkopar East, Mumbai',lat:19.0896,lon:72.9081,specialties:['Gynaecology','Psychology','General Medicine','Paediatrics','Dermatology'],wait:28,queue:5},
  {id:4,name:'Kalyan District Hospital',locality:'Kalyan West',city:'Kalyan',state:'Maharashtra',pin:'421301',address:'Kalyan West, Thane District, Maharashtra',lat:19.2437,lon:73.1355,specialties:['Gynaecology','Physiotherapy','General Medicine','Orthopaedics','ENT'],wait:41,queue:8},
  {id:5,name:'Civil Hospital Thane',locality:'Thane West',city:'Thane',state:'Maharashtra',pin:'400601',address:'Civil Hospital Road, Thane West, Maharashtra',lat:19.1970,lon:72.9708,specialties:['Gynaecology','Psychology','General Medicine','Paediatrics','Dermatology','ENT'],wait:36,queue:6},

  // Additional Mumbai public/government hospitals
  {id:6,name:'K.E.M. Hospital',locality:'Parel',city:'Mumbai',state:'Maharashtra',pin:'400012',address:'Acharya Donde Marg, Parel, Mumbai',lat:18.9992,lon:72.8408,specialties:['Gynaecology','Physiotherapy','Psychology','General Medicine','Paediatrics','Orthopaedics','Dermatology','ENT'],wait:52,queue:12},
  {id:7,name:'B.Y.L. Nair Hospital',locality:'Mumbai Central',city:'Mumbai',state:'Maharashtra',pin:'400008',address:'Dr Anandrao Nair Marg, Mumbai Central, Mumbai',lat:18.9767,lon:72.8236,specialties:['Gynaecology','Physiotherapy','Psychology','General Medicine','Paediatrics','Orthopaedics','Dermatology','ENT'],wait:46,queue:11},
  {id:8,name:'Dr. R.N. Cooper Municipal General Hospital',locality:'Juhu',city:'Mumbai',state:'Maharashtra',pin:'400056',address:'JVPD Scheme, Juhu, Mumbai',lat:19.1075,lon:72.8360,specialties:['Gynaecology','Physiotherapy','Psychology','General Medicine','Paediatrics','Orthopaedics','Dermatology','ENT'],wait:39,queue:8},
  {id:9,name:'K.B. Bhabha Municipal General Hospital',locality:'Bandra',city:'Mumbai',state:'Maharashtra',pin:'400050',address:'Waterfield Road, Bandra West, Mumbai',lat:19.0615,lon:72.8332,specialties:['Gynaecology','Physiotherapy','Psychology','General Medicine','Paediatrics','Orthopaedics','Dermatology','ENT'],wait:37,queue:7},
  {id:10,name:'V.N. Desai Municipal General Hospital',locality:'Santacruz East',city:'Mumbai',state:'Maharashtra',pin:'400055',address:'Road No. 11, Golibar, Santacruz East, Mumbai',lat:19.0795,lon:72.8505,specialties:['Gynaecology','Physiotherapy','Psychology','General Medicine','Paediatrics','Orthopaedics','Dermatology','ENT'],wait:42,queue:9},
  {id:11,name:'Sant Muktabai Municipal General Hospital',locality:'Ghatkopar West',city:'Mumbai',state:'Maharashtra',pin:'400084',address:'S.G. Barve Marg, Ghatkopar West, Mumbai',lat:19.0864,lon:72.9046,specialties:['Gynaecology','Psychology','General Medicine','Paediatrics','Dermatology'],wait:31,queue:6},
  {id:12,name:'K.M.J. Phule Municipal General Hospital',locality:'Vikhroli East',city:'Mumbai',state:'Maharashtra',pin:'400083',address:'Vikhroli East, Mumbai',lat:19.1114,lon:72.9270,specialties:['Gynaecology','Physiotherapy','General Medicine','Paediatrics','Orthopaedics','ENT'],wait:35,queue:7},
  {id:13,name:'Siddharth Municipal General Hospital',locality:'Goregaon West',city:'Mumbai',state:'Maharashtra',pin:'400104',address:'Goregaon West, Mumbai',lat:19.1663,lon:72.8499,specialties:['Gynaecology','Psychology','General Medicine','Paediatrics','Dermatology','ENT'],wait:38,queue:8},
  {id:14,name:'Shatabdi Hospital',locality:'Kandivali',city:'Mumbai',state:'Maharashtra',pin:'400067',address:'Kandivali, Mumbai',lat:19.2047,lon:72.8377,specialties:['Gynaecology','Physiotherapy','General Medicine','Paediatrics','Orthopaedics','ENT'],wait:40,queue:9},
  {id:15,name:'Shatabdi Hospital',locality:'Govandi',city:'Mumbai',state:'Maharashtra',pin:'400043',address:'Govandi East, Mumbai',lat:19.0554,lon:72.9189,specialties:['Gynaecology','Psychology','General Medicine','Paediatrics','Dermatology'],wait:33,queue:7},
  {id:16,name:'S.K. Patil Municipal General Hospital',locality:'Malad',city:'Mumbai',state:'Maharashtra',pin:'400064',address:'Malad, Mumbai',lat:19.1872,lon:72.8487,specialties:['Gynaecology','Physiotherapy','General Medicine','Paediatrics','Orthopaedics','ENT'],wait:36,queue:8},
  {id:17,name:'H.B.T. Trauma Care Hospital',locality:'Jogeshwari',city:'Mumbai',state:'Maharashtra',pin:'400102',address:'Jogeshwari, Mumbai',lat:19.1378,lon:72.8334,specialties:['General Medicine','Orthopaedics','ENT'],wait:44,queue:10},
  {id:18,name:'K.B. Bhabha Municipal General Hospital',locality:'Kurla',city:'Mumbai',state:'Maharashtra',pin:'400070',address:'Kurla West, Mumbai',lat:19.0726,lon:72.8826,specialties:['Gynaecology','Physiotherapy','General Medicine','Paediatrics','Orthopaedics','ENT'],wait:43,queue:9},
  {id:19,name:'M.W. Desai Municipal General Hospital',locality:'Malad',city:'Mumbai',state:'Maharashtra',pin:'400064',address:'Malad, Mumbai',lat:19.1870,lon:72.8480,specialties:['Gynaecology','General Medicine','Paediatrics','Dermatology'],wait:34,queue:7}
];

let patient = {};
let selectedSpecialty = null;
let selectedHospital = null;
let patientCoordinates = null;

let backendSpecialties = [];
let backendAppointment = null;
const API_BASE = '/api';

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {'Content-Type':'application/json', ...(options.headers || {})},
    ...options
  });
  const data = await response.json().catch(()=>({}));
  if(!response.ok) throw new Error(data.detail || data.message || 'SmartToken backend request failed');
  return data;
}

async function loadBackendCatalog() {
  backendSpecialties = await apiRequest('/specialties');
}
function backendSpecialtyId(name) {
  const s = backendSpecialties.find(x => x.name.toLowerCase() === name.toLowerCase());
  return s ? s.id : null;
}

function openModal(id){document.getElementById(id).classList.add('show')}
function closeModal(id){document.getElementById(id).classList.remove('show')}
function toast(msg,type='success'){
  const t=document.getElementById('toast'); if(!t)return;
  t.textContent=msg; t.className='toast show '+type;
  setTimeout(()=>t.classList.remove('show'),3200);
}
async function submitPatient(e){
  e.preventDefault();
  const btn=e.submitter;
  if(btn) btn.disabled=true;
  try{
    patient={name:pName.value.trim(),location:pLocation.value.trim(),phone:pPhone.value.trim(),email:pEmail.value.trim()};
    const created=await apiRequest('/patients',{method:'POST',body:JSON.stringify({
      name:patient.name,email:patient.email,phone:patient.phone
    })});
    patient.id=created.id;
    await loadBackendCatalog();
    goPatientStep(2);
    renderSpecialties();
  }catch(err){
    toast(err.message,'error');
  }finally{
    if(btn) btn.disabled=false;
  }
}
function goPatientStep(n){
  document.querySelectorAll('#patientModal .modal-step').forEach(x=>x.classList.remove('active'));
  const ids=['patientStep1','patientStep2','patientStep3','patientStep4'];
  document.getElementById(ids[n-1]).classList.add('active');
  document.querySelectorAll('.modal-progress span').forEach((x,i)=>x.classList.toggle('active',i<n));
}
function renderSpecialties(){
  specialtyGrid.innerHTML=specialties.map((s,i)=>`
    <button class="specialty-card" onclick="selectSpecialty(${i})">
      <span>${s.icon}</span><b>${s.name}</b><small>${s.desc}</small><i>→</i>
    </button>`).join('');
}
function selectSpecialty(i){
  selectedSpecialty=specialties[i];
  const backendId=backendSpecialtyId(selectedSpecialty.name);
  if(!backendId){toast('This specialty is not available in the backend yet.','error');return;}
  selectedSpecialty.backendId=backendId;
  hospitalSearch.value='';
  goPatientStep(3);
  renderHospitals();
}
function distanceKm(lat1, lon1, lat2, lon2){
  const R=6371, toRad=v=>v*Math.PI/180;
  const dLat=toRad(lat2-lat1), dLon=toRad(lon2-lon1);
  const a=Math.sin(dLat/2)**2 + Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*Math.sin(dLon/2)**2;
  return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
}

function renderHospitals(){
  const q=(hospitalSearch.value||'').toLowerCase().trim();
  let list=hospitals.filter(h=>
    h.specialties.includes(selectedSpecialty.name) &&
    [h.name,h.locality,h.city,h.state,h.pin,h.address].join(' ').toLowerCase().includes(q)
  );
  if(patientCoordinates){
    list=list.map(h=>({...h,distance:distanceKm(patientCoordinates.lat,patientCoordinates.lon,h.lat,h.lon)}))
             .sort((a,b)=>a.distance-b.distance);
  }
  hospitalList.innerHTML=list.length?list.map(h=>`
    <button class="hospital-card" onclick="selectHospital(${h.id})">
      <div class="hospital-icon">✚</div><div class="hospital-info"><b>${h.name}</b><span>${h.address}</span>
      <small>${h.locality}, ${h.city} · ${h.pin}${typeof h.distance==='number' ? ` · ${h.distance.toFixed(1)} km away` : ''}</small>
      <div class="hospital-meta"><em>● Live queue</em><em>Real-time ETA after booking</em></div></div><strong>→</strong>
    </button>`).join(''):`<div class="empty-state">No ${selectedSpecialty.name} hospitals found for this search. Try a wider locality, city or PIN.</div>`;
}
function selectHospital(id){
  selectedHospital=hospitals.find(h=>h.id===id);
  if(!selectedHospital){toast('Hospital not found.','error');return;}
  bookingSummary.innerHTML=`<div><span>Specialty</span><b>${selectedSpecialty.name}</b></div>
  <div><span>Hospital</span><b>${selectedHospital.name}</b></div>
  <div><span>Patient</span><b>${patient.name}</b></div>
  <div><span>Location</span><b>${selectedHospital.locality}, ${selectedHospital.city} · ${selectedHospital.pin}</b></div>`;
  const now=new Date();
  now.setMinutes(now.getMinutes()+30);
  apptDate.value=now.toISOString().slice(0,10);
  apptTime.value=String(now.getHours()).padStart(2,'0')+':'+String(Math.floor(now.getMinutes()/5)*5).padStart(2,'0');
  goPatientStep(4);
}
async function confirmBooking(e){
  e.preventDefault();
  const btn=e.submitter;
  if(btn){btn.disabled=true;btn.textContent='Connecting to SmartToken…';}
  try{
    const specialtyId=selectedSpecialty.backendId || backendSpecialtyId(selectedSpecialty.name);
    const data=await apiRequest('/appointments',{
      method:'POST',
      body:JSON.stringify({
        patient_id:patient.id,
        name:patient.name,
        email:patient.email,
        phone:patient.phone,
        hospital_id:selectedHospital.id,
        specialty_id:specialtyId,
        is_emergency:false
      })
    });
    backendAppointment=data;
    renderTokenResult(data);
    document.querySelectorAll('#patientModal .modal-step').forEach(x=>x.classList.remove('active'));
    patientSuccess.classList.add('active');
    document.querySelectorAll('.modal-progress span').forEach(x=>x.classList.add('active'));
    startLivePatientPolling();
  }catch(err){
    toast(err.message,'error');
  }finally{
    if(btn){btn.disabled=false;btn.textContent='Generate Smart Token ✦';}
  }
}

function formatBackendTime(value){
  if(!value)return '-';
  const d=new Date(value);
  return isNaN(d.getTime()) ? String(value) : d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}
function renderTokenResult(data){
  const emailState=data.notification_email ? 'Email sent' : 'Email configured but not dispatched';
  const smsState=data.notification_sms ? 'SMS sent' : 'SMS configured but not dispatched';
  tokenResult.innerHTML=`<div class="result-token">${data.token_number}</div>
  <div class="result-details">
    <div><span>Hospital</span><b>${selectedHospital.name}</b></div>
    <div><span>Department</span><b>${selectedSpecialty.name}</b></div>
    <div><span>Queue position</span><b>#${data.queue_position}</b></div>
    <div><span>Estimated wait</span><b>${data.waiting_minutes} minutes</b></div>
    <div><span>Suggested arrival</span><b>${formatBackendTime(data.estimated_arrival_time)}</b></div>
    <div><span>Appointment</span><b>${formatBackendTime(data.appointment_time)}</b></div>
  </div>
  <div class="notification-sim"><b>✉ Email + SMS ${data.notification_email || data.notification_sms ? 'dispatched' : 'ready'}</b>
  <small>${emailState} · ${smsState}. Future cancellation, emergency and doctor-change events will automatically update this queue.</small></div>`;
}
let patientPollTimer=null;
function startLivePatientPolling(){
  if(patientPollTimer) clearInterval(patientPollTimer);
  if(!backendAppointment?.id)return;
  patientPollTimer=setInterval(async()=>{
    try{
      const live=await apiRequest(`/queue/appointment/${backendAppointment.id}`);
      backendAppointment={...backendAppointment,...live};
      if(patientSuccess.classList.contains('active')) renderTokenResult(backendAppointment);
      if(live.status==='CANCELLED') clearInterval(patientPollTimer);
    }catch(_){}
  },5000);
}
function useCurrentLocation(){
  locationStatus.textContent='Requesting your location to sort nearby hospitals...';
  if(!navigator.geolocation){
    locationStatus.textContent='Location is not supported. You can continue using locality, city or PIN search.';
    return;
  }
  navigator.geolocation.getCurrentPosition(
    pos=>{
      patientCoordinates={lat:pos.coords.latitude,lon:pos.coords.longitude};
      locationStatus.textContent='Location received. Hospitals are now shown from nearest to farthest.';
      renderHospitals();
    },
    ()=>{
      locationStatus.textContent='Location was not shared. You can continue using locality, city or PIN search.';
    },
    {enableHighAccuracy:true,timeout:10000,maximumAge:300000}
  );
}
async function adminLogin(e){
  e.preventDefault();
  const code=hospitalCode.value.trim();
  if(code!=='SMT-MUM-001'){toast('Demo hospital code is SMT-MUM-001','error');return;}
  try{
    await apiRequest('/health');
    window.location.href='admin.html';
  }catch(err){
    toast('Start the SmartToken backend first. '+err.message,'error');
  }
}

loadBackendCatalog().catch(()=>{});
