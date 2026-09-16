"""General crop cards. Filter by month, regime and annual rain."""
from __future__ import annotations

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

CROPS = {
    "maize": {"name": "Maize", "months": ["Oct","Nov","Dec"], "role": "summer cereal",
        "growth_days": [90, 140], "regime": ["summer-rain", "mixed"], "min_rain_mm": 550,
        "soil_plan": "Well drained loam. Confirm pH with a lab sample.",
        "irrigation_plan": "Dryland only if summer rain is reliable. Else 400–600 mm over the season.",
        "price_note": "SAFEX / silo. No live feed."},
    "sorghum": {"name": "Sorghum", "months": ["Oct","Nov","Dec"], "role": "drought cereal",
        "growth_days": [90, 130], "regime": ["summer-rain", "mixed", "arid"], "min_rain_mm": 300,
        "soil_plan": "Better than maize on drought-prone soil.",
        "irrigation_plan": "Often dryland. Irrigate at boot if rain fails.",
        "price_note": "Local mill / informal."},
    "dry_beans": {"name": "Dry beans", "months": ["Nov","Dec","Jan"], "role": "summer legume",
        "growth_days": [80, 110], "regime": ["summer-rain", "mixed"], "min_rain_mm": 450,
        "soil_plan": "Follow a cereal. Test before lime.",
        "irrigation_plan": "Keep flowering moist. Skip if clay is wet.",
        "price_note": "NAMC / informal."},
    "cowpeas": {"name": "Cowpeas", "months": ["Oct","Nov","Dec","Jan"], "role": "cover / cash legume",
        "growth_days": [70, 100], "regime": ["summer-rain", "mixed", "arid"], "min_rain_mm": 280,
        "soil_plan": "Nitrogen crop after a cereal.",
        "irrigation_plan": "Irrigate only if grown for grain and rain fails.",
        "price_note": "Informal / own use."},
    "groundnuts": {"name": "Groundnuts", "months": ["Oct","Nov"], "role": "summer legume",
        "growth_days": [120, 150], "regime": ["summer-rain"], "min_rain_mm": 450,
        "soil_plan": "Sandy loam. Skip heavy clay.",
        "irrigation_plan": "Even moisture at pegging.",
        "price_note": "Processor contracts in some districts."},
    "sunflower": {"name": "Sunflower", "months": ["Nov","Dec","Jan"], "role": "summer oilseed",
        "growth_days": [90, 120], "regime": ["summer-rain", "mixed"], "min_rain_mm": 400,
        "soil_plan": "Needs drainage.",
        "irrigation_plan": "One watering at budding if the week is dry.",
        "price_note": "SAFEX sunflower."},
    "wheat": {"name": "Wheat", "months": ["Apr","May","Jun"], "role": "winter cereal",
        "growth_days": [120, 180], "regime": ["winter-rain", "mixed"], "min_rain_mm": 350,
        "soil_plan": "Interior only with irrigation or a wet winter.",
        "irrigation_plan": "Moisture through stem extension if you irrigate.",
        "price_note": "SAFEX wheat."},
    "cabbage": {"name": "Cabbage", "months": ["Feb","Mar","Apr","Aug","Sep"], "role": "leaf vegetable",
        "growth_days": [70, 100], "regime": ["summer-rain", "winter-rain", "mixed", "arid"], "min_rain_mm": 0,
        "needs_irrigation_if_arid": True,
        "soil_plan": "Needs water on an arid cell. Soil test before fertiliser.",
        "irrigation_plan": "25–35 mm per week if dry. Not a dryland crop at 250 mm rainfall.",
        "price_note": "NFPM / NAMC."},
    "spinach": {"name": "Spinach / Swiss chard", "months": ["Feb","Mar","Apr","May","Aug","Sep"], "role": "leaf vegetable",
        "growth_days": [40, 70], "regime": ["summer-rain", "winter-rain", "mixed", "arid"], "min_rain_mm": 0,
        "needs_irrigation_if_arid": True,
        "soil_plan": "Cooler months. Mulch.",
        "irrigation_plan": "15–25 mm per week if dry. Needs irrigation on this rainfall.",
        "price_note": "Hawkers / NFPM."},
    "tomato": {"name": "Tomato", "months": ["Aug","Sep","Oct","Jan","Feb"], "role": "fruit vegetable",
        "growth_days": [70, 100], "regime": ["summer-rain", "mixed", "arid"], "min_rain_mm": 0,
        "needs_irrigation_if_arid": True,
        "soil_plan": "Well drained. Must be irrigated on arid cells.",
        "irrigation_plan": "25–40 mm per week in fruiting if dry. Not dryland at 250 mm.",
        "price_note": "NFPM tomatoes."},
    "potato": {"name": "Potato", "months": ["Aug","Sep","Jan","Feb"], "role": "tuber",
        "growth_days": [90, 120], "regime": ["summer-rain", "mixed"], "min_rain_mm": 400,
        "soil_plan": "Skip heavy clay.",
        "irrigation_plan": "20–30 mm per week if dry.",
        "price_note": "NFPM potatoes."},
    "onion": {"name": "Onion", "months": ["Mar","Apr","May"], "role": "bulb",
        "growth_days": [120, 160], "regime": ["winter-rain", "mixed", "summer-rain", "arid"], "min_rain_mm": 0,
        "needs_irrigation_if_arid": True,
        "soil_plan": "Beds must drain.",
        "irrigation_plan": "Steady moisture until bulbs swell. Irrigation required if annual rain is low.",
        "price_note": "NFPM onions."},
}

def for_window(months: list[str], regime: str | None = None, annual_mm: float | None = None) -> list[dict]:
    out = []
    for cid, c in CROPS.items():
        hit = [m for m in c["months"] if m in months]
        if not hit:
            continue
        if regime and c.get("regime") and regime not in c["regime"]:
            continue
        if annual_mm is not None and annual_mm < (c.get("min_rain_mm") or 0):
            continue
        item = {"id": cid, "name": c["name"], "role": c["role"], "plant_in": hit, "growth_days": c["growth_days"]}
        if annual_mm is not None and annual_mm < 400 and c.get("needs_irrigation_if_arid"):
            item["note"] = "Only with irrigation on this rainfall"
        out.append(item)
    return out

def card(crop_id: str) -> dict | None:
    c = CROPS.get(crop_id)
    return {"id": crop_id, **c} if c else None
