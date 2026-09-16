"""General crop cards. Filter by month, regime and annual rain."""
from __future__ import annotations

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

CROPS = {
    "fodder": {"name": "Fodder / rest / small stock",
        "months": MONTHS, "role": "livestock first",
        "growth_days": [365, 365], "regime": ["arid"], "min_rain_mm": 0,
        "soil_plan": "At ~200 mm this is grazing country. Keep cover. Do not strip the soil for a cash crop without water.",
        "irrigation_plan": "No field irrigation plan unless you have a reliable borehole or canal. Then treat vegetables as a small irrigated garden, not the whole hectare.",
        "price_note": "Auction / speculator livestock prices, not NFPM."},
    "sorghum": {"name": "Sorghum", "months": ["Oct","Nov","Dec"], "role": "drought cereal",
        "growth_days": [90, 130], "regime": ["summer-rain", "mixed", "arid"], "min_rain_mm": 0,
        "needs_irrigation_if_arid": True,
        "soil_plan": "Only if you can water, or a rare wet start. Not a default dryland crop at 190 mm.",
        "irrigation_plan": "On arid cells this is an irrigated or opportunistic crop. Dryland sorghum wants closer to 350 mm+.",
        "price_note": "Local mill / informal."},
    "cowpeas": {"name": "Cowpeas", "months": ["Oct","Nov","Dec","Jan"], "role": "cover / cash legume",
        "growth_days": [70, 100], "regime": ["summer-rain", "mixed", "arid"], "min_rain_mm": 0,
        "needs_irrigation_if_arid": True,
        "soil_plan": "Cover or a short grain crop if water or a wet window arrives.",
        "irrigation_plan": "At 190 mm, irrigate or skip. Do not count on October rain (this cell often has <10 mm).",
        "price_note": "Informal / own use."},
    "maize": {"name": "Maize", "months": ["Oct","Nov","Dec"], "role": "summer cereal",
        "growth_days": [90, 140], "regime": ["summer-rain", "mixed"], "min_rain_mm": 550,
        "soil_plan": "Well drained loam. Lab sample before lime.",
        "irrigation_plan": "Dryland only with reliable summer rain.",
        "price_note": "SAFEX / silo."},
    "dry_beans": {"name": "Dry beans", "months": ["Nov","Dec","Jan"], "role": "summer legume",
        "growth_days": [80, 110], "regime": ["summer-rain", "mixed"], "min_rain_mm": 450,
        "soil_plan": "Follow a cereal.", "irrigation_plan": "Keep flowering moist.", "price_note": "NAMC / informal."},
    "cabbage": {"name": "Cabbage", "months": ["Feb","Mar","Apr","May","Aug","Sep"], "role": "leaf vegetable",
        "growth_days": [70, 100], "regime": ["summer-rain", "winter-rain", "mixed", "arid"], "min_rain_mm": 0,
        "needs_irrigation_if_arid": True,
        "soil_plan": "Irrigated garden crop on arid land. Cooler months only.",
        "irrigation_plan": "25–35 mm per week if dry. Not the whole 1 ha without a water source.",
        "price_note": "NFPM / NAMC. Nearest market may be hundreds of km."},
    "spinach": {"name": "Spinach / Swiss chard", "months": ["Feb","Mar","Apr","May","Aug","Sep"], "role": "leaf vegetable",
        "growth_days": [40, 70], "regime": ["summer-rain", "winter-rain", "mixed", "arid"], "min_rain_mm": 0,
        "needs_irrigation_if_arid": True,
        "soil_plan": "Cooler months. Mulch. Garden scale if arid.",
        "irrigation_plan": "15–25 mm per week if dry.",
        "price_note": "Hawkers closer than Kimberley Market."},
    "tomato": {"name": "Tomato", "months": ["Aug","Sep","Oct","Jan","Feb"], "role": "fruit vegetable",
        "growth_days": [70, 100], "regime": ["summer-rain", "mixed", "arid"], "min_rain_mm": 0,
        "needs_irrigation_if_arid": True,
        "soil_plan": "Must be irrigated. Oct–Dec on this cell is hot and dry (RH often <30%). High water and disease/heat stress.",
        "irrigation_plan": "25–40 mm per week in fruiting. Not dryland. Prefer a small bed, not the full hectare.",
        "price_note": "NFPM tomatoes. This cell is ~300 km from Kimberley Market."},
    "onion": {"name": "Onion", "months": ["Mar","Apr","May"], "role": "bulb",
        "growth_days": [120, 160], "regime": ["winter-rain", "mixed", "summer-rain", "arid"], "min_rain_mm": 0,
        "needs_irrigation_if_arid": True,
        "soil_plan": "Beds must drain. Irrigation required here.",
        "irrigation_plan": "Even moisture until bulbs swell.",
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
            item["note"] = "Only with irrigation"
        out.append(item)
    return out

def card(crop_id: str) -> dict | None:
    c = CROPS.get(crop_id)
    return {"id": crop_id, **c} if c else None
