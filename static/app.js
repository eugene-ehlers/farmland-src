const CENTER=[24.8,-28.6];
const OSM={version:8,sources:{osm:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap'}},layers:[{id:'osm',type:'raster',source:'osm'}]};
const map=new maplibregl.Map({container:'map',style:OSM,center:CENTER,zoom:5,maxBounds:[[9.5,-36.8],[41.5,-15.2]]});
map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-left');
function esc(s){return String(s??'').replace(/&/g,'&').replace(/</g,'<').replace(/>/g,'>')}
function banner(t){const el=document.getElementById('banner');if(el)el.textContent=t;}
function climateTable(c){
  if(!c||!c.monthly)return '<p>Climate not loaded.</p>';
  const rows=c.monthly.map(m=>`<tr><td>${esc(m.month)}</td><td>${m.rain_mm??'—'}</td><td>${m.rain_chirps_mm??'—'}</td><td>${m.t_mean_c??'—'}</td><td>${m.t_min_c??'—'}/${m.t_max_c??'—'}</td><td>${m.rh_pct??'—'}</td><td>${m.sun_mj_m2??'—'}</td></tr>`).join('');
  return `<p><strong>ERA5 ${c.annual_rain_mm??'—'} mm</strong> · <strong>CHIRPS ${c.annual_chirps_mm??'—'} mm</strong> · ${c.elevation_m??'—'} m</p>
    <table class="clim"><thead><tr><th></th><th>ERA5 mm</th><th>CHIRPS mm</th><th>T °C</th><th>Min/max</th><th>RH %</th><th>Sun</th></tr></thead><tbody>${rows}</tbody></table>
    <p class="foot">${esc(c.source)} · ${esc(c.chirps_source||'')} · ${esc(c.period)}</p>`;
}
function soilBlock(s, notes){
  if(!s)return '<p>Loading soil…</p>';
  const nums=s.has_values?`<p>Texture <strong>${esc(s.texture_class||'—')}</strong> · sand ${s.sand_pct??'—'}% · clay ${s.clay_pct??'—'}% · pH ${s.ph_water??'—'} · C ${s.soc_g_kg??'—'} g/kg · CEC ${s.cec_cmol_kg??'—'}</p>`:
    '<p>SoilGrids has no predicted value at this coordinate (common in parts of South Africa on the public point API). Climate notes below still apply. Next step is a lab sample on this plot.</p>';
  const lis=(notes||[]).map(n=>`<li>${esc(n)}</li>`).join('');
  return `${nums}<ul>${lis}</ul><p class="foot">${esc(s.source||'')}</p>`;
}
function dossierHtml(p, climate, soil){
  return `<h2>${esc(p.name)}</h2>
    <div class="ha">${p.extent_ha??'—'} ha · ${esc(p.parcel_id)}</div>
    <div class="meta">smallholding tile · not a cadastre diagram</div>
    <div class="block"><h3>Climate 2015–2024</h3>${climate?climateTable(climate):'<p>Loading historic weather…</p>'}</div>
    <div class="block"><h3>Soil and what it suggests</h3>${soil?soilBlock(soil.soil, soil.notes):'<p>Loading soil…</p>'}</div>`;
}
async function openDossier(id){
  const r=await fetch('/api/v1/parcels/'+encodeURIComponent(id));
  if(!r.ok)return;
  const body=await r.json();
  document.getElementById('dossier-body').innerHTML=dossierHtml(body.parcel,null,null);
  document.getElementById('dossier').hidden=false;
  let climate=null;
  try{
    const cr=await fetch('/api/v1/parcels/'+encodeURIComponent(id)+'/climate');
    const cj=await cr.json();
    climate=cr.ok?cj.climate:null;
    document.getElementById('dossier-body').innerHTML=dossierHtml(body.parcel,climate,null);
  }catch(e){}
  try{
    const sr=await fetch('/api/v1/parcels/'+encodeURIComponent(id)+'/soil');
    const sj=await sr.json();
    document.getElementById('dossier-body').innerHTML=dossierHtml(body.parcel,climate, sr.ok?sj:null);
  }catch(e){}
}
document.getElementById('close-dossier').onclick=()=>{document.getElementById('dossier').hidden=true};
async function loadParcels(){
  if(map.getZoom()<12){
    if(map.getSource('parcels')) map.getSource('parcels').setData({type:'FeatureCollection',features:[]});
    banner('Zoom closer (street / farm scale) to see ~1 ha cells.');
    return;
  }
  const b=map.getBounds();
  const bbox=[b.getWest(),b.getSouth(),b.getEast(),b.getNorth()].map(x=>x.toFixed(5)).join(',');
  const fc=await(await fetch('/api/v1/parcels?bbox='+bbox+'&limit=800')).json();
  if(!map.getSource('parcels')){
    map.addSource('parcels',{type:'geojson',data:fc});
    map.addLayer({id:'parcels-fill',type:'fill',source:'parcels',paint:{'fill-color':'#6b4f2a','fill-opacity':0.16}});
    map.addLayer({id:'parcels-line',type:'line',source:'parcels',paint:{'line-color':'#c4a35a','line-width':0.7}});
    map.on('click','parcels-fill',e=>{openDossier(e.features[0].properties.parcel_id);});
    map.on('mouseenter','parcels-fill',()=>map.getCanvas().style.cursor='pointer');
    map.on('mouseleave','parcels-fill',()=>map.getCanvas().style.cursor='');
  } else map.getSource('parcels').setData(fc);
  const n=(fc.features||[]).length;
  banner(n?`${n} cells (~1 ha each) in view.`:(fc.note||'Zoom closer to load cells.'));
}
let t=null;
map.on('load',loadParcels);
map.on('moveend',()=>{clearTimeout(t);t=setTimeout(loadParcels,350);});
document.getElementById('search-form').addEventListener('submit',async e=>{
  e.preventDefault();
  const raw=document.getElementById('search').value.trim();if(!raw)return;
  const coord=raw.match(/^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/);
  if(coord){const a=+coord[1],b=+coord[2];const lat=Math.abs(a)>15?a:b,lon=Math.abs(a)>15?b:a;map.flyTo({center:[lon,lat],zoom:13});return;}
  const data=await(await fetch('/api/v1/geocode?q='+encodeURIComponent(raw))).json();
  if(!data.results||!data.results.length){alert('No town or place matched in southern Africa.');return;}
  map.flyTo({center:[data.results[0].lon,data.results[0].lat],zoom:13});
});
