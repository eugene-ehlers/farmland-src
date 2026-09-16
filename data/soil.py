"""Indicative soil from SoilGrids + notes from climate. Not a lab sample."""
from __future__ import annotations
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from enterprises import year_plan

UA = "Farmland/0.8 (github.com/eugene-ehlers/farmland-src)"
SG = "https://rest.isric.org/soilgrids/v2.0/properties/query"
PROPS = ["clay", "sand", "silt", "phh2o", "soc", "cec", "bdod"]
DEPTHS = ["0-5cm", "5-15cm", "15-30cm"]

def _get(url, timeout=35):
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def _conv(name, raw, factor):
    if raw is None:
        return None
    v = raw / float(factor)
    if name in ("clay", "sand", "silt"):
        return round(v, 1)
    if name == "phh2o":
        return round(v, 2)
    if name == "soc":
        return round(v, 2)
    if name == "cec":
        return round(v, 2)
    if name == "bdod":
        return round(v, 2)
    return round(v, 2)

def texture_class(sand, silt, clay):
    if None in (sand, silt, clay):
        return None
    if clay >= 40:
        return "clay"
    if clay >= 27 and sand <= 45:
        return "clay loam"
    if sand >= 70 and clay < 15:
        return "sandy"
    if sand >= 43 and clay < 20:
        return "sandy loam"
    if silt >= 50:
        return "silty"
    return "loam"

def soilgrids(lat: float, lon: float) -> dict:
    q = urlencode(
        [("lon", f"{lon:.5f}"), ("lat", f"{lat:.5f}")] +
        [("property", p) for p in PROPS] +
        [("depth", d) for d in DEPTHS] +
        [("value", "mean")],
        doseq=True,
    )
    data = _get(f"{SG}?{q}")
    layers = {L["name"]: L for L in (data.get("properties") or {}).get("layers") or []}
    top = {}
    for name in PROPS:
        L = layers.get(name)
        if not L:
            top[name] = None
            continue
        factor = float((L.get("unit_measure") or {}).get("d_factor") or 1)
        weights = {"0-5cm": 5, "5-15cm": 10, "15-30cm": 15}
        num = den = 0.0
        found = False
        for d in L.get("depths") or []:
            raw = (d.get("values") or {}).get("mean")
            if raw is None:
                continue
            w = weights.get(d.get("label"), 10)
            num += _conv(name, raw, factor) * w
            den += w
            found = True
        top[name] = round(num / den, 2) if found and den else None
    tex = texture_class(top.get("sand"), top.get("silt"), top.get("clay"))
    return {
        "source": "SoilGrids 2.0 (ISRIC), 250 m predicted map sampled at cell centre. Not a pit or lab sample.",
        "scale": "250 m",
        "confidence": "indicative",
        "texture_class": tex,
        "sand_pct": top.get("sand"),
        "silt_pct": top.get("silt"),
        "clay_pct": top.get("clay"),
        "ph_water": top.get("phh2o"),
        "soc_g_kg": top.get("soc"),
        "cec_cmol_kg": top.get("cec"),
        "bulk_density": top.get("bdod"),
        "has_values": any(top.get(k) is not None for k in PROPS),
    }

def notes(soil: dict, climate: dict | None) -> list[str]:
    out = []
    ph = soil.get("ph_water")
    tex = soil.get("texture_class")
    rain = (climate or {}).get("annual_rain_mm")
    monthly = (climate or {}).get("monthly") or []
    if ph is not None and ph < 5.5:
        out.append("pH looks acid on the predicted map. Test before liming.")
    if tex in ("sandy", "sandy loam"):
        out.append("Light texture: smaller, more frequent irrigation if you irrigate.")
    if tex in ("clay", "clay loam"):
        out.append("Heavier texture: can waterlog. Avoid working the soil wet.")
    if rain is not None and rain < 450:
        out.append("Historic rain is low for dryland maize.")
    elif rain is not None and rain < 650:
        out.append("Historic rain is modest. Keep a water plan.")
    out.append("Lime and fertiliser rates wait for a lab sample stored on these cell ids.")
    return out

def pack(soil: dict, climate: dict | None) -> dict:
    return {"soil": soil, "notes": notes(soil, climate), "enterprises": year_plan(climate, soil)}
