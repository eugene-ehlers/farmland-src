#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
sys.path.insert(0, str(ROOT / "data"))
from chirps import monthly_chirps  # type: ignore
from soil import soilgrids, notes as soil_notes  # type: ignore

UA = "Farmland/0.8 (github.com/eugene-ehlers/farmland-src)"
STEP = 0.001
ORIGIN_W, ORIGIN_S = 11.50, -35.80
ORIGIN_E, ORIGIN_N = 36.20, -15.40
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
CLIMATE_CACHE: dict[str, dict] = {}
SOIL_CACHE: dict[str, dict] = {}

app = FastAPI(title="Farmland", version="0.8.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])

def get_json(url, timeout=40):
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
    mid_lat = (s + n) / 2.0
    mid_lon = (w + e) / 2.0
    ha = round(abs((e - w) * 111_320.0 * math.cos(math.radians(mid_lat)) * (n - s) * 110_540.0) / 10_000.0, 2)
    pid = cell_id(ix, iy)
    return {
        "type": "Feature",
        "id": pid,
        "geometry": {"type": "Polygon", "coordinates": [[[round(w,6),round(s,6)],[round(e,6),round(s,6)],[round(e,6),round(n,6)],[round(w,6),round(n,6)],[round(w,6),round(s,6)]]]},
        "properties": {
            "parcel_id": pid,
            "sg_code": None,
            "name": f"Analysis cell {pid}",
            "extent_ha": ha,
            "kind": "grid",
            "step_deg": STEP,
            "centroid": [round(mid_lon, 5), round(mid_lat, 5)],
            "source": "Coordinate grid (~1 ha). Not a cadastral farm portion.",
        },
    }

def _avg(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 2) if xs else None

def climate_for(lat: float, lon: float) -> dict:
    key = f"{lat:.4f},{lon:.4f}"
    if key in CLIMATE_CACHE:
        return CLIMATE_CACHE[key]
    params = {
        "latitude": f"{lat:.4f}",
        "longitude": f"{lon:.4f}",
        "start_date": "2015-01-01",
        "end_date": "2024-12-31",
        "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,shortwave_radiation_sum",
        "timezone": "Africa/Johannesburg",
    }
    data = get_json("https://archive-api.open-meteo.com/v1/archive?" + urlencode(params))
    daily = data.get("daily") or {}
    times = daily.get("time") or []
    buckets = {m: {"t": [], "tx": [], "tn": [], "p": [], "h": [], "s": []} for m in range(1, 13)}
    for i, day in enumerate(times):
        m = int(day[5:7])
        b = buckets[m]
        if daily.get("temperature_2m_mean"): b["t"].append(daily["temperature_2m_mean"][i])
        if daily.get("temperature_2m_max"): b["tx"].append(daily["temperature_2m_max"][i])
        if daily.get("temperature_2m_min"): b["tn"].append(daily["temperature_2m_min"][i])
        if daily.get("precipitation_sum"): b["p"].append(daily["precipitation_sum"][i])
        if daily.get("relative_humidity_2m_mean"): b["h"].append(daily["relative_humidity_2m_mean"][i])
        if daily.get("shortwave_radiation_sum"): b["s"].append(daily["shortwave_radiation_sum"][i])
    chirps = None
    try:
        chirps = monthly_chirps(lat, lon)
    except Exception:
        chirps = None
    monthly = []
    rain_year = 0.0
    for m in range(1, 13):
        b = buckets[m]
        rain_days = [x for x in b["p"] if x is not None]
        monthly_rain = round(sum(rain_days) / 10.0, 1) if rain_days else None
        if monthly_rain is not None:
            rain_year += monthly_rain
        chirps_m = chirps["monthly_mm"][m-1] if chirps else None
        monthly.append({
            "month": MONTHS[m - 1],
            "rain_mm": monthly_rain,
            "rain_chirps_mm": chirps_m,
            "t_mean_c": _avg(b["t"]),
            "t_max_c": _avg(b["tx"]),
            "t_min_c": _avg(b["tn"]),
            "rh_pct": _avg(b["h"]),
            "sun_mj_m2": _avg(b["s"]),
        })
    out = {
        "period": "2015-01-01 to 2024-12-31",
        "source": "ERA5 via Open-Meteo. Not a SAWS station.",
        "chirps_source": "CHIRPS v2 via ClimateSERV (~5 km, station+satellite rain)",
        "scale": "ERA5 ~9-25 km; CHIRPS ~5 km; sampled at cell centroid",
        "confidence": "indicative historic climate",
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "elevation_m": data.get("elevation"),
        "annual_rain_mm": round(rain_year, 0),
        "annual_chirps_mm": chirps["annual_mm"] if chirps else None,
        "monthly": monthly,
    }
    CLIMATE_CACHE[key] = out
    return out

@app.get("/health")
def health():
    return {"service": "farmland", "status": "available", "grid_step_deg": STEP}

@app.get("/api/v1/layers")
def layers():
    return {"demo": False, "layers": [
        {"id": "weather_era5", "status": "loaded_on_demand"},
        {"id": "weather_chirps", "status": "loaded_on_demand"},
        {"id": "soil_grids", "status": "loaded_on_demand", "source": "SoilGrids 250m where ISRIC returns a value"},
        {"id": "soil_lab", "status": "gap", "note": "Once-off plot analysis stored later on these cell ids"},
    ]}

@app.get("/api/v1/parcels")
def parcels(bbox: str | None = Query(default=None), limit: int = Query(default=500, ge=1, le=900)):
    if not bbox:
        return {"type": "FeatureCollection", "features": []}
    w, s, e, n = [float(x.strip()) for x in bbox.split(",")]
    w = max(w, ORIGIN_W); s = max(s, ORIGIN_S); e = min(e, ORIGIN_E); n = min(n, ORIGIN_N)
    if e <= w or n <= s or (e - w) > 0.12 or (n - s) > 0.12:
        return {"type": "FeatureCollection", "features": [], "note": "Zoom in further to draw ~1 ha cells"}
    ix0, iy0 = ix_iy(w + 1e-12, s + 1e-12)
    ix1, iy1 = ix_iy(e - 1e-12, n - 1e-12)
    feats, truncated = [], False
    for iy in range(iy0, iy1 + 1):
        for ix in range(ix0, ix1 + 1):
            if len(feats) >= limit:
                truncated = True
                break
            feats.append(cell_feature(ix, iy))
        if truncated:
            break
    return {"type": "FeatureCollection", "features": feats, "count": len(feats), "truncated": truncated}

@app.get("/api/v1/parcels/{parcel_id}")
def parcel_one(parcel_id: str):
    parsed = parse_id(parcel_id)
    if not parsed:
        raise HTTPException(404, "not a grid cell id")
    ft = cell_feature(*parsed)
    return {"parcel": ft["properties"], "geometry": ft["geometry"]}

@app.get("/api/v1/parcels/{parcel_id}/climate")
def parcel_climate(parcel_id: str):
    parsed = parse_id(parcel_id)
    if not parsed:
        raise HTTPException(404, "not a grid cell id")
    lon, lat = cell_feature(*parsed)["properties"]["centroid"]
    return {"parcel_id": parcel_id, "climate": climate_for(lat, lon)}

@app.get("/api/v1/parcels/{parcel_id}/soil")
def parcel_soil(parcel_id: str):
    parsed = parse_id(parcel_id)
    if not parsed:
        raise HTTPException(404, "not a grid cell id")
    lon, lat = cell_feature(*parsed)["properties"]["centroid"]
    key = f"{lat:.4f},{lon:.4f}"
    if key not in SOIL_CACHE:
        try:
            sg = soilgrids(lat, lon)
        except Exception as exc:
            sg = {"has_values": False, "source": f"SoilGrids failed: {exc}"}
        try:
            climate = climate_for(lat, lon)
        except Exception:
            climate = None
        SOIL_CACHE[key] = {"soil": sg, "notes": soil_notes(sg, climate)}
    return {"parcel_id": parcel_id, **SOIL_CACHE[key]}

@app.get("/api/v1/geocode")
def geocode(q: str = Query(min_length=2)):
    hits = get_json("https://nominatim.openstreetmap.org/search?" + urlencode({"q": q, "format": "jsonv2", "limit": 8, "countrycodes": "za,sz,ls,na,bw,zw,mz"}), timeout=12)
    return {"query": q, "results": [{"name": h.get("display_name"), "lat": float(h["lat"]), "lon": float(h["lon"]), "type": h.get("type"), "class": h.get("class")} for h in hits]}

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")

app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
