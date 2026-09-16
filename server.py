#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

STATIC = Path(__file__).resolve().parent / "static"
CSG = "https://dffeportal.environment.gov.za/hosting/rest/services/CSG_Cadaster/CSG_Cadastral_Data/MapServer/1/query"
UA = "Farmland/0.3 (github.com/eugene-ehlers/farmland-src)"
FIELDS = "PRCL_KEY,PRCL_TYPE,PROVINCE,MAJ_REGION,PARCEL_NO,PORTION,GEOM_AREA,ID"

app = FastAPI(title="Farmland", version="0.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])

def get_json(url, timeout=25):
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def to_feat(raw):
    a = raw.get("attributes") or {}
    rings = (raw.get("geometry") or {}).get("rings") or []
    coords = [[[round(p[0], 6), round(p[1], 6)] for p in ring] for ring in rings]
    key = a.get("PRCL_KEY") or a.get("ID")
    area = a.get("GEOM_AREA")
    ha = None
    if area is not None:
        v = float(area)
        ha = round(v / 10000.0, 2) if v > 1000 else round(v, 2)
    return {
        "type": "Feature",
        "id": key,
        "geometry": {"type": "Polygon", "coordinates": coords},
        "properties": {
            "parcel_id": key,
            "sg_code": key,
            "name": f"Portion {a.get('PORTION')} of farm {a.get('PARCEL_NO')} ({a.get('MAJ_REGION') or ''})",
            "extent_ha": ha,
            "province": a.get("PROVINCE"),
            "maj_region": a.get("MAJ_REGION"),
            "parcel_no": a.get("PARCEL_NO"),
            "portion": a.get("PORTION"),
            "prcl_type": a.get("PRCL_TYPE"),
            "source": "CSG farm portion",
        },
    }

@app.get("/health")
def health():
    return {"service": "farmland", "status": "available"}

@app.get("/api/v1/layers")
def layers():
    return {"demo": False, "layers": [
        {"id": "basemap_osm", "status": "loaded", "source": "OpenStreetMap"},
        {"id": "parcels", "status": "loaded_on_demand", "source": "CSG farm portions via DFFE"},
        {"id": "weather_history", "status": "gap"},
        {"id": "soil", "status": "gap"},
    ]}

@app.get("/api/v1/coverage")
def coverage():
    return {"polygon_source": "CSG farm portions, bbox query", "gaps": ["weather_history", "soil"]}

@app.get("/api/v1/parcels")
def parcels(bbox: str | None = Query(default=None), limit: int = Query(default=200, ge=1, le=400)):
    if not bbox:
        return {"type": "FeatureCollection", "features": [], "note": "Pass bbox=W,S,E,N"}
    try:
        w, s, e, n = [float(x.strip()) for x in bbox.split(",")]
    except ValueError:
        raise HTTPException(400, "bbox must be W,S,E,N")
    if e < w or n < s:
        raise HTTPException(400, "bbox order W,S,E,N")
    if (e - w) > 1.2 or (n - s) > 1.2:
        return {"type": "FeatureCollection", "features": [], "note": "Zoom in to load farm portions"}
    params = {
        "f": "json", "where": "1=1", "outFields": FIELDS, "returnGeometry": "true",
        "geometry": f"{w},{s},{e},{n}", "geometryType": "esriGeometryEnvelope",
        "inSR": "4326", "outSR": "4326", "spatialRel": "esriSpatialRelIntersects",
        "resultRecordCount": str(limit),
    }
    try:
        data = get_json(CSG + "?" + urlencode(params))
    except Exception as exc:
        raise HTTPException(502, f"CSG query failed: {exc}") from exc
    if data.get("error"):
        raise HTTPException(502, str(data["error"]))
    feats = [to_feat(ft) for ft in data.get("features") or [] if ft.get("geometry")]
    return {"type": "FeatureCollection", "features": feats, "source": "CSG", "count": len(feats), "truncated": bool(data.get("exceededTransferLimit"))}

@app.get("/api/v1/parcels/{parcel_id}")
def parcel_one(parcel_id: str):
    safe = parcel_id.replace("'", "")
    data = get_json(CSG + "?" + urlencode({"f": "json", "where": f"PRCL_KEY='{safe}'", "outFields": FIELDS, "returnGeometry": "true", "outSR": "4326", "resultRecordCount": "1"}))
    feats = data.get("features") or []
    if not feats:
        raise HTTPException(404, "parcel not found")
    ft = to_feat(feats[0])
    return {"parcel": ft["properties"], "geometry": ft["geometry"], "intelligence": {}}

@app.get("/api/v1/geocode")
def geocode(q: str = Query(min_length=2)):
    hits = get_json("https://nominatim.openstreetmap.org/search?" + urlencode({"q": q, "format": "jsonv2", "limit": 8, "countrycodes": "za,sz,ls,na,bw,zw,mz"}), timeout=12)
    return {"query": q, "results": [{"name": h.get("display_name"), "lat": float(h["lat"]), "lon": float(h["lon"]), "type": h.get("type"), "class": h.get("class")} for h in hits]}

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")

app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
