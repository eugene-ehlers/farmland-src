"""Indicative enterprises from climate + soil. Not a record of what was grown on this plot."""
from __future__ import annotations

SUMMER = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
WINTER = ["May", "Jun", "Jul", "Aug"]

def _rain(climate, months):
    m = {x["month"]: x.get("rain_mm") or 0 for x in (climate or {}).get("monthly") or []}
    return sum(m.get(n, 0) for n in months)

def year_plan(climate: dict | None, soil: dict | None) -> dict:
    climate = climate or {}
    soil = soil or {}
    annual = climate.get("annual_rain_mm")
    summer = _rain(climate, SUMMER)
    winter = _rain(climate, WINTER)
    monthly = climate.get("monthly") or []
    frost = [m["month"] for m in monthly if (m.get("t_min_c") or 99) < 3]
    warm = [m["month"] for m in monthly if (m.get("t_mean_c") or 0) >= 18]
    tex = soil.get("texture_class")
    ph = soil.get("ph_water")
    regime = "summer-rain" if summer >= winter * 1.3 else ("winter-rain" if winter >= summer * 1.1 else "mixed")

    slots = []
    if regime == "winter-rain":
        slots.append({"window": "Apr–Oct", "role": "main", "examples": ["wheat", "barley", "canola", "oats"], "why": "Winter-rain pattern in the 10-year climate."})
        slots.append({"window": "Nov–Mar", "role": "cover / veg", "examples": ["cover mix", "cowpeas if irrigated", "leaf vegetables if water"], "why": "Dry summer in this climate unless you irrigate."})
    else:
        slots.append({"window": "Oct–Mar", "role": "main", "examples": ["maize", "sorghum", "dry beans", "cowpeas", "groundnuts", "sunflower"], "why": "Summer-rain pattern. Beans/cowpeas in the rotation fix nitrogen."})
        slots.append({"window": "Apr–Aug", "role": "cover / rest / winter veg", "examples": ["grazing vetch", "oats forage", "fallow with cover", "cabbage/spinach if frost and water allow"], "why": "Dry, cooler months. Rest or a cover stops the soil going bare."})

    if annual is not None and annual < 450:
        slots[0]["examples"] = ["sorghum", "cowpeas", "millet", "drought vegetables under irrigation"]
        slots[0]["why"] += " Annual rain is low for dryland maize."
    if tex in ("sandy", "sandy loam"):
        slots.append({"window": "any irrigated slot", "role": "caution", "examples": ["smaller irrigation doses", "mulch"], "why": "Light soil does not hold a big watering."})
    if tex in ("clay", "clay loam"):
        slots.append({"window": "wet months", "role": "caution", "examples": ["avoid working wet clay", "ridge vegetables"], "why": "Heavy soil waterlogs easily."})
    if ph is not None and ph < 5.5:
        slots.append({"window": "before cash crop", "role": "soil", "examples": ["lab test + lime if the test says so", "beans after a cereal"], "why": "Predicted pH is acid. Do not guess a lime bag from the map."})

    rotation = [
        "Year A summer: cereal (maize or sorghum) if rain allows",
        "Year A winter / cover: legume cover or forage",
        "Year B summer: legume cash (beans, cowpeas) or mixed vegetables",
        "Year B winter: rest or light cover — do not leave the plot bare",
    ]
    return {
        "kind": "climate_fit",
        "not": "Historic crop success on this hectare. We do not have plot yields.",
        "rain_regime": regime,
        "annual_rain_mm": annual,
        "summer_rain_mm": round(summer, 0),
        "winter_rain_mm": round(winter, 0),
        "warm_months": warm,
        "frost_risk_months": frost,
        "slots": slots,
        "rotation_idea": rotation,
        "next": "Store what this farmer actually plants and harvests on these cell ids. That becomes the real success record.",
    }
