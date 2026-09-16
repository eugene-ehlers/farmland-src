"""General crop cards for SA smallholdings. Not a prescription and not live market prices."""
from __future__ import annotations

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

CROPS = {
    "maize": {
        "name": "Maize",
        "months": ["Oct","Nov","Dec"],
        "role": "summer cereal",
        "soil": "Well drained loam; pH about 5.5–7.0. Poor on waterlogged clay.",
        "irrigation": "Dryland if summer rain is reliable. Under irrigation, often 400–600 mm over the season, more in sandy soil. Peak demand around tasselling.",
        "water_mm_season": [400, 600],
        "price_status": "gap",
        "price_note": "Use SAFEX / silo price, not NFPM. No live feed on Farmland yet.",
    },
    "sorghum": {
        "name": "Sorghum",
        "months": ["Oct","Nov","Dec"],
        "role": "drought cereal",
        "soil": "Tolerates lighter, poorer soils than maize. Avoid frost at flowering.",
        "irrigation": "Often dryland. If irrigated, less water than maize; still needs moisture at boot and grain fill.",
        "water_mm_season": [350, 500],
        "price_status": "gap",
        "price_note": "Local mill / informal market. No live feed.",
    },
    "dry_beans": {
        "name": "Dry beans",
        "months": ["Nov","Dec","Jan"],
        "role": "summer legume",
        "soil": "Well drained; pH about 6.0–7.0. Does not like acid sand without lime confirmed by a test.",
        "irrigation": "Sensitive to both drought and waterlogging. Light, frequent water on sand if the rain breaks.",
        "water_mm_season": [300, 450],
        "price_status": "gap",
        "price_note": "NAMC / informal. No live feed.",
    },
    "cowpeas": {
        "name": "Cowpeas",
        "months": ["Oct","Nov","Dec","Jan"],
        "role": "cover / cash legume",
        "soil": "Handles poorer, sandier soils. Good rotation after a cereal.",
        "irrigation": "Often dryland in summer-rain areas. Irrigate only if the stand is for grain and rain fails.",
        "water_mm_season": [250, 400],
        "price_status": "gap",
        "price_note": "Mostly informal / own use.",
    },
    "groundnuts": {
        "name": "Groundnuts",
        "months": ["Oct","Nov"],
        "role": "summer legume",
        "soil": "Sandy loam that the pegs can enter. Not heavy clay.",
        "irrigation": "Needs even moisture at flowering and pegging. Dryland only where summer rain is dependable.",
        "water_mm_season": [400, 550],
        "price_status": "gap",
        "price_note": "Processor contracts in some districts.",
    },
    "sunflower": {
        "name": "Sunflower",
        "months": ["Nov","Dec","Jan"],
        "role": "summer oilseed",
        "soil": "Many soils if drained. Avoid waterlogged stands.",
        "irrigation": "Often dryland. Irrigation helps at budding if the rain breaks.",
        "water_mm_season": [350, 500],
        "price_status": "gap",
        "price_note": "SAFEX sunflower. No live feed here.",
    },
    "wheat": {
        "name": "Wheat",
        "months": ["Apr","May","Jun"],
        "role": "winter cereal",
        "soil": "Better on heavier soils in winter-rain areas. Frost at flowering is a risk inland.",
        "irrigation": "Winter-rain Western Cape often dryland. Summer-rain interior only with irrigation or a very wet winter.",
        "water_mm_season": [350, 550],
        "price_status": "gap",
        "price_note": "SAFEX wheat. No live feed here.",
    },
    "cabbage": {
        "name": "Cabbage",
        "months": ["Feb","Mar","Apr","Aug","Sep"],
        "role": "leaf vegetable",
        "soil": "Fertile, well drained. Needs a soil test before heavy fertiliser.",
        "irrigation": "Shallow roots: frequent light water. Roughly 25–35 mm per week in warm weather if there is no rain.",
        "water_mm_season": [350, 500],
        "price_status": "gap",
        "price_note": "NFPM cabbage prices are public on market boards and in NAMC reports — not wired live.",
    },
    "spinach": {
        "name": "Spinach / Swiss chard",
        "months": ["Feb","Mar","Apr","May","Aug","Sep"],
        "role": "leaf vegetable",
        "soil": "Moist, fertile. Bolts in high heat.",
        "irrigation": "Keep the topsoil moist. Often 15–25 mm per week if dry.",
        "water_mm_season": [250, 400],
        "price_status": "gap",
        "price_note": "Local hawkers and NFPM. No live feed.",
    },
    "tomato": {
        "name": "Tomato",
        "months": ["Aug","Sep","Oct","Jan","Feb"],
        "role": "fruit vegetable",
        "soil": "Well drained, not frost. Staking and disease pressure are the real limits.",
        "irrigation": "Regular water; avoid wet leaves if you can. Roughly 25–40 mm per week in fruiting if dry.",
        "water_mm_season": [400, 600],
        "price_status": "gap",
        "price_note": "NFPM tomatoes are a main price series in NAMC reports.",
    },
    "potato": {
        "name": "Potato",
        "months": ["Aug","Sep","Jan","Feb"],
        "role": "tuber",
        "soil": "Loose, well drained. Heavy clay and waterlogging rot tubers.",
        "irrigation": "Even moisture from tuber set. Dryland only in reliable rain. Often 20–30 mm per week if dry.",
        "water_mm_season": [350, 550],
        "price_status": "gap",
        "price_note": "Potatoes dominate many NFPM volumes. NAMC quarterly. No live feed.",
    },
    "onion": {
        "name": "Onion",
        "months": ["Mar","Apr","May"],
        "role": "bulb",
        "soil": "Well drained, not waterlogged.",
        "irrigation": "Steady moisture until bulbs swell, then ease off to store.",
        "water_mm_season": [350, 500],
        "price_status": "gap",
        "price_note": "NFPM onions. NAMC quarterly. No live feed.",
    },
}

def for_month(month: str) -> list[dict]:
    m = month[:3].title()
    out = []
    for cid, c in CROPS.items():
        if m in c["months"]:
            out.append({"id": cid, **{k: c[k] for k in ("name", "role", "months")}})
    return out

def card(crop_id: str) -> dict | None:
    c = CROPS.get(crop_id)
    if not c:
        return None
    return {"id": crop_id, **c}
