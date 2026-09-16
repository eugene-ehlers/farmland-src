"""Nearest National Fresh Produce Markets. Distances only. Prices are a gap until an official feed."""
from __future__ import annotations
import math

# Approximate gate coordinates. Size class from Competition Commission FPMI (2025).
MARKETS = [
    {"id": "jhb", "name": "Johannesburg Market (City Deep)", "lat": -26.217, "lon": 28.183, "size": "large", "small_lot": False},
    {"id": "tsh", "name": "Tshwane Fresh Produce Market", "lat": -25.737, "lon": 28.189, "size": "large", "small_lot": False},
    {"id": "cpt", "name": "Cape Town Market (Epping)", "lat": -33.932, "lon": 18.540, "size": "large", "small_lot": False},
    {"id": "dbn", "name": "Durban Fresh Produce Market (Clairwood)", "lat": -29.905, "lon": 30.980, "size": "large", "small_lot": False},
    {"id": "spr", "name": "Ekurhuleni / Springs Market", "lat": -26.255, "lon": 28.442, "size": "medium", "small_lot": False},
    {"id": "bfn", "name": "Mangaung Fresh Produce Market", "lat": -29.133, "lon": 26.246, "size": "medium", "small_lot": False},
    {"id": "plz", "name": "Gqeberha Fresh Produce Market", "lat": -33.870, "lon": 25.550, "size": "medium", "small_lot": False},
    {"id": "pzb", "name": "Msunduzi / Pietermaritzburg Market", "lat": -29.600, "lon": 30.380, "size": "medium", "small_lot": False},
    {"id": "els", "name": "Buffalo City / East London Market", "lat": -33.001, "lon": 27.903, "size": "medium", "small_lot": False},
    {"id": "kdp", "name": "Matlosana / Klerksdorp Market", "lat": -26.871, "lon": 26.666, "size": "medium", "small_lot": False},
    {"id": "wlk", "name": "Matjhabeng / Welkom Market", "lat": -27.977, "lon": 26.735, "size": "medium", "small_lot": False},
    {"id": "kim", "name": "Sol Plaatje / Kimberley Market", "lat": -28.732, "lon": 24.762, "size": "small", "small_lot": True},
    {"id": "rtb", "name": "Rustenburg Fresh Produce Market", "lat": -25.667, "lon": 27.242, "size": "small", "small_lot": True},
    {"id": "grg", "name": "Garden Route / George Market", "lat": -33.964, "lon": 22.460, "size": "small", "small_lot": True},
    {"id": "mth", "name": "King Sabata Dalindyebo / Mthatha Market", "lat": -31.589, "lon": 28.790, "size": "small", "small_lot": True},
    {"id": "qnc", "name": "Qonce Market", "lat": -32.877, "lon": 27.394, "size": "small", "small_lot": True},
]

def _km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 1)

def nearest(lat: float, lon: float, n: int = 4) -> dict:
    ranked = []
    for m in MARKETS:
        km = _km(lat, lon, m["lat"], m["lon"])
        ranked.append({
            "id": m["id"],
            "name": m["name"],
            "km": km,
            "size": m["size"],
            "fits_crate_lots": m["small_lot"] or m["size"] == "medium",
            "note": "Commission market. Small lots usually go through an agent or a local hawkers' channel, not a full pallet to City Deep.",
        })
    ranked.sort(key=lambda x: x["km"])
    top = ranked[:n]
    return {
        "source": "Curated NFPM list (Competition Commission FPMI + published market addresses). Coordinates approximate.",
        "price_status": "gap",
        "price_note": "No live NFPM price API on this service. NAMC quarterly smallholder reports and each market's own price board are the public sources.",
        "logistics_status": "gap",
        "logistics_note": "Distance is road-crow-fly km. Rand per trip needs a bakkie/taxi tariff we do not invent.",
        "nearest": top,
        "hint": "A smallholder selling crates often does better at the closest medium/small market or the local informal market than at Joburg Market.",
    }
