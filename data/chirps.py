"""CHIRPS v2 monthly rain via SERVIR ClimateSERV. ~5 km, Africa-oriented."""
from __future__ import annotations
import json, time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

UA = "Farmland/0.7 (github.com/eugene-ehlers/farmland-src)"
BASE = "https://climateserv.servirglobal.net/api"

def _get(url, timeout=30):
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode()

def monthly_chirps(lat: float, lon: float, start="01/01/2015", end="12/31/2024"):
    d = 0.03
    geom = {
        "type": "Polygon",
        "coordinates": [[[lon-d, lat+d], [lon+d, lat+d], [lon+d, lat-d], [lon-d, lat-d], [lon-d, lat+d]]],
    }
    q = urlencode({
        "datatype": "0",
        "begintime": start,
        "endtime": end,
        "intervaltype": "1",
        "operationtype": "4",
        "callback": "successCallback",
        "dateType_Category": "default",
        "isZip_CurrentDataType": "false",
        "geometry": json.dumps(geom),
    })
    raw = _get(f"{BASE}/submitDataRequest/?{q}")
    uid = raw.replace("successCallback(", "").rstrip(")")
    uid = json.loads(uid)[0]
    for _ in range(20):
        prog = _get(f"{BASE}/getDataRequestProgress/?id={uid}")
        try:
            val = float(json.loads(prog)[0])
        except Exception:
            val = 0.0
        if val >= 100:
            break
        time.sleep(1.5)
    body = json.loads(_get(f"{BASE}/getDataFromRequest/?id={uid}", timeout=45))
    rows = body.get("data") or []
    months = [None] * 12
    counts = [0] * 12
    totals = [0.0] * 12
    for row in rows:
        raw_date = str(row.get("date") or row.get("Date") or "")
        val = row.get("value", row.get("raw_value"))
        if isinstance(val, dict):
            val = val.get("avg") or val.get("sum") or val.get("value")
        try:
            mm = float(val)
        except (TypeError, ValueError):
            continue
        month = None
        if "/" in raw_date:
            parts = raw_date.replace("-", "/").split("/")
            if len(parts) == 2:
                month = int(parts[0])
            elif len(parts) == 3:
                month = int(parts[0]) if int(parts[0]) <= 12 else int(parts[1])
        elif "-" in raw_date and len(raw_date) >= 7:
            month = int(raw_date[5:7])
        if not month or not (1 <= month <= 12):
            continue
        totals[month-1] += mm
        counts[month-1] += 1
    out = []
    annual = 0.0
    ok = False
    for i in range(12):
        if counts[i]:
            v = round(totals[i] / counts[i], 1)
            out.append(v)
            annual += v
            ok = True
        else:
            out.append(None)
    if not ok:
        return None
    return {"monthly_mm": out, "annual_mm": round(annual, 0)}
