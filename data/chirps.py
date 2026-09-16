"""CHIRPS v2 rain via SERVIR ClimateSERV. ~5 km."""
from __future__ import annotations
import json, time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

UA = "Farmland/0.7 (github.com/eugene-ehlers/farmland-src)"
BASE = "https://climateserv.servirglobal.net/api"

def _get(url, timeout=45):
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode()

def _num(val):
    if isinstance(val, dict):
        for k in ("avg", "sum", "value", "raw_value"):
            if val.get(k) is not None:
                try:
                    return float(val[k])
                except (TypeError, ValueError):
                    pass
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

def monthly_chirps(lat: float, lon: float, start="01/01/2015", end="12/31/2024"):
    d = 0.04
    geom = {"type": "Polygon", "coordinates": [[[lon-d, lat+d], [lon+d, lat+d], [lon+d, lat-d], [lon-d, lat-d], [lon-d, lat+d]]]}
    q = urlencode({
        "datatype": "0",
        "begintime": start,
        "endtime": end,
        "intervaltype": "0",
        "operationtype": "5",
        "callback": "successCallback",
        "dateType_Category": "default",
        "isZip_CurrentDataType": "false",
        "geometry": json.dumps(geom),
    })
    raw = _get(f"{BASE}/submitDataRequest/?{q}")
    uid = json.loads(raw.replace("successCallback(", "").rstrip(")"))[0]
    for _ in range(30):
        prog = _get(f"{BASE}/getDataRequestProgress/?id={uid}")
        try:
            if float(json.loads(prog)[0]) >= 100:
                break
        except Exception:
            pass
        time.sleep(1.2)
    body = json.loads(_get(f"{BASE}/getDataFromRequest/?id={uid}", timeout=60))
    rows = body.get("data") or []
    totals = [0.0] * 12
    counts = [0] * 12
    for row in rows:
        mm = _num(row.get("value"))
        if mm is None:
            mm = _num(row.get("raw_value"))
        if mm is None:
            continue
        month = row.get("month")
        if not month:
            date = str(row.get("date") or row.get("isodate") or "")
            if "/" in date:
                month = int(date.split("/")[0])
            elif "-" in date and len(date) >= 7:
                month = int(date[5:7])
        try:
            month = int(month)
        except (TypeError, ValueError):
            continue
        if 1 <= month <= 12:
            totals[month - 1] += mm
            counts[month - 1] += 1
    years = max((sum(counts) / 365.25) if sum(counts) else 0, 1)
    out = []
    annual = 0.0
    ok = False
    for i in range(12):
        if counts[i]:
            # totals are summed daily rain across years; divide by number of years in that month
            n_years = counts[i] / 30.4
            v = round(totals[i] / max(n_years, 1), 1)
            out.append(v)
            annual += v
            ok = True
        else:
            out.append(None)
    if not ok:
        return None
    return {"monthly_mm": out, "annual_mm": round(annual, 0), "days": sum(counts)}
