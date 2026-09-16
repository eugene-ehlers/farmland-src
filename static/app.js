const LIMPOPO=[26.4,-25.5,31.9,-22.15],CENTER=[29.45,-23.9];
const OSM={version:8,sources:{osm:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap'},esri:{type:'raster',tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],tileSize:256,attribution:'Esri World Imagery'}},layers:[{id:'osm',type:'raster',source:'osm'}]};
const map=new maplibregl.Map({container:'map',style:OSM,center:CENTER,zoom:7,maxBounds:[[25.2,-26.4],[33.2,-21.3]]});
map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-left');
let satOn=false;
function esc(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function dossierHtml(d){const p=d.parcel,i=d.intelligence;const foot=(b)=>b?`${esc(b.source||'')} · ${esc(b.scale||'')} · ${esc(b.as_of||'')} · ${esc(b.confidence||'')}`:'not loaded';
return `<h2>${esc(p.name)}</h2><div class="ha">${p.extent_ha} ha · ${esc(p.parcel_id)}</div><div class="meta">sg_code: ${p.sg_code==null?'null (CSG not loaded)':esc(p.sg_code)}</div>
<div class="block"><h3>Land type</h3><p>${esc(i.land_type.class)}</p><p class="foot">${foot(i.land_type)}</p></div>
<div class="block"><h3>Climate</h3><p>${esc(i.climate.class)}</p><p>${i.climate.mean_annual_rainfall_mm??'null'} mm MAR</p><p class="foot">${foot(i.climate)}</p></div>
<div class="block"><h3>Hydro</h3><p>${esc(i.hydro.nearest_river)} (${i.hydro.km} km)</p><p>Catchment: ${esc(i.hydro.in_catchment)}</p></div>
<div class="block"><h3>Relief</h3><p>${esc(i.relief.description)}</p><p class="foot">${esc(i.relief.source)}</p></div>
<div class="block"><h3>Settlement</h3><p>${esc(i.settlement.class)}</p><p class="foot">${esc(i.settlement.source)} · ${esc(i.settlement.as_of)}</p></div>`;}
async function openDossier(id){const r=await fetch('/api/v1/parcels/'+encodeURIComponent(id));if(!r.ok)return;document.getElementById('dossier-body').innerHTML=dossierHtml(await r.json());document.getElementById('dossier').hidden=false;}
document.getElementById('close-dossier').onclick=()=>{document.getElementById('dossier').hidden=true};
map.on('load',async()=>{const fc=await(await fetch(`/api/v1/parcels?bbox=${LIMPOPO.join(',')}&limit=500`)).json();
map.addSource('parcels',{type:'geojson',data:fc});
map.addLayer({id:'parcels-fill',type:'fill',source:'parcels',paint:{'fill-color':'#3d6b2f','fill-opacity':0.35}});
map.addLayer({id:'parcels-line',type:'line',source:'parcels',paint:{'line-color':'#243f1c','line-width':1.4}});
map.addLayer({id:'parcels-hi',type:'line',source:'parcels',filter:['==',['get','parcel_id'],''],paint:{'line-color':'#c4a35a','line-width':3}});
map.on('click','parcels-fill',e=>{const id=e.features[0].properties.parcel_id;map.setFilter('parcels-hi',['==',['get','parcel_id'],id]);openDossier(id);});
map.on('mouseenter','parcels-fill',()=>map.getCanvas().style.cursor='pointer');
map.on('mouseleave','parcels-fill',()=>map.getCanvas().style.cursor='');
});
document.getElementById('chips').addEventListener('click',ev=>{const btn=ev.target.closest('.chip');if(!btn)return;const layer=btn.dataset.layer;
if(layer==='satellite'){satOn=!satOn;btn.classList.toggle('on',satOn);if(satOn){if(!map.getLayer('esri'))map.addLayer({id:'esri',type:'raster',source:'esri'},'parcels-fill');if(map.getLayer('osm'))map.setLayoutProperty('osm','visibility','none');map.setLayoutProperty('esri','visibility','visible');}else{if(map.getLayer('esri'))map.setLayoutProperty('esri','visibility','none');if(map.getLayer('osm'))map.setLayoutProperty('osm','visibility','visible');}return;}
btn.classList.toggle('on');const on=btn.classList.contains('on');
if(layer==='parcels'){const vis=on?'visible':'none';['parcels-fill','parcels-line','parcels-hi'].forEach(id=>{if(map.getLayer(id))map.setLayoutProperty(id,'visibility',vis);});return;}
if(!map.getLayer('parcels-fill'))return;
if(layer==='settlement'&&on)map.setPaintProperty('parcels-fill','fill-color',['match',['get','layer_settlement'],'town','#c45c26','rural','#d4a017','#3d6b2f']);
else if(on)map.setPaintProperty('parcels-fill','fill-color',({land_type:'#6b4f2a',climate:'#2f5f7a',hydro:'#2a6f8a',relief:'#5a4a32'})[layer]||'#3d6b2f');
else map.setPaintProperty('parcels-fill','fill-color','#3d6b2f');
});
document.getElementById('search-form').addEventListener('submit',async e=>{e.preventDefault();const raw=document.getElementById('search').value.trim();if(!raw)return;
const coord=raw.match(/^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/);if(coord){const a=+coord[1],b=+coord[2];const lat=Math.abs(a)>30?a:b,lon=Math.abs(a)>30?b:a;map.flyTo({center:[lon,lat],zoom:13});return;}
const fc=await(await fetch(`/api/v1/parcels?bbox=${LIMPOPO.join(',')}&limit=500&q=${encodeURIComponent(raw)}`)).json();
if(!fc.features.length){alert('No demo parcel name matched.');return;}const f=fc.features[0],ring=f.geometry.coordinates[0];
const xs=ring.map(p=>p[0]),ys=ring.map(p=>p[1]);map.fitBounds([[Math.min(...xs),Math.min(...ys)],[Math.max(...xs),Math.max(...ys)]],{padding:60,maxZoom:13});
map.setFilter('parcels-hi',['==',['get','parcel_id'],f.properties.parcel_id]);openDossier(f.properties.parcel_id);
});
