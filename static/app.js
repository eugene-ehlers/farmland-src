const CENTER=[24.8,-28.6];
const MONTHS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const OSM={version:8,sources:{osm:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap'}},layers:[{id:'osm',type:'raster',source:'osm'}]};
const map=new maplibregl.Map({container:'map',style:OSM,center:CENTER,zoom:5,maxBounds:[[9.5,-36.8],[41.5,-15.2]]});
map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-left');
function esc(s){return String(s??'').replace(/&/g,'&').replace(/</g,'<').replace(/>/g,'>')}
function banner(t){const el=document.getElementById('banner');if(el)el.textContent=t;}
function windowMonths(){
  const i=new Date().getMonth();
  return [0,1,2,3].map(k=>MONTHS[(i+k)%12]);
}
let currentParcel=null, currentClimate=null, currentSoil=null;
function climateTable(c){
  if(!c||!c.monthly)return '<p>Climate not loaded.</p>';
  const rows=c.monthly.map(m=>`<tr><td>${esc(m.month)}</td><td>${m.rain_mm??'—'}</td><td>${m.rain_chirps_mm??'—'}</td><td>${m.t_mean_c??'—'}</td><td>${m.t_min_c??'—'}/${m.t_max_c??'—'}</td><td>${m.rh_pct??'—'}</td><td>${m.sun_mj_m2??'—'}</td></tr>`).join('');
  return `<p><strong>ERA5 ${c.annual_rain_mm??'—'} mm</strong> · CHIRPS ${c.annual_chirps_mm??'—'} mm · ${c.elevation_m??'—'} m</p>
    <table class="clim"><thead><tr><th></th><th>ERA5</th><th>CHIRPS</th><th>T</th><th>Min/max</th><th>RH</th><th>Sun</th></tr></thead><tbody>${rows}</tbody></table>`;
}
function soilBlock(s, notes){
  if(!s)return '<p>Loading soil…</p>';
  const nums=s.has_values?`<p>Texture <strong>${esc(s.texture_class||'—')}</strong> · sand ${s.sand_pct??'—'}% · clay ${s.clay_pct??'—'}% · pH ${s.ph_water??'—'}</p>`:'<p>No SoilGrids value on this cell. Climate and markets still apply.</p>';
  return nums+'<ul>'+(notes||[]).map(n=>`<li>${esc(n)}</li>`).join('')+'</ul>';
}
function planBlock(p){
  if(!p)return '';
  const slots=(p.slots||[]).map(s=>`<li><strong>${esc(s.window)}</strong> (${esc(s.role)}): ${esc((s.examples||[]).join(', '))}</li>`).join('');
  const rot=(p.rotation_idea||[]).map(x=>`<li>${esc(x)}</li>`).join('');
  return `<p class="meta">${esc(p.rain_regime||'')} · summer ${p.summer_rain_mm??'—'} mm · winter ${p.winter_rain_mm??'—'} mm</p><p><em>${esc(p.not||'')}</em></p><ul>${slots}</ul><ul>${rot}</ul>`;
}
function marketBlock(m){
  if(!m)return '';
  return '<ul>'+(m.nearest||[]).map(x=>`<li>${esc(x.name)} · ${x.km} km · ${esc(x.size)}</li>`).join('')+'</ul><p class="foot">'+esc(m.price_note||'')+'</p>';
}
function bindPicker(){
  const monthEl=document.getElementById('pick-month');
  const cropEl=document.getElementById('pick-crop');
  if(!monthEl||!cropEl)return;
  const loadCrops=async()=>{
    const m=monthEl.value;
    cropEl.disabled=true; cropEl.innerHTML='<option value="">Loading…</option>';
    document.getElementById('crop-card').innerHTML='';
    if(!m){cropEl.innerHTML='<option value="">Choose a month</option>';return;}
    const regime=(currentSoil&&currentSoil.enterprises&&currentSoil.enterprises.rain_regime)||'';
    const data=await(await fetch('/api/v1/crops?month='+encodeURIComponent(m)+(regime?'&regime='+encodeURIComponent(regime):''))).json();
    const list=data.crops||[];
    if(!list.length){cropEl.innerHTML='<option value="">No fit in this window</option>';return;}
    cropEl.innerHTML='<option value="">Choose a crop</option>'+list.map(c=>`<option value="${c.id}">${esc(c.name)}</option>`).join('');
    cropEl.disabled=false;
  };
  monthEl.onchange=loadCrops;
  cropEl.onchange=async()=>{
    const id=cropEl.value; const box=document.getElementById('crop-card');
    if(!id){box.innerHTML='';return;}
    const c=await(await fetch('/api/v1/crops/'+encodeURIComponent(id))).json();
    const days=(c.growth_days||[]).join('–');
    box.innerHTML=`<p><strong>${esc(c.name)}</strong> · ${esc(c.role||'')} · growth ${esc(days)} days</p>
      <p><strong>Soil plan:</strong> ${esc(c.soil_plan||c.soil||'')}</p>
      <p><strong>Irrigation plan:</strong> ${esc(c.irrigation_plan||c.irrigation||'')}</p>
      <p><strong>Market price:</strong> ${esc(c.price_note||'Not wired live.')}</p>
      <p class="foot">General card for this crop type on this climate. Not a lab script and not a live quote.</p>`;
  };
  loadCrops();
}
function renderDossier(){
  const p=currentParcel; if(!p)return;
  const win=windowMonths();
  const monthOpts=win.map((m,i)=>`<option value="${m}">${i===0?m+' (now)':m}</option>`).join('');
  document.getElementById('dossier-body').innerHTML=`<h2>${esc(p.name)}</h2>
    <div class="ha">${p.extent_ha??'—'} ha · ${esc(p.parcel_id)}</div>
    <div class="block"><h3>This land</h3>
      <div>${currentClimate?climateTable(currentClimate):'<p>Loading climate…</p>'}</div>
    </div>
    <div class="block"><h3>Soil</h3>${currentSoil?soilBlock(currentSoil.soil,currentSoil.notes):'<p>Loading soil…</p>'}</div>
    <div class="block"><h3>Year pattern</h3>${currentSoil&&currentSoil.enterprises?planBlock(currentSoil.enterprises):'<p>Loading…</p>'}</div>
    <div class="block"><h3>Nearest markets</h3>${currentSoil&&currentSoil.markets?marketBlock(currentSoil.markets):'<p>Loading…</p>'}</div>
    <div class="block"><h3>Plant in this window</h3>
      <p class="meta">Current month and the next three. Crops are those that fit this land’s rain season.</p>
      <label>Month <select id="pick-month">${monthOpts}</select></label>
      <label>Crop <select id="pick-crop"><option value="">Choose month</option></select></label>
      <div id="crop-card"></div>
    </div>`;
  bindPicker();
}
async function openDossier(id){
  const r=await fetch('/api/v1/parcels/'+encodeURIComponent(id));
  if(!r.ok)return;
  currentParcel=(await r.json()).parcel; currentClimate=null; currentSoil=null;
  document.getElementById('dossier').hidden=false; renderDossier();
  try{const cr=await fetch('/api/v1/parcels/'+encodeURIComponent(id)+'/climate');const cj=await cr.json();if(cr.ok)currentClimate=cj.climate;}catch(e){}
  renderDossier();
  try{const sr=await fetch('/api/v1/parcels/'+encodeURIComponent(id)+'/soil');const sj=await sr.json();if(sr.ok)currentSoil=sj;}catch(e){}
  renderDossier();
}
document.getElementById('close-dossier').onclick=()=>{document.getElementById('dossier').hidden=true};
async function loadParcels(){
  if(map.getZoom()<12){if(map.getSource('parcels')) map.getSource('parcels').setData({type:'FeatureCollection',features:[]});banner('Zoom closer to see ~1 ha cells.');return;}
  const b=map.getBounds();
  const bbox=[b.getWest(),b.getSouth(),b.getEast(),b.getNorth()].map(x=>x.toFixed(5)).join(',');
  const fc=await(await fetch('/api/v1/parcels?bbox='+bbox+'&limit=800')).json();
  if(!map.getSource('parcels')){
    map.addSource('parcels',{type:'geojson',data:fc});
    map.addLayer({id:'parcels-fill',type:'fill',source:'parcels',paint:{'fill-color':'#6b4f2a','fill-opacity':0.16}});
    map.addLayer({id:'parcels-line',type:'line',source:'parcels',paint:{'line-color':'#c4a35a','line-width':0.7}});
    map.on('click','parcels-fill',e=>openDossier(e.features[0].properties.parcel_id));
    map.on('mouseenter','parcels-fill',()=>map.getCanvas().style.cursor='pointer');
    map.on('mouseleave','parcels-fill',()=>map.getCanvas().style.cursor='');
  } else map.getSource('parcels').setData(fc);
  banner(((fc.features||[]).length)+' cells in view.');
}
let t=null;map.on('load',loadParcels);map.on('moveend',()=>{clearTimeout(t);t=setTimeout(loadParcels,350);});
document.getElementById('search-form').addEventListener('submit',async e=>{
  e.preventDefault();
  const raw=document.getElementById('search').value.trim();if(!raw)return;
  const coord=raw.match(/^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/);
  if(coord){const a=+coord[1],b=+coord[2];const lat=Math.abs(a)>15?a:b,lon=Math.abs(a)>15?b:a;map.flyTo({center:[lon,lat],zoom:13});return;}
  const data=await(await fetch('/api/v1/geocode?q='+encodeURIComponent(raw))).json();
  if(!data.results||!data.results.length){alert('No match.');return;}
  map.flyTo({center:[data.results[0].lon,data.results[0].lat],zoom:13});
});
