"""General crop cards. Not a prescription and not live market prices."""
from __future__ import annotations

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

CROPS = {
    "maize": {"name": "Maize", "months": ["Oct","Nov","Dec"], "role": "summer cereal",
        "growth_days": [90, 140], "regime": ["summer-rain", "mixed"],
        "soil": "Well drained loam; pH about 5.5–7.0. Poor on waterlogged clay.",
        "soil_plan": "Do not plant into wet clay. Confirm pH with a lab sample before lime. Keep residue if the soil is sandy.",
        "irrigation": "Dryland if summer rain is reliable. Under irrigation often 400–600 mm over the season. Peak at tasselling.",
        "irrigation_plan": "If rain this week is under ~20 mm in a hot spell, plan a 20–30 mm irrigation on sand, 25–35 mm on loam. Stop if the soil is already wet.",
        "price_note": "SAFEX / silo. No live feed on Farmland yet."},
    "sorghum": {"name": "Sorghum", "months": ["Oct","Nov","Dec"], "role": "drought cereal",
        "growth_days": [90, 130], "regime": ["summer-rain", "mixed"],
        "soil": "Lighter, poorer soils than maize. Avoid frost at flowering.",
        "soil_plan": "Better than maize on drought-prone sand. Do not plant into a frost pocket.",
        "irrigation": "Often dryland. Less water than maize; still needs moisture at boot and grain fill.",
        "irrigation_plan": "Irrigate only if the rain fails at boot. 15–25 mm is usually enough on loam.",
        "price_note": "Local mill / informal. No live feed."},
    "dry_beans": {"name": "Dry beans", "months": ["Nov","Dec","Jan"], "role": "summer legume",
        "growth_days": [80, 110], "regime": ["summer-rain", "mixed"],
        "soil": "Well drained; pH about 6.0–7.0.",
        "soil_plan": "Follow a cereal. Do not lime from the map — test first. Avoid waterlogged clay.",
        "irrigation": "Sensitive to drought and waterlogging. Light, frequent water on sand if rain breaks.",
        "irrigation_plan": "Keep the top 20 cm moist at flowering. Skip a watering if clay is sticky.",
        "price_note": "NAMC / informal. No live feed."},
    "cowpeas": {"name": "Cowpeas", "months": ["Oct","Nov","Dec","Jan"], "role": "cover / cash legume",
        "growth_days": [70, 100], "regime": ["summer-rain", "mixed"],
        "soil": "Handles poorer, sandier soils. Good after a cereal.",
        "soil_plan": "Use as the nitrogen crop in the rotation. Leave residue if possible.",
        "irrigation": "Often dryland in summer-rain areas.",
        "irrigation_plan": "Irrigate only if the stand is for grain and two weeks pass with almost no rain.",
        "price_note": "Mostly informal / own use."},
    "groundnuts": {"name": "Groundnuts", "months": ["Oct","Nov"], "role": "summer legume",
        "growth_days": [120, 150], "regime": ["summer-rain"],
        "soil": "Sandy loam the pegs can enter. Not heavy clay.",
        "soil_plan": "Skip this crop on heavy clay or shallow stone.",
        "irrigation": "Even moisture at flowering and pegging.",
        "irrigation_plan": "Do not let the pegging zone dry out. Light frequent water on sand.",
        "price_note": "Processor contracts in some districts."},
    "sunflower": {"name": "Sunflower", "months": ["Nov","Dec","Jan"], "role": "summer oilseed",
        "growth_days": [90, 120], "regime": ["summer-rain", "mixed"],
        "soil": "Many soils if drained.",
        "soil_plan": "Avoid waterlogged stands and very shallow soils.",
        "irrigation": "Often dryland. Irrigation helps at budding if rain breaks.",
        "irrigation_plan": "One 20–30 mm watering at budding if the week is dry.",
        "price_note": "SAFEX sunflower. No live feed."},
    "wheat": {"name": "Wheat", "months": ["Apr","May","Jun"], "role": "winter cereal",
        "growth_days": [120, 180], "regime": ["winter-rain", "mixed"],
        "soil": "Better on heavier soils in winter-rain areas.",
        "soil_plan": "Inland summer-rain plots only with irrigation or a wet winter. Watch flowering frost.",
        "irrigation": "Western Cape often dryland. Interior usually needs water.",
        "irrigation_plan": "If you irrigate, keep moisture through stem extension. Ease off at harvest.",
        "price_note": "SAFEX wheat. No live feed."},
    "cabbage": {"name": "Cabbage", "months": ["Feb","Mar","Apr","Aug","Sep"], "role": "leaf vegetable",
        "growth_days": [70, 100], "regime": ["summer-rain", "winter-rain", "mixed"],
        "soil": "Fertile, well drained.",
        "soil_plan": "Needs a soil test before heavy fertiliser. Not a dryland crop on sand without water.",
        "irrigation": "25–35 mm per week in warm dry weather.",
        "irrigation_plan": "Shallow roots: two light waterings a week beat one flooding.",
        "price_note": "NFPM / NAMC. Not wired live."},
    "spinach": {"name": "Spinach / Swiss chard", "months": ["Feb","Mar","Apr","May","Aug","Sep"], "role": "leaf vegetable",
        "growth_days": [40, 70], "regime": ["summer-rain", "winter-rain", "mixed"],
        "soil": "Moist, fertile. Bolts in high heat.",
        "soil_plan": "Better in the cooler months on this climate. Mulch to hold water.",
        "irrigation": "15–25 mm per week if dry.",
        "irrigation_plan": "Keep the topsoil moist. Skip if rain already did that job.",
        "price_note": "Hawkers and NFPM. No live feed."},
    "tomato": {"name": "Tomato", "months": ["Aug","Sep","Oct","Jan","Feb"], "role": "fruit vegetable",
        "growth_days": [70, 100], "regime": ["summer-rain", "mixed"],
        "soil": "Well drained, not frost.",
        "soil_plan": "Stake, mulch, avoid frost months on the climate card.",
        "irrigation": "25–40 mm per week in fruiting if dry.",
        "irrigation_plan": "Water the soil, not the leaves, if you can. Cut back if fruit is cracking after rain.",
        "price_note": "NFPM tomatoes in NAMC reports."},
    "potato": {"name": "Potato", "months": ["Aug","Sep","Jan","Feb"], "role": "tuber",
        "growth_days": [90, 120], "regime": ["summer-rain", "mixed"],
        "soil": "Loose, well drained. Clay and waterlogging rot tubers.",
        "soil_plan": "Skip heavy clay cells. Need even moisture from tuber set.",
        "irrigation": "20–30 mm per week if dry.",
        "irrigation_plan": "Do not flood. Stop late so skins set.",
        "price_note": "NFPM potatoes. NAMC quarterly."},
    "onion": {"name": "Onion", "months": ["Mar","Apr","May"], "role": "bulb",
        "growth_days": [120, 160], "regime": ["winter-rain", "mixed", "summer-rain"],
        "soil": "Well drained, not waterlogged.",
        "soil_plan": "Beds must drain. Not for a wet clay patch.",
        "irrigation": "Steady moisture until bulbs swell, then ease off.",
        "irrigation_plan": "Keep even moisture early; dry off to store.",
        "price_note": "NFPM onions. NAMC quarterly."},
}

def window_months(start: str | None = None, count: int = 4) -> list[str]:
    if start and start[:3].title() in MONTHS:
        i = MONTHS.index(start[:3].title())
    else:
        import datetime
        i = datetime.date.today().month - 1
    return [MONTHS[(i + k) % 12] for k in range(count)]

def for_window(months: list[str], regime: str | None = None) -> list[dict]:
    out = []
    for cid, c in CROPS.items():
        hit = [m for m in c["months"] if m in months]
        if not hit:
            continue
        if regime and c.get("regime") and regime not in c["regime"] and regime != "mixed":
            # still show vegetables that list all regimes
            if set(c.get("regime") or []) == {"summer-rain"} and regime == "winter-rain":
                continue
            if set(c.get("regime") or []) == {"winter-rain"} and regime == "summer-rain":
                continue
        out.append({"id": cid, "name": c["name"], "role": c["role"], "plant_in": hit, "growth_days": c["growth_days"]})
    return out

def card(crop_id: str) -> dict | None:
    c = CROPS.get(crop_id)
    if not c:
        return None
    return {"id": crop_id, **c}
