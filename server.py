#!/usr/bin/env python3
from __future__ import annotations
import json, math
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

STATIC = Path(__file__).resolve().parent / "static"
UA = "Farmland/0.4 (github.com/eugene-ehlers/farmland-src)"
# ~1.1 km cells. Covers RSA + Namibia, Botswana, Zimbabwe, Mozambique, Lesotho, Eswatini.
STEP = 0.01
ORIGIN_W, ORIGIN_S = 11.50, -35.80
ORIGIN_E, ORIGIN_N = 36.20, -15.40

app = FastAPI(title="Farmland", version="0.4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])

def get_json(url, timeout=12):
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def ix_iy(lon, lat):
    return int(math.floor((lon - ORIGIN_W) / STEP)), int(math.floor((lat - ORIGIN_S) / STEP))

def cell_bounds(ix, iy):
    w = ORIGIN_W + ix * STEP
    s = ORIGIN_S + iy * STEP
    return w, s, w + STEP, s + STEP

def cell_id(ix, iy):
    return f"g:{ix}:{iy}"

def parse_id(pid: str):
    parts = pid.split(":")
    if len(parts) != 3 or parts[0] != "g":
        return None
    try:
        return int(parts[1]), int(parts[2])
    except ValueError:
        return None

def cell_feature(ix, iy):
    w, s, e, n = cell_bounds(ix, iy)
    mid_lat = (s + n) / 2
    ha = round(abs((e - w) * 111_320.0 * math.cos(math.radians(mid_lat)) * (n - s) * 110_540.0) / 10_000.0, 1)
    pid = cell_id(ix, iy)
    return {
        "type": "Feature",
        "id": pid,
        "geometry": {"type": "Polygon", "coordinates": [[[round(w,5),round(s,5)],[round(e,5),round(s,5)],[round(e,5),round(n,5)],[round(w,5),round(n,5)],[round(w,5),round(s,5)]]]},
        "properties": {
            "parcel_id": pid,
            "sg_code": None,
            "name": f"Analysis cell {pid}",
            "extent_ha": ha,
            "kind": "grid",
            "step_deg": STEP,
            "source": "Coordinate grid. Not a cadastral farm portion.",
        },
    }

@app.get("/health")
def health():
    return {"service": "farmland", "status": "available", "grid_step_deg": STEP}

@app.get("/api/v1/layers")
def layers():
    return {"demo": False, "layers": [
        {"id": "basemap_osm", "status": "loaded", "source": "OpenStreetMap"},
        {"id": "parcels", "status": "loaded", "source": f"Analysis grid {STEP} deg (~1 km). Full coverage of the southern Africa frame."},
        {"id": "cadastre", "status": "gap", "note": "Legal CSG farm portions can join later; they are not the grain."},
        {"id": "weather_history", "status": "gap"},
        {"id": "soil", "status": "gap"},
    ]}

@app.get("/api/v1/coverage")
def coverage():
    return {"polygon_source": "coordinate grid", "step_deg": STEP, "sg_code": None, "gaps": ["weather_history", "soil", "cadastre"]}

@app.get("/api/v1/parcels")
def parcels(bbox: str | None = Query(default=None), limit: int = Query(default=400, ge=1, le=800)):
    if not bbox:
        return {"type": "FeatureCollection", "features": [], "note": "Pass bbox=W,S,E,N"}
    try:
        w, s, e, n = [float(x.strip()) for x in bbox.split(",")]
    except ValueError:
        raise HTTPException(400, "bbox must be W,S,E,N")
    w = max(w, ORIGIN_W); s = max(s, ORIGIN_S); e = min(e, ORIGIN_E); n = min(n, ORIGIN_N)
    if e <= w or n <= s:
        return {"type": "FeatureCollection", "features": []}
    if (e - w) > 0.55 or (n - s) > 0.55:
        return {"type": "FeatureCollection", "features": [], "note": "Zoom in to draw analysis cells"}
    ix0, iy0 = ix_iy(w + 1e-9, s + 1e-9)
    ix1, iy1 = ix_iy(e - 1e-9, n - 1e-9)
    feats = []
    truncated = False
    for iy in range(iy0, iy1 + 1):
        for ix in range(ix0, ix1 + 1):
            if len(feats) >= limit:
                truncated = True
                break
            feats.append(cell_feature(ix, iy))
        if truncated:
            break
    return {"type": "FeatureCollection", "features": feats, "source": "grid", "count": len(feats), "truncated": truncated}

@app.get("/api/v1/parcels/{parcel_id}")
def parcel_one(parcel_id: str):
    parsed = parse_id(parcel_id)
    if not parsed:
        raise HTTPException(404, "not a grid cell id")
    ft = cell_feature(*parsed)
    return {"parcel": ft["properties"], "geometry": ft["geometry"], "intelligence": {}}

@app.get("/api/v1/geocode")
def geocode(q: str = Query(min_length=2)):
    hits = get_json("https://nominatim.openstreetmap.org/search?" + urlencode({"q": q, "format": "jsonv2", "limit": 8, "countrycodes": "za,sz,ls,na,bw,zw,mz"}), timeout=12)
    return {"query": q, "results": [{"name": h.get("display_name"), "lat": float(h["lat"]), "lon": float(h["lon"]), "type": h.get("type"), "class": h.get("class")} for h in hits]}

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")

app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
