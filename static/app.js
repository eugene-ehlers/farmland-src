const CENTER=[24.8,-28.6];
const OSM={version:8,sources:{osm:{type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,attribution:'© OpenStreetMap'},esri:{type:'raster',tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],tileSize:256,attribution:'Esri World Imagery'}},layers:[{id:'osm',type:'raster',source:'osm'}]};
const map=new maplibregl.Map({
  container:'map',style:OSM,center:CENTER,zoom:5,
  maxBounds:[[9.5,-36.8],[41.5,-15.2]]
});
map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-left');
function esc(s){return String(s??'').replace(/&/g,'&').replace(/</g,'<').replace(/>/g,'>')}
document.getElementById('close-dossier').onclick=()=>{document.getElementById('dossier').hidden=true};
function showPlace(hit){
  map.flyTo({center:[hit.lon,hit.lat],zoom:hit.class==='place'?10:11});
  const el=document.getElementById('dossier-body');
  el.innerHTML=`<h2>${esc(hit.name)}</h2><div class="meta">${esc(hit.class||'')} / ${esc(hit.type||'')}</div>
    <div class="block"><h3>On this map now</h3><p>OpenStreetMap towns, roads, rail, rivers and named relief.</p></div>
    <div class="block"><h3>Not loaded yet</h3><p>Official land polygons, historic weather sampled to land, soil / land type, faculties, co-ops and seed houses.</p></div>`;
  document.getElementById('dossier').hidden=false;
}
document.getElementById('search-form').addEventListener('submit',async e=>{
  e.preventDefault();
  const raw=document.getElementById('search').value.trim();
  if(!raw)return;
  const coord=raw.match(/^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/);
  if(coord){
    const a=+coord[1],b=+coord[2];
    const lat=Math.abs(a)>15?a:b,lon=Math.abs(a)>15?b:a;
    map.flyTo({center:[lon,lat],zoom:11});
    return;
  }
  const data=await(await fetch('/api/v1/geocode?q='+encodeURIComponent(raw))).json();
  if(!data.results||!data.results.length){alert('No town or place matched in southern Africa.');return;}
  showPlace(data.results[0]);
});
