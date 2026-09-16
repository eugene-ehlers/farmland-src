#!/usr/bin/env python3
"""Farmland API + static map. No auth. No demo farms."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "parcels.geojson"
STATIC = ROOT / "static"

if DATA.exists():
    with DATA.open() as f:
        PARCELS = json.load(f)
    if PARCELS.get("disclaimer") or any(
        (ft.get("properties") or {}).get("sg_code") is None
        and str((ft.get("properties") or {}).get("parcel_id", "")).startswith("fm-limpopo-")
        for ft in PARCELS.get("features") or []
    ):
        PARCELS = {"type": "FeatureCollection", "features": []}
else:
    PARCELS = {"type": "FeatureCollection", "features": []}

INDEX = {
    ft["properties"]["parcel_id"]: ft
    for ft in PARCELS.get("features") or []
    if ft.get("properties", {}).get("parcel_id")
}

LAYERS = [
    {
        "id": "basemap_osm",
        "title": "Towns, roads, rail, rivers, relief names",
        "source": "OpenStreetMap",
        "status": "loaded",
        "kind": "basemap",
        "note": "Current public map. Includes South Africa, Eswatini, Lesotho, Namibia, Botswana, Zimbabwe, Mozambique.",
    },
    {
        "id": "basemap_satellite",
        "title": "Aerial imagery",
        "source": "Esri World Imagery",
        "status": "available_not_shown",
        "kind": "basemap",
    },
    {
        "id": "parcels",
        "title": "Cadastral / farm-portion polygons",
        "source": "CSG / provincial LPI extract",
        "status": "gap",
        "kind": "grain",
        "note": "No official polygons loaded. Rows will be created from an extract, not invented.",
    },
    {
        "id": "weather_history",
        "title": "Historic weather",
        "source": "To load: SAWS stations + CHIRPS / similar public rainfall rasters",
        "status": "gap",
        "kind": "column",
        "note": "Will be sampled onto polygons once grains exist. Not invented station values.",
    },
    {
        "id": "soil",
        "title": "Soil / land type",
        "source": "DALRRD / ARC Land Type when licensed",
        "status": "gap",
        "kind": "column",
    },
    {
        "id": "agri_institutions",
        "title": "Agricultural faculties, colleges, co-ops, seed houses",
        "source": "Public directories — not loaded",
        "status": "gap",
        "kind": "poi",
    },
]

app = FastAPI(title="Farmland", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"service": "farmland", "status": "available", "parcels": len(INDEX)}


@app.get("/api/v1/layers")
def layers():
    return {
        "layers": LAYERS,
        "demo": False,
        "note": "No demo farms. Polygon rows start when an official extract is loaded.",
    }


@app.get("/api/v1/coverage")
def coverage():
    loaded = [L for L in LAYERS if L["status"] == "loaded"]
    gaps = [L for L in LAYERS if L["status"] == "gap"]
    return {"loaded": loaded, "gaps": gaps, "polygon_rows": len(INDEX)}


@app.get("/api/v1/parcels")
def parcels():
    return {"type": "FeatureCollection", "features": []}


@app.get("/api/v1/parcels/{parcel_id}")
def parcel_one(parcel_id: str):
    feat = INDEX.get(parcel_id)
    if not feat:
        raise HTTPException(404, "No official polygon loaded for this id")
    p = feat["properties"]
    return {"parcel": {"parcel_id": p["parcel_id"], "sg_code": p.get("sg_code"), "name": p.get("name")}, "geometry": feat["geometry"]}


@app.get("/api/v1/geocode")
def geocode(q: str = Query(min_length=2)):
    params = urlencode(
        {
            "q": q,
            "format": "jsonv2",
            "limit": 8,
            "countrycodes": "za,sz,ls,na,bw,zw,mz",
            "addressdetails": 1,
        }
    )
    req = Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": "Farmland/0.2 (agricultural land map; contact via github.com/eugene-ehlers/farmland-src)"},
    )
    with urlopen(req, timeout=12) as resp:
        hits = json.loads(resp.read().decode())
    out = []
    for h in hits:
        out.append(
            {
                "name": h.get("display_name"),
                "lat": float(h["lat"]),
                "lon": float(h["lon"]),
                "type": h.get("type"),
                "class": h.get("class"),
            }
        )
    return {"query": q, "results": out}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
