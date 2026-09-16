#!/usr/bin/env python3
"""Farmland API + static map UI. No auth."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "parcels.geojson"
STATIC = ROOT / "static"

if not DATA.exists():
    import subprocess, sys
    subprocess.check_call([sys.executable, str(ROOT / "data" / "build_parcels.py")])
with DATA.open() as f:
    PARCELS = json.load(f)

INDEX: dict[str, dict] = {}
for feat in PARCELS["features"]:
    INDEX[feat["properties"]["parcel_id"]] = feat

LAYERS = [
    {"id": "basemap", "title": "Base map (OSM / satellite toggle)", "source": "OpenStreetMap / Esri World Imagery", "scale": "web tiles", "date": "current tiles", "type": "raster", "status": "real"},
    {"id": "parcels", "title": "Farm-portion polygons", "source": "Demo polygons in Limpopo — CSG extract not loaded", "scale": "indicative farm-portion size", "date": "2026-09-16", "type": "vector", "status": "demo"},
    {"id": "land_type", "title": "Land type / soil class", "source": "Demo labels styled on ARC Land Type; official 1:250 000 sample not loaded", "scale": "1:250000", "date": "demo", "type": "vector", "status": "demo"},
    {"id": "climate", "title": "Climate class", "source": "Demo summer-rainfall bands styled on Schulze / Limpopo climate capability", "scale": "regional", "date": "demo", "type": "vector", "status": "demo"},
    {"id": "hydro", "title": "Rivers / catchments", "source": "Named Limpopo rivers from public geography (OSM / DWS naming); distances are demo", "scale": "named watercourse", "date": "demo", "type": "vector", "status": "demo"},
    {"id": "relief", "title": "Relief", "source": "Descriptive class from location (Bushveld / Lowveld / escarpment); DEM hillshade not loaded", "scale": "regional", "date": "demo", "type": "vector", "status": "demo"},
    {"id": "settlement", "title": "Settlement class", "source": "SANLC-style town / rural / farm reclass (demo majority)", "scale": "land-cover proxy", "date": "2020", "type": "vector", "status": "demo"},
]

def bbox_of_ring(ring):
    xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
    return min(xs), min(ys), max(xs), max(ys)

def intersects(a, b):
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

def dossier(feat):
    p = feat["properties"]
    return {"parcel": {"parcel_id": p["parcel_id"], "sg_code": p.get("sg_code"), "name": p["name"], "extent_ha": p["extent_ha"], "centroid": p["centroid"]}, "intelligence": p["intelligence"], "geometry": feat["geometry"]}

def list_props(feat):
    p = feat["properties"]
    return {"parcel_id": p["parcel_id"], "sg_code": p.get("sg_code"), "name": p["name"], "extent_ha": p["extent_ha"], "layer_settlement": p.get("layer_settlement")}

app = FastAPI(title="Farmland", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"service": "farmland", "status": "available"}

@app.get("/api/v1/layers")
def layers():
    return {"layers": LAYERS, "demo": True, "note": "Demo parcels — CSG extract not loaded"}

@app.get("/api/v1/parcels")
def parcels(bbox: str | None = Query(default=None), limit: int = Query(default=200, ge=1, le=500), q: str | None = Query(default=None)):
    feats = PARCELS["features"]
    if bbox:
        w, s, e, n = [float(x.strip()) for x in bbox.split(",")]
        view = (w, s, e, n)
        feats = [f for f in feats if intersects(bbox_of_ring(f["geometry"]["coordinates"][0]), view)]
    if q and q.strip():
        needle = q.lower().strip()
        feats = [f for f in feats if needle in f["properties"]["name"].lower() or needle in f["properties"]["parcel_id"].lower()]
    feats = feats[:limit]
    return {"type": "FeatureCollection", "features": [{"type": "Feature", "id": f["properties"]["parcel_id"], "geometry": f["geometry"], "properties": list_props(f)} for f in feats]}

@app.get("/api/v1/parcels/{parcel_id}")
def parcel_one(parcel_id: str):
    feat = INDEX.get(parcel_id)
    if not feat:
        raise HTTPException(404, "parcel not found")
    return dossier(feat)

@app.get("/api/v1/parcels/{parcel_id}/intelligence")
def parcel_intel(parcel_id: str):
    feat = INDEX.get(parcel_id)
    if not feat:
        raise HTTPException(404, "parcel not found")
    body = dossier(feat)
    return {"parcel": body["parcel"], "intelligence": body["intelligence"]}

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")

app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
