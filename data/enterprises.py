"""Indicative enterprises from climate + soil. Not plot yields."""
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
    tex = soil.get("texture_class")
    ph = soil.get("ph_water")

    if annual is not None and annual < 400:
        regime = "arid"
    elif summer >= winter * 1.3 and (annual or 0) >= 400:
        regime = "summer-rain"
    elif winter >= summer * 1.1:
        regime = "winter-rain"
    else:
        regime = "mixed"

    if regime == "arid":
        slots = [
            {"window": "Any month", "role": "main", "examples": ["drought vegetables under irrigation", "sorghum if a wet spell", "small stock / fodder"],
             "why": f"About {annual:.0f} mm a year. That is not a dryland maize climate. Water or a very hardy crop."},
            {"window": "Year-round", "role": "cover", "examples": ["do not leave soil bare", "mulch", "light cover if it germinates"],
             "why": "Low, even rain. A bare plot blows and bakes."},
        ]
        rotation = [
            "Do not plan dryland maize on this rainfall.",
            "If you have water: short vegetables in the cooler months, sorghum or cowpeas only if a wet window arrives.",
            "If you do not have water: fodder / small stock / rest with cover — this is not a grain hectare.",
        ]
    elif regime == "winter-rain":
        slots = [
            {"window": "Apr–Oct", "role": "main", "examples": ["wheat", "barley", "canola", "oats"], "why": "Winter-rain pattern."},
            {"window": "Nov–Mar", "role": "cover / veg", "examples": ["cover", "irrigated vegetables"], "why": "Dry summer unless you irrigate."},
        ]
        rotation = ["Winter cereal", "Summer cover or irrigated veg", "Do not leave the plot bare"]
    else:
        slots = [
            {"window": "Oct–Mar", "role": "main", "examples": ["maize", "sorghum", "dry beans", "cowpeas", "sunflower"], "why": "Summer-rain pattern."},
            {"window": "Apr–Aug", "role": "cover", "examples": ["legume cover", "oats forage", "cabbage if frost and water allow"], "why": "Cooler, drier months."},
        ]
        rotation = ["Summer cereal", "Winter legume cover", "Summer beans or vegetables", "Winter rest or cover"]
        if annual is not None and annual < 550:
            slots[0]["examples"] = ["sorghum", "cowpeas", "sunflower", "beans if the season starts wet"]
            slots[0]["why"] = "Summer rain, but the annual total is tight for dryland maize."
            rotation[0] = "Summer sorghum or cowpeas — maize only if you irrigate or the season is clearly wet"

    if ph is not None and ph >= 7.5:
        slots.append({"window": "soil", "role": "caution", "examples": ["watch zinc and iron", "lab sample before fertiliser"], "why": "Predicted pH is alkaline."})
    if tex in ("sandy", "sandy loam"):
        slots.append({"window": "irrigation", "role": "caution", "examples": ["small frequent waterings", "mulch"], "why": "Light soil does not store a big watering."})

    return {
        "kind": "climate_fit",
        "disclaimer": "Not historic yield on this hectare. Pattern from 2015–2024 climate only.",
        "rain_regime": regime,
        "annual_rain_mm": annual,
        "summer_rain_mm": round(summer, 0),
        "winter_rain_mm": round(winter, 0),
        "frost_risk_months": frost,
        "slots": slots,
        "rotation_idea": rotation,
    }
