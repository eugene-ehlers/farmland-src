const CENTER=[24.8,-28.6];
const OSM={version:8,sources:{osm:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap'}},layers:[{id:'osm',type:'raster',source:'osm'}]};
const map=new maplibregl.Map({container:'map',style:OSM,center:CENTER,zoom:5,maxBounds:[[9.5,-36.8],[41.5,-15.2]]});
map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-left');
function esc(s){return String(s??'').replace(/&/g,'&').replace(/</g,'<').replace(/>/g,'>')}
function banner(t){const el=document.getElementById('banner');if(el)el.textContent=t;}
function dossierHtml(p){
  return `<h2>${esc(p.name)}</h2>
    <div class="ha">${p.extent_ha??'—'} ha · ${esc(p.parcel_id)}</div>
    <div class="meta">sg_code: null · analysis cell, not a cadastre diagram</div>
    <div class="block"><h3>Grain</h3><p>This row is a ${esc(String(p.step_deg??0.01))}° coordinate cell. Weather, soil and markets will attach to this id.</p><p class="foot">${esc(p.source||'')}</p></div>
    <div class="block"><h3>Not on this row yet</h3><p>Historic weather, soil / land type, enterprise calendar, markets, legal farm overlay.</p></div>`;
}
async function openDossier(id){
  const r=await fetch('/api/v1/parcels/'+encodeURIComponent(id));
  if(!r.ok)return;
  const body=await r.json();
  document.getElementById('dossier-body').innerHTML=dossierHtml(body.parcel);
  document.getElementById('dossier').hidden=false;
}
document.getElementById('close-dossier').onclick=()=>{document.getElementById('dossier').hidden=true};
async function loadParcels(){
  if(map.getZoom()<9){
    if(map.getSource('parcels')) map.getSource('parcels').setData({type:'FeatureCollection',features:[]});
    banner('Zoom in to see analysis cells (~1 km). Every cell has a stable id.');
    return;
  }
  const b=map.getBounds();
  const bbox=[b.getWest(),b.getSouth(),b.getEast(),b.getNorth()].map(x=>x.toFixed(5)).join(',');
  const fc=await(await fetch('/api/v1/parcels?bbox='+bbox+'&limit=600')).json();
  if(!map.getSource('parcels')){
    map.addSource('parcels',{type:'geojson',data:fc});
    map.addLayer({id:'parcels-fill',type:'fill',source:'parcels',paint:{'fill-color':'#6b4f2a','fill-opacity':0.18}});
    map.addLayer({id:'parcels-line',type:'line',source:'parcels',paint:{'line-color':'#c4a35a','line-width':0.8}});
    map.on('click','parcels-fill',e=>{openDossier(e.features[0].properties.parcel_id);});
    map.on('mouseenter','parcels-fill',()=>map.getCanvas().style.cursor='pointer');
    map.on('mouseleave','parcels-fill',()=>map.getCanvas().style.cursor='');
  } else map.getSource('parcels').setData(fc);
  const n=(fc.features||[]).length;
  banner(n?`${n} analysis cells in view. Click a cell for its id.`:(fc.note||'Zoom in to load cells.'));
}
let t=null;
map.on('load',loadParcels);
map.on('moveend',()=>{clearTimeout(t);t=setTimeout(loadParcels,350);});
document.getElementById('search-form').addEventListener('submit',async e=>{
  e.preventDefault();
  const raw=document.getElementById('search').value.trim();if(!raw)return;
  const coord=raw.match(/^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/);
  if(coord){const a=+coord[1],b=+coord[2];const lat=Math.abs(a)>15?a:b,lon=Math.abs(a)>15?b:a;map.flyTo({center:[lon,lat],zoom:11});return;}
  const data=await(await fetch('/api/v1/geocode?q='+encodeURIComponent(raw))).json();
  if(!data.results||!data.results.length){alert('No town or place matched in southern Africa.');return;}
  map.flyTo({center:[data.results[0].lon,data.results[0].lat],zoom:11});
});
