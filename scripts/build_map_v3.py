"""
v3 map: dark UI + glassmorphism inspired by chitintim.github.io.
Welcome modal, mobile-friendly bottom-sheet, clickable links + Google Maps action,
score slider, tier filters. Same data + scoring as v2.
"""

import json
import hashlib
from collections import Counter
from pathlib import Path
from build_db_v2 import CAT_A, CAT_B, CAT_C, CAT_D

OUT = "/sessions/keen-focused-ritchie/mnt/outputs/HK_Vegetarian_Restaurants_Map.html"
GEOCODE_PATHS = [
    Path("/sessions/keen-focused-ritchie/mnt/outputs/Veggie/data/geocoded.json"),
    Path(__file__).resolve().parent / "data" / "geocoded.json",
    Path(__file__).resolve().parent.parent / "data" / "geocoded.json",
]
def load_geocoded():
    for p in GEOCODE_PATHS:
        if p.exists():
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    return {}
GEOCODED = load_geocoded()

DISTRICTS = {
    "central": (22.2820, 114.1577), "sheung wan": (22.2870, 114.1502),
    "wan chai": (22.2780, 114.1733), "causeway bay": (22.2802, 114.1860),
    "north point": (22.2916, 114.1996), "quarry bay": (22.2880, 114.2150),
    "taikoo": (22.2880, 114.2150), "admiralty": (22.2796, 114.1648),
    "sai ying pun": (22.2858, 114.1424), "kennedy town": (22.2810, 114.1284),
    "mid-levels": (22.2780, 114.1505), "soho": (22.2820, 114.1535),
    "the peak": (22.2706, 114.1494), "repulse bay": (22.2376, 114.1948),
    "stanley": (22.2196, 114.2096),
    "tsim sha tsui": (22.2980, 114.1722), "tst": (22.2980, 114.1722),
    "tst east": (22.2974, 114.1815), "harbour city": (22.2965, 114.1685),
    "mong kok": (22.3193, 114.1694), "yau ma tei": (22.3115, 114.1707),
    "jordan": (22.3046, 114.1715),
    "sham shui po": (22.3303, 114.1622), "kowloon city": (22.3287, 114.1885),
    "san po kong": (22.3388, 114.1996), "kowloon bay": (22.3231, 114.2135),
    "diamond hill": (22.3408, 114.2017), "kwun tong": (22.3128, 114.2256),
    "whampoa": (22.3056, 114.1908), "hung hom": (22.3055, 114.1830),
    "tai po": (22.4515, 114.1645),
    "tsuen wan": (22.3711, 114.1144), "tseung kwan o": (22.3079, 114.2603),
    "tko": (22.3079, 114.2603), "tuen mun": (22.3915, 113.9750),
    "lantau": (22.2545, 113.9056),
    "ifc": (22.2849, 114.1583), "times square": (22.2790, 114.1833),
}


def coords_for(name_en, district, name_seed):
    """Look up geocoded coords first; fall back to district-centroid + jitter."""
    key = f"{name_en}||{district}"
    geo = GEOCODED.get(key)
    if geo and geo.get("lat") is not None:
        return geo["lat"], geo["lng"]
    # Fallback — district centroid + small deterministic jitter
    s = (district or "Central").lower()
    coords = None
    for k, val in DISTRICTS.items():
        if k in s:
            coords = val
            break
    if coords is None:
        coords = DISTRICTS["central"]
    h = hashlib.md5(name_seed.encode("utf-8")).digest()
    dx = (h[0] - 128) / 128 * 0.0040
    dy = (h[1] - 128) / 128 * 0.0040
    return coords[0] + dy, coords[1] + dx


CATS = [
    ("A. Chinese / Buddhist 齋", CAT_A, "#d4a72c"),
    ("B. Modern Plant-Based / Fine", CAT_B, "#4ecdc4"),
    ("C. Mainstream w/ Strong Veg", CAT_C, "#ff6b6b"),
    ("D. Indian / ME / Med", CAT_D, "#a855f7"),
]

records = []
for cat_label, rows, colour in CATS:
    for r in rows:
        name = r.get("Name (EN)", "")
        seed = name + cat_label
        lat, lng = coords_for(name, r.get("District", ""), seed)
        records.append({
            "name_en": name,
            "name_zh": r.get("Name (中文)", ""),
            "category": cat_label,
            "color": colour,
            "score": r.get("__score__", 0),
            "tier": r.get("__tier__", "—"),
            "subtype": r.get("Sub-type", ""),
            "district": r.get("District", ""),
            "address": r.get("Address", ""),
            "phone": r.get("Phone", ""),
            "website": r.get("Website / IG", ""),
            "booking": r.get("Booking", ""),
            "hours": r.get("Hours", ""),
            "price": r.get("Price (HKD/pp)", ""),
            "veg_type": r.get("Veg type", ""),
            "jain": r.get("Jain", ""),
            "dishes": r.get("Signature / sample dishes (with prices where known)", ""),
            "google": r.get("Google rating", ""),
            "openrice": r.get("OpenRice rating", ""),
            "happycow": r.get("HappyCow rating", ""),
            "michelin": r.get("Michelin / Tatler / Time Out", ""),
            "review_flag": r.get("Review-quality flag", ""),
            "status": r.get("Operational status", ""),
            "notes": r.get("Notes", ""),
            "sources": r.get("Sources (URLs)", ""),
            "lat": lat, "lng": lng,
        })

records_json = json.dumps(records, ensure_ascii=False)
tier_counts = Counter(r["tier"] for r in records)
s_count = tier_counts.get("S", 0)
a_count = tier_counts.get("A", 0)

HTML = r"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5">
<meta name="theme-color" content="#05050a">
<meta name="description" content="A curated, transparently-scored database of __COUNT__ vegetarian-friendly restaurants in Hong Kong.">
<title>HK Veg — Hong Kong Vegetarian Restaurants</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<style>
  /* ─── Palette ─── */
  :root {
    --bg: #f7f7f3;
    --bg-lighter: #ffffff;
    --bg-elevated: #ffffff;
    --card: rgba(15, 18, 30, 0.04);
    --card-hover: rgba(15, 18, 30, 0.08);
    --card-border: rgba(15, 18, 30, 0.10);
    --card-border-strong: rgba(15, 18, 30, 0.18);
    --text: #14141f;
    --text-dim: #5a5a68;
    --text-mute: #8a8a98;
    --shadow-md: 0 4px 14px rgba(20, 20, 31, 0.10);
    --shadow-lg: 0 18px 50px rgba(20, 20, 31, 0.18);

    --catA: #d4a72c;   /* Chinese 齋 — golden */
    --catB: #2a9d8f;   /* Modern plant-based — teal (slightly darker for light bg) */
    --catC: #e35d4b;   /* Mainstream — coral */
    --catD: #8b5cf6;   /* Indian/ME/Med — purple */

    --tierS: #2a9d8f;
    --tierA: #6fbf87;
    --tierB: #ffd95a;
    --tierC: #f4974b;
    --tierD: #e35d4b;

    --glow-teal: rgba(42, 157, 143, 0.10);
    --glow-purple: rgba(139, 92, 246, 0.08);

    --accent: #2a9d8f;
    --spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  html, body { margin: 0; padding: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', 'PingFang TC', 'Microsoft JhengHei', 'Heiti TC', 'Noto Sans TC', sans-serif; color: var(--text); background: var(--bg); overscroll-behavior: none; }
  button { font: inherit; color: inherit; }
  ::selection { background: var(--catB); color: var(--bg); }

  /* ─── Layout ───────────────────────────────────── */
  #app { display: grid; grid-template-columns: 380px 1fr; height: 100dvh; }
  #sidebar {
    background: var(--bg-lighter);
    border-right: 1px solid var(--card-border);
    display: flex; flex-direction: column; min-height: 0;
  }
  #map { height: 100%; min-height: 0; }

  /* ─── Sidebar header ─────────────────────────────── */
  #sidebar header { padding: 16px 18px 12px; border-bottom: 1px solid var(--card-border); display: flex; align-items: center; justify-content: space-between; gap: 10px; }
  #sidebar header h1 {
    margin: 0; font-size: 18px; font-weight: 800; letter-spacing: -0.02em; line-height: 1.15;
    background: linear-gradient(135deg, var(--catB) 0%, var(--catA) 50%, var(--catC) 100%);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
  }
  #sidebar header h1 .leaf { -webkit-text-fill-color: initial; color: #6fe1d8; margin-right: 2px; }
  #sidebar header h1 .count { -webkit-text-fill-color: initial; color: var(--text-mute); font-size: 12px; font-weight: 500; margin-left: 6px; letter-spacing: 0; }
  .header-buttons { display: flex; gap: 6px; flex-shrink: 0; }
  .icon-btn { width: 34px; height: 34px; border-radius: 10px; border: 1px solid var(--card-border); background: var(--card); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; color: var(--text-dim); transition: all 0.25s var(--spring); }
  .icon-btn:hover { background: var(--card-hover); color: var(--catB); border-color: var(--catB); transform: translateY(-1px); }
  .icon-btn:active { transform: scale(0.95); }

  /* ─── Controls ───────────────────────────────────── */
  .controls { padding: 12px 18px; border-bottom: 1px solid var(--card-border); display: flex; flex-direction: column; gap: 10px; }
  .controls input[type=search] { padding: 9px 12px; border: 1px solid var(--card-border-strong); border-radius: 10px; font-size: 14px; width: 100%; background: var(--card); color: var(--text); }
  .controls input[type=search]::placeholder { color: var(--text-mute); }
  .controls input[type=search]:focus { outline: 2px solid var(--accent); outline-offset: -1px; border-color: var(--accent); background: var(--card-hover); }

  .group-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-mute); margin: 4px 0 -2px; font-weight: 600; }
  .filter-row { display: flex; flex-wrap: wrap; gap: 5px; align-items: center; }

  .chip { display: inline-flex; align-items: center; gap: 6px; padding: 5px 11px; border-radius: 14px; font-size: 12px; cursor: pointer; user-select: none; border: 1px solid var(--card-border); background: var(--card); color: var(--text-dim); transition: all 0.25s var(--spring); min-height: 28px; }
  .chip:hover { background: var(--card-hover); color: var(--text); }
  .chip.active { background: var(--text); color: var(--bg); border-color: var(--text); }
  .chip .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
  .chip.A .dot { background: var(--catA); } .chip.B .dot { background: var(--catB); }
  .chip.C .dot { background: var(--catC); } .chip.D .dot { background: var(--catD); }

  .tier-chip { display: inline-flex; align-items: center; padding: 5px 12px; border-radius: 12px; font-size: 12px; font-weight: 700; font-family: 'SF Mono', ui-monospace, Menlo, monospace; cursor: pointer; user-select: none; border: 1px solid transparent; transition: all 0.25s var(--spring); min-width: 30px; min-height: 28px; justify-content: center; }
  .tier-chip.S { background: var(--tierS); color: #062520; }
  .tier-chip.A { background: var(--tierA); color: #062520; }
  .tier-chip.B { background: var(--tierB); color: #2a2306; }
  .tier-chip.C { background: var(--tierC); color: #2a1606; }
  .tier-chip.D { background: var(--tierD); color: #2a0606; }
  .tier-chip:not(.active) { opacity: 0.28; }
  .tier-chip.active:hover { transform: translateY(-1px); }

  .slider-row { display: flex; align-items: center; gap: 12px; font-size: 12px; }
  input[type=range] { flex: 1; height: 24px; accent-color: var(--catB); }
  #score-val { font-family: 'SF Mono', ui-monospace, Menlo, monospace; font-weight: 700; width: 30px; text-align: right; color: var(--catB); }

  select { padding: 6px 10px; border: 1px solid var(--card-border-strong); border-radius: 10px; font-size: 12.5px; background: var(--card); color: var(--text); min-height: 32px; }
  select:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
  label.toggle { display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; cursor: pointer; user-select: none; padding: 4px 0; color: var(--text-dim); }
  label.toggle input { width: 15px; height: 15px; accent-color: var(--catB); }
  label.toggle:hover { color: var(--text); }

  /* ─── Stats / list ───────────────────────────────── */
  .stats { padding: 8px 18px; font-size: 11.5px; color: var(--text-mute); border-bottom: 1px solid var(--card-border); display: flex; justify-content: space-between; align-items: center; }
  .stats button.reset { font-size: 11px; padding: 3px 10px; border: 1px solid var(--card-border); background: var(--card); border-radius: 6px; cursor: pointer; color: var(--text-dim); transition: all 0.2s; }
  .stats button.reset:hover { background: var(--card-hover); color: var(--text); border-color: var(--card-border-strong); }

  #list { overflow-y: auto; flex: 1; min-height: 0; -webkit-overflow-scrolling: touch; }
  #list:empty::before { content: "Nothing matches. Try resetting."; display: block; padding: 32px 18px; text-align: center; color: var(--text-mute); font-size: 13px; }
  .item { padding: 11px 18px 11px 16px; border-bottom: 1px solid var(--card-border); cursor: pointer; transition: all 0.2s var(--spring); display: grid; grid-template-columns: 38px 1fr; gap: 12px; align-items: start; }
  .item:hover { background: var(--card-hover); }
  .item:active { background: rgba(78, 205, 196, 0.08); }
  .item.selected { background: rgba(78, 205, 196, 0.1); border-left: 3px solid var(--catB); padding-left: 13px; }
  .item .score-badge { width: 36px; height: 36px; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-family: 'SF Mono', ui-monospace, Menlo, monospace; font-size: 13px; font-weight: 800; flex-shrink: 0; margin-top: 1px; }
  .item .score-badge.S { background: var(--tierS); color: #062520; } .item .score-badge.A { background: var(--tierA); color: #062520; }
  .item .score-badge.B { background: var(--tierB); color: #2a2306; } .item .score-badge.C { background: var(--tierC); color: #2a1606; }
  .item .score-badge.D { background: var(--tierD); color: #2a0606; } .item .score-badge.dash { background: var(--card); color: var(--text-mute); font-size: 16px; }
  .item .row1 { display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap; }
  .item .name { font-weight: 600; font-size: 14px; line-height: 1.3; color: var(--text); }
  .item .zh { color: var(--text-mute); font-size: 12.5px; }
  .item .meta { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 5px; font-size: 11.5px; color: var(--text-mute); }
  .item .pill { background: var(--card); padding: 2px 8px; border-radius: 9px; }
  .item .pill.michelin { background: rgba(212, 167, 44, 0.16); color: #6b4f0a; }
  .item .pill.closed { background: rgba(227, 93, 75, 0.14); color: #a23a28; }
  .item .cat-pill { color: #062520; padding: 2px 8px; border-radius: 9px; font-size: 11px; font-weight: 600; }

  /* ─── Popup (light because Leaflet popups need light bg by default — keep readable) ─── */
  .leaflet-popup-content-wrapper { background: var(--bg-lighter); color: var(--text); border-radius: 12px; box-shadow: var(--shadow-lg); border: 1px solid var(--card-border-strong); }
  .leaflet-popup-tip { background: var(--bg-lighter); }
  .leaflet-popup-content { margin: 14px 16px; line-height: 1.5; max-width: 360px; color: var(--text); }
  .leaflet-popup-close-button { color: var(--text-mute) !important; font-size: 20px !important; padding: 6px 8px 0 0 !important; }
  .leaflet-popup-close-button:hover { color: var(--text) !important; }
  .popup .head { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 6px; }
  .popup .score-badge { width: 48px; height: 48px; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'SF Mono', ui-monospace, Menlo, monospace; font-weight: 800; flex-shrink: 0; }
  .popup .score-badge .score { font-size: 17px; line-height: 1; }
  .popup .score-badge .tier { font-size: 9.5px; opacity: 0.85; margin-top: 2px; font-weight: 600; }
  .popup .score-badge.S { background: var(--tierS); color: #062520; } .popup .score-badge.A { background: var(--tierA); color: #062520; }
  .popup .score-badge.B { background: var(--tierB); color: #2a2306; } .popup .score-badge.C { background: var(--tierC); color: #2a1606; }
  .popup .score-badge.D { background: var(--tierD); color: #2a0606; } .popup .score-badge.dash { background: var(--card); color: var(--text-mute); }
  .popup h3 { margin: 0 0 2px; font-size: 15px; color: var(--text); }
  .popup .zh { color: var(--text-mute); font-size: 12px; }
  .popup .cat-tag { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; color: #0d1f1d; margin-top: 4px; font-weight: 600; }
  .popup dl { display: grid; grid-template-columns: 80px 1fr; gap: 4px 10px; margin: 8px 0 0; font-size: 12.5px; }
  .popup dt { color: var(--text-mute); }
  .popup dd { margin: 0; word-break: break-word; color: var(--text); }
  .popup .dishes { margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--card-border); font-size: 12.5px; color: var(--text); }
  .popup .dishes .label { color: var(--text-mute); font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 3px; }
  .popup .ratings { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
  .popup .rating { background: var(--card); padding: 2px 8px; border-radius: 8px; font-size: 11px; color: var(--text); }
  .popup .rating.michelin { background: rgba(212, 167, 44, 0.22); color: #6b4f0a; }
  .popup .flag { margin-top: 8px; padding: 6px 10px; background: rgba(255, 230, 109, 0.14); border-left: 3px solid var(--catA); font-size: 11.5px; border-radius: 4px; color: var(--text); }
  .popup .flag.warn { background: rgba(255, 122, 122, 0.14); border-color: var(--tierD); }
  .popup a { color: var(--accent); text-decoration: none; }
  .popup a:hover { text-decoration: underline; }
  .popup .actions { margin-top: 12px; display: flex; gap: 6px; flex-wrap: wrap; }
  .popup .action-btn { display: inline-flex; align-items: center; gap: 6px; padding: 7px 12px; border-radius: 8px; font-size: 12.5px; font-weight: 600; text-decoration: none; border: 1px solid var(--card-border-strong); background: var(--card); color: var(--text); transition: all 0.25s var(--spring); cursor: pointer; }
  .popup .action-btn:hover { background: var(--card-hover); transform: translateY(-1px); text-decoration: none; }
  .popup .action-btn.primary { background: linear-gradient(135deg, var(--catB), var(--catD)); color: white; border-color: transparent; }
  .popup .action-btn.primary:hover { box-shadow: 0 4px 14px rgba(78, 205, 196, 0.25); }
  .popup .action-btn .icon { font-size: 13px; line-height: 1; }
  .popup .notes-block { margin-top: 8px; font-size: 11.5px; color: var(--text-dim); line-height: 1.5; }

  /* ─── Map controls / legend ──────────────────────── */
  .legend { font-size: 11px; line-height: 1.55; background: var(--bg-elevated); color: var(--text); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); border: 1px solid var(--card-border-strong) !important; }
  .legend .row { display: flex; align-items: center; gap: 6px; }
  .legend .swatch { width: 10px; height: 10px; border-radius: 50%; border: 1.5px solid var(--bg-elevated); box-shadow: 0 0 0 1px var(--card-border-strong); }
  .legend strong { color: var(--text); }
  .legend small { color: var(--text-mute); }
  .leaflet-control-attribution { font-size: 10px; background: var(--bg-elevated) !important; color: var(--text-mute) !important; }
  .leaflet-control-attribution a { color: var(--text-dim) !important; }
  .leaflet-control-zoom a { background: var(--bg-elevated) !important; color: var(--text) !important; border-color: var(--card-border-strong) !important; }
  .leaflet-control-zoom a:hover { background: var(--card-hover) !important; }

  /* ─── Welcome modal ──────────────────────────────── */
  .modal-bg {
    position: fixed; inset: 0;
    background: rgba(5, 5, 10, 0.78);
    display: none; z-index: 9999; align-items: center; justify-content: center; padding: 20px;
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  }
  .modal-bg.open { display: flex; animation: fade-in 0.2s ease-out; }
  @keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
  .modal {
    background: var(--bg-elevated);
    border: 1px solid var(--card-border-strong);
    border-radius: 20px;
    max-width: 480px; width: 100%; max-height: 92vh; overflow-y: auto;
    box-shadow: var(--shadow-lg);
    animation: slide-up 0.3s var(--spring);
    position: relative;
  }
  .modal::before {
    content: ""; position: absolute; inset: 0; border-radius: 20px;
    background: linear-gradient(135deg, var(--glow-teal), transparent 60%);
    opacity: 0.5; pointer-events: none; z-index: 0;
  }
  @keyframes slide-up { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
  .modal-header { padding: 28px 30px 6px; position: relative; z-index: 1; }
  .modal-header h2 { margin: 0 0 12px; font-size: 28px; font-weight: 800; letter-spacing: -0.025em; background: linear-gradient(135deg, var(--catB), var(--catA)); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
  .modal-header h2 .leaf { -webkit-text-fill-color: initial; }
  .modal-header .sub { color: var(--text); font-size: 15px; line-height: 1.4; margin: 0 0 8px; font-weight: 500; }
  .modal-header .sub-2 { color: var(--text-dim); font-size: 13.5px; line-height: 1.55; margin: 0; }
  .modal-header .sub-2 strong { color: var(--text); }
  .modal-body { padding: 4px 30px 8px; font-size: 13.5px; line-height: 1.6; color: var(--text); position: relative; z-index: 1; }
  .modal-body p { margin: 0; }
  .how-line { color: var(--text-dim); font-size: 12.5px; line-height: 1.55; margin-top: 14px !important; }
  .how-line strong { color: var(--text); font-family: 'SF Mono', ui-monospace, Menlo, monospace; font-size: 11.5px; padding: 1px 5px; border-radius: 4px; background: var(--card); border: 1px solid var(--card-border); }
  .stat-row { display: flex; gap: 8px; flex-wrap: wrap; margin: 4px 0 0; }
  .stat-pill {
    display: inline-flex; flex-direction: column; align-items: flex-start;
    padding: 11px 14px; border-radius: 12px;
    background: var(--card); border: 1px solid var(--card-border);
    flex: 1; min-width: 78px;
    transition: all 0.3s var(--spring);
  }
  .stat-pill:hover { transform: translateY(-2px); border-color: var(--accent); }
  .stat-pill .num { font-family: 'SF Mono', ui-monospace, Menlo, monospace; font-size: 22px; font-weight: 800; line-height: 1; color: var(--accent); }
  .stat-pill .lbl { font-size: 10px; color: var(--text-mute); margin-top: 5px; text-transform: uppercase; letter-spacing: 0.06em; }
  .modal-footer { padding: 16px 30px 26px; display: flex; gap: 12px; justify-content: space-between; align-items: center; flex-wrap: wrap; position: relative; z-index: 1; }
  .modal-footer .secondary { color: var(--text-mute); font-size: 11.5px; line-height: 1.4; flex: 1; min-width: 180px; }
  .info-inline { display: inline-flex; width: 18px; height: 18px; border-radius: 50%; border: 1px solid var(--card-border-strong); align-items: center; justify-content: center; font-size: 10px; color: var(--accent); vertical-align: middle; line-height: 1; }
  .btn-primary {
    background: linear-gradient(135deg, var(--catB), var(--catD));
    color: white; border: none;
    padding: 11px 26px; border-radius: 10px; cursor: pointer;
    font-size: 14px; font-weight: 700;
    transition: all 0.25s var(--spring);
    box-shadow: 0 4px 14px rgba(78, 205, 196, 0.18);
  }
  .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(78, 205, 196, 0.3); }
  .btn-primary:active { transform: scale(0.97); }

  /* ─── Mobile FAB ──────────────────────────────── */
  #mobile-fab { display: none; }

  /* ─── Mobile layout ──────────────────────────────── */
  @media (max-width: 800px) {
    #app { grid-template-columns: 1fr; grid-template-rows: 1fr; }
    #sidebar {
      position: fixed; left: 0; right: 0; bottom: 0;
      height: 60vh; max-height: 88dvh;
      transform: translateY(calc(100% - 64px));
      transition: transform 0.32s var(--spring);
      z-index: 1000; border-right: none;
      border-top: 1px solid var(--card-border-strong);
      border-top-left-radius: 20px; border-top-right-radius: 20px;
      box-shadow: var(--shadow-lg);
      overflow: hidden;
    }
    #sidebar.expanded { transform: translateY(0); height: 92dvh; }
    #sidebar header {
      padding: 12px 18px 10px; cursor: pointer; position: relative; flex-shrink: 0;
    }
    #sidebar header::before {
      content: ""; position: absolute; top: 8px; left: 50%;
      transform: translateX(-50%);
      width: 38px; height: 4px; border-radius: 2px;
      background: var(--card-border-strong);
    }
    #sidebar header h1 { font-size: 16px; padding-top: 10px; }
    .header-buttons { display: none; }

    .controls { padding: 10px 16px 8px; gap: 8px; }
    .filter-row { gap: 6px; }
    .chip { padding: 7px 12px; font-size: 12.5px; }
    .tier-chip { padding: 6px 12px; font-size: 12.5px; min-width: 32px; min-height: 32px; }

    .stats { padding: 8px 16px; }
    .item { padding: 12px 16px; }
    .item .name { font-size: 14.5px; }

    #map { height: 100dvh; }

    /* Floating Action Buttons */
    #mobile-fab, #mobile-lang-fab {
      display: flex; position: fixed; right: 14px;
      width: 44px; height: 44px; border-radius: 50%;
      background: var(--bg-elevated); color: var(--accent);
      border: 1px solid var(--card-border-strong);
      box-shadow: var(--shadow-md);
      align-items: center; justify-content: center;
      font-size: 17px; font-weight: 600;
      cursor: pointer; z-index: 999;
    }
    #mobile-fab { top: 14px; }
    #mobile-lang-fab { top: 66px; font-size: 15px; }
    #mobile-fab:active, #mobile-lang-fab:active { transform: scale(0.92); }

    /* Modal as bottom sheet */
    .modal { border-radius: 20px 20px 0 0; max-height: 92dvh; align-self: flex-end; width: 100%; max-width: none; }
    .modal-bg { padding: 0; align-items: flex-end; }
    .modal-header { padding: 22px 22px 12px; }
    .modal-body { padding: 0 22px 12px; }
    .modal-footer { padding: 12px 22px 24px; }

    .leaflet-popup-content { max-width: calc(100vw - 60px); }
  }

  @media (max-width: 380px) {
    #sidebar header h1 { font-size: 14.5px; }
    .modal-header h2 { font-size: 20px; }
  }

  /* Reduced motion */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
  }
</style>
</head>
<body>

<!-- Welcome / About modal -->
<div class="modal-bg" id="modal-bg" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal" tabindex="-1">
    <div class="modal-header">
      <h2 id="modal-title"><span class="leaf">🌱</span> <span data-i18n="title">HK Veg</span></h2>
      <p class="sub" data-i18n="sub1">Vegetarian. In Hong Kong. Books nothing in advance. Pick three.</p>
      <p class="sub-2" data-i18n-html="sub2">So here's a map of <strong>__COUNT__</strong> veggie-friendly spots, ranked by an actual score (instead of OpenRice's paid-review wild west).</p>
    </div>
    <div class="modal-body">
      <div class="stat-row">
        <div class="stat-pill"><span class="num">__COUNT__</span><span class="lbl" data-i18n="placesLabel">places</span></div>
        <div class="stat-pill"><span class="num">__S__</span><span class="lbl" data-i18n="sTierLabel">S-tier</span></div>
        <div class="stat-pill"><span class="num">__A__</span><span class="lbl" data-i18n="aTierLabel">A-tier</span></div>
        <div class="stat-pill"><span class="num">4</span><span class="lbl" data-i18n="cuisinesLabel">cuisines</span></div>
      </div>
      <p class="how-line" data-i18n-html="howLine">Score weights ratings by review volume, bonuses Michelin/Tatler/Time Out picks, penalises suspect bimodal patterns. <strong>S</strong> 85+ → <strong>D</strong> &lt;55. Closed places sink. Tap anything in the list to fly the map there.</p>
    </div>
    <div class="modal-footer">
      <span class="secondary" data-i18n-html="hitInfo">Hit <span class="info-inline">?</span> anytime for this. Maps · Call · Site buttons in every popup.</span>
      <button class="btn-primary" id="modal-close" data-i18n="letsEatBtn">Let's eat</button>
    </div>
  </div>
</div>

<button id="mobile-fab" aria-label="About">?</button>
<button id="mobile-lang-fab" aria-label="Switch language">中</button>

<div id="app">
  <aside id="sidebar">
    <header id="sidebar-header" role="button" aria-label="Toggle results panel">
      <h1><span class="leaf">🌱</span> <span data-i18n="title">HK Veg</span> <span class="count" id="m-count"></span></h1>
      <div class="header-buttons">
        <button class="icon-btn lang-btn" id="lang-btn" data-i18n-title="langBtnTitle" aria-label="Switch language">中</button>
        <button class="icon-btn" id="info-btn" data-i18n-title="aboutBtnTitle" aria-label="About">?</button>
      </div>
    </header>

    <div class="controls">
      <input id="search" type="search" data-i18n-placeholder="searchPlaceholder" placeholder="Search name, dish, district…" autocomplete="off" />

      <div class="group-label" data-i18n="qualityLabel">Quality (min score)</div>
      <div class="slider-row">
        <input id="score-slider" type="range" min="0" max="95" step="5" value="0" aria-label="Minimum quality score" />
        <span id="score-val">0</span>
      </div>

      <div class="group-label" data-i18n="tierLabel">Tier</div>
      <div class="filter-row">
        <span class="tier-chip S active" data-tier="S">S</span>
        <span class="tier-chip A active" data-tier="A">A</span>
        <span class="tier-chip B active" data-tier="B">B</span>
        <span class="tier-chip C active" data-tier="C">C</span>
        <span class="tier-chip D active" data-tier="D">D</span>
      </div>

      <div class="group-label" data-i18n="categoryLabel">Category</div>
      <div class="filter-row" id="cat-filters">
        <span class="chip A active" data-cat="A. Chinese / Buddhist 齋"><span class="dot"></span><span data-i18n="catA">Chinese 齋</span></span>
        <span class="chip B active" data-cat="B. Modern Plant-Based / Fine"><span class="dot"></span><span data-i18n="catB">Plant-based</span></span>
        <span class="chip C active" data-cat="C. Mainstream w/ Strong Veg"><span class="dot"></span><span data-i18n="catC">Mainstream</span></span>
        <span class="chip D active" data-cat="D. Indian / ME / Med"><span class="dot"></span><span data-i18n="catD">Indian/ME/Med</span></span>
      </div>

      <div class="group-label" data-i18n="moreFilters">More filters</div>
      <div class="filter-row" style="gap:10px;">
        <select id="veg-filter">
          <option value="" data-i18n="anyVegType">Any veg type</option>
          <option value="vegan" data-i18n="veganOnly">Vegan only</option>
          <option value="jain" data-i18n="jainOptions">Jain options</option>
        </select>
        <label class="toggle"><input type="checkbox" id="critic-only"> <span data-i18n="criticOnly">Critic-recognised</span></label>
      </div>
      <div class="filter-row" style="gap:10px;">
        <label class="toggle"><input type="checkbox" id="trusted-only"> <span data-i18n="trustedReviews">Trusted reviews</span></label>
        <label class="toggle"><input type="checkbox" id="hide-closed" checked> <span data-i18n="hideClosed">Hide closed</span></label>
      </div>
    </div>

    <div class="stats">
      <span id="stats-text"></span>
      <button class="reset" id="reset-btn" data-i18n="resetBtn">reset</button>
    </div>
    <div id="list"></div>
  </aside>
  <main id="map"></main>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
const DATA = __DATA__;
const CAT_COLORS = {
  "A. Chinese / Buddhist 齋": "#ffe66d",
  "B. Modern Plant-Based / Fine": "#4ecdc4",
  "C. Mainstream w/ Strong Veg": "#ff6b6b",
  "D. Indian / ME / Med": "#a855f7",
};

// ─── i18n / strings ───────────────────────────────────────
const COUNT_TOTAL = __COUNT__;
const STRINGS = {
  en: {
    title: "HK Veg",
    sub1: "Vegetarian. In Hong Kong. Books nothing in advance. Pick three.",
    sub2: (n) => `So here's a map of <strong>${n}</strong> veggie-friendly spots, ranked by an actual score (instead of OpenRice's paid-review wild west).`,
    placesLabel: "places", sTierLabel: "S-tier", aTierLabel: "A-tier", cuisinesLabel: "cuisines",
    howLine: "Score weights ratings by review volume, bonuses Michelin/Tatler/Time Out picks, penalises suspect bimodal patterns. <strong>S</strong> 85+ → <strong>D</strong> &lt;55. Closed places sink. Tap anything in the list to fly the map there.",
    hitInfo: 'Hit <span class="info-inline">?</span> anytime for this. Maps · Call · Site buttons in every popup.',
    letsEatBtn: "Let's eat",
    searchPlaceholder: "Search name, dish, district…",
    qualityLabel: "Quality (min score)", tierLabel: "Tier", categoryLabel: "Category", moreFilters: "More filters",
    anyVegType: "Any veg type", veganOnly: "Vegan only", jainOptions: "Jain options",
    criticOnly: "Critic-recognised", trustedReviews: "Trusted reviews", hideClosed: "Hide closed",
    resetBtn: "reset",
    catA: "Chinese 齋", catB: "Plant-based", catC: "Mainstream", catD: "Indian/ME/Med",
    statsShown: (s, t) => `${s} of ${t} shown`,
    countShown: (n) => `· ${n} shown`,
    nothingMatches: "Nothing matches. Try resetting.",
    popup: { type: "Type", district: "District", address: "Address", phone: "Phone", web: "Web/IG", hours: "Hours", price: "Price", vegType: "Veg type", booking: "Booking", jainPrefix: " · Jain: ", dishesLabel: "Signature / sample dishes", maps: "Google Maps", call: "Call", website: "Website", status: "Status:", reviewQ: "Review quality:", priceFmt: (p) => `HKD ${p}/person`, tier: (t) => t === "—" ? "closed" : "tier " + t, closed: "closed" },
    legendTitle: "Categories",
    legendCats: { catA: "Chinese 齋", catB: "Modern plant-based", catC: "Mainstream w/ veg", catD: "Indian / ME / Med" },
    legendNote: "Marker size = score.",
    aboutBtnTitle: "About", themeBtnTitle: "Toggle light/dark", langBtnTitle: "切換中文",
    langBtnLabel: "中",
  },
  zh: {
    title: "香港素食",
    sub1: "素食者。住香港。從不訂位。三樣全中。",
    sub2: (n) => `所以整咗呢張地圖：<strong>${n}</strong> 間素食友善餐廳，按一套真正可信嘅評分排序（唔好再信 OpenRice 嗰啲付費評論）。`,
    placesLabel: "間", sTierLabel: "S 級", aTierLabel: "A 級", cuisinesLabel: "菜系",
    howLine: "評分綜合：用戶評分（按評論數加權）＋ 米芝蓮／Tatler／Time Out 加分 − 可疑評論扣分。<strong>S</strong> 85+ → <strong>D</strong> &lt;55。結業餐廳沉底。撳列表項可飛去地圖上對應位置。",
    hitInfo: '隨時可撳 <span class="info-inline">?</span> 重新查看。每個彈出框都有 地圖・致電・網站 鍵。',
    letsEatBtn: "開飯",
    searchPlaceholder: "搜尋餐廳、菜式、地區……",
    qualityLabel: "質素（最低分）", tierLabel: "等級", categoryLabel: "分類", moreFilters: "更多篩選",
    anyVegType: "所有素食類型", veganOnly: "純素", jainOptions: "耆那素食",
    criticOnly: "獲評論機構認可", trustedReviews: "可靠評論", hideClosed: "隱藏結業",
    resetBtn: "重設",
    catA: "中式齋菜", catB: "新派純素", catC: "主流餐廳", catD: "印／中東／地中海",
    statsShown: (s, t) => `顯示 ${s} ／ ${t} 間`,
    countShown: (n) => `· ${n} 間`,
    nothingMatches: "冇匹配結果。試吓重設篩選。",
    popup: { type: "類型", district: "地區", address: "地址", phone: "電話", web: "網站／IG", hours: "營業時間", price: "人均", vegType: "素食類型", booking: "預約", jainPrefix: " · 耆那：", dishesLabel: "招牌／示範菜式", maps: "Google 地圖", call: "致電", website: "網站", status: "狀態：", reviewQ: "評論質素：", priceFmt: (p) => `HKD ${p} ／ 位`, tier: (t) => t === "—" ? "已結業" : t + " 級", closed: "已結業" },
    legendTitle: "分類",
    legendCats: { catA: "中式齋菜", catB: "新派純素", catC: "主流（有素食）", catD: "印／中東／地中海" },
    legendNote: "圖標大小＝分數。",
    aboutBtnTitle: "關於", themeBtnTitle: "切換淺／深色", langBtnTitle: "Switch to English",
    langBtnLabel: "EN",
  },
};

function getInitialLang() {
  try {
    const saved = localStorage.getItem("hkv-lang");
    if (saved === "en" || saved === "zh") return saved;
  } catch (_) {}
  return "en";
}
let currentLang = getInitialLang();
const t = () => STRINGS[currentLang];

// ─── Map ──────────────────────────────────────────────────
const isMobile = () => window.matchMedia("(max-width: 800px)").matches;
const map = L.map("map", { zoomControl: true }).setView([22.305, 114.170], isMobile() ? 10 : 11);
L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
  attribution: '&copy; OpenStreetMap, &copy; CARTO', maxZoom: 19, subdomains: "abcd",
}).addTo(map);

let legendDiv = null;
const legend = L.control({ position: "bottomright" });
legend.onAdd = function () {
  const div = L.DomUtil.create("div", "leaflet-control");
  div.style.padding = "9px 11px"; div.style.borderRadius = "10px";
  div.style.boxShadow = "var(--shadow-md)";
  div.classList.add("legend");
  legendDiv = div;
  renderLegend();
  return div;
};
function renderLegend() {
  if (!legendDiv) return;
  const s = t();
  legendDiv.innerHTML = `
    <strong style="font-size:11px;">${s.legendTitle}</strong>
    <div class="row"><span class="swatch" style="background:${CAT_COLORS["A. Chinese / Buddhist 齋"]}"></span>${s.legendCats.catA}</div>
    <div class="row"><span class="swatch" style="background:${CAT_COLORS["B. Modern Plant-Based / Fine"]}"></span>${s.legendCats.catB}</div>
    <div class="row"><span class="swatch" style="background:${CAT_COLORS["C. Mainstream w/ Strong Veg"]}"></span>${s.legendCats.catC}</div>
    <div class="row"><span class="swatch" style="background:${CAT_COLORS["D. Indian / ME / Med"]}"></span>${s.legendCats.catD}</div>
    <small style="display:block;margin-top:4px;max-width:140px;">${s.legendNote}</small>`;
}
legend.addTo(map);

function makeIcon(r) {
  const size = r.score >= 85 ? 24 : r.score >= 75 ? 21 : r.score >= 65 ? 18 : r.score >= 55 ? 16 : 14;
  const opacity = r.score === 0 ? 0.4 : 1;
  return L.divIcon({
    className: "veg-marker",
    html: `<div style="width:${size}px;height:${size}px;border-radius:50%;background:${r.color};border:2.5px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.5);opacity:${opacity};"></div>`,
    iconSize: [size, size], iconAnchor: [size/2, size/2], popupAnchor: [0, -size/2],
  });
}

// ─── Helpers for clickable links ─────────────────────────
function escapeHtml(s) { return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

function websiteHref(s) {
  if (!s || s === "—") return "";
  const t = String(s).trim();
  const igMatch = t.match(/^@([A-Za-z0-9_.]+)/);
  if (igMatch) return `https://www.instagram.com/${igMatch[1]}/`;
  if (/^https?:\/\//i.test(t)) return encodeURI(t);
  if (/^[A-Za-z0-9.-]+\.[A-Za-z]{2,}(\/.*)?$/.test(t)) return `https://${t}`;
  if (/^facebook\.com\/|^instagram\.com\//.test(t)) return `https://${t}`;
  return "";
}
function websiteLink(raw) {
  if (!raw || raw === "—") return "";
  const href = websiteHref(raw);
  const display = String(raw).replace(/^https?:\/\/(www\.)?/i, "").replace(/^@/, "@");
  if (href) return `<a href="${href}" target="_blank" rel="noopener noreferrer">${escapeHtml(display)}</a>`;
  return escapeHtml(raw);
}
function phoneTel(s) {
  const m = String(s || "").match(/(\+\d[\d\s-]{6,}\d)/);
  return m ? m[1].replace(/[\s-]/g, "") : "";
}
function phoneLink(raw) {
  if (!raw || raw === "—") return "";
  const tel = phoneTel(raw);
  if (!tel) return escapeHtml(raw);
  const m = String(raw).match(/(\+\d[\d\s-]{6,}\d)/);
  const visible = m ? m[1] : raw;
  const after = m ? String(raw).replace(m[1], "") : "";
  return `<a href="tel:${tel}">${escapeHtml(visible)}</a>${escapeHtml(after)}`;
}
function gmapsUrl(r) {
  const parts = [r.name_en];
  if (r.address && r.address !== "—") parts.push(r.address);
  else if (r.district) parts.push(r.district);
  parts.push("Hong Kong");
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(parts.filter(Boolean).join(", "))}`;
}

function popupHtml(r) {
  const s = t();
  const p = s.popup;
  const flagClass = (r.review_flag || "").toLowerCase().includes("mixed") || (r.review_flag || "").toLowerCase().includes("verify") ? "flag warn" : "flag";
  const showFlag = r.review_flag && r.review_flag.toLowerCase() !== "trusted";
  const statusWarn = (r.status || "").toUpperCase().includes("CLOSED") || (r.status || "").toUpperCase().includes("UNCERTAIN");
  const closed = (r.status || "").toUpperCase().includes("CLOSED");
  const ratings = [
    r.google && r.google !== "—" && `Google ${r.google}`,
    r.openrice && r.openrice !== "—" && `OpenRice ${r.openrice}`,
    r.happycow && r.happycow !== "—" && `HappyCow ${r.happycow}`,
  ].filter(Boolean);
  const tierClass = r.tier === "—" ? "dash" : r.tier;
  const tel = phoneTel(r.phone);
  const webHref = websiteHref(r.website);
  // For zh mode, prefer Chinese name as primary if it exists
  const primaryName = (currentLang === "zh" && r.name_zh && r.name_zh !== "—") ? r.name_zh : r.name_en;
  const secondaryName = (currentLang === "zh" && r.name_zh && r.name_zh !== "—") ? r.name_en : (r.name_zh && r.name_zh !== "—" ? r.name_zh : "");

  return `<div class="popup">
    <div class="head">
      <div class="score-badge ${tierClass}">
        <span class="score">${r.score === 0 ? "—" : r.score}</span>
        <span class="tier">${p.tier(r.tier)}</span>
      </div>
      <div style="flex:1;min-width:0;">
        <h3>${escapeHtml(primaryName)}</h3>
        ${secondaryName ? `<div class="zh">${escapeHtml(secondaryName)}</div>` : ""}
        <span class="cat-tag" style="background:${r.color}">${escapeHtml(catLabel(r.category))}</span>
      </div>
    </div>
    <dl>
      <dt>${p.type}</dt><dd>${escapeHtml(r.subtype)}</dd>
      <dt>${p.district}</dt><dd>${escapeHtml(r.district)}</dd>
      <dt>${p.address}</dt><dd>${escapeHtml(r.address)}</dd>
      ${r.phone && r.phone !== "—" ? `<dt>${p.phone}</dt><dd>${phoneLink(r.phone)}</dd>` : ""}
      ${r.website && r.website !== "—" ? `<dt>${p.web}</dt><dd>${websiteLink(r.website)}</dd>` : ""}
      ${r.hours ? `<dt>${p.hours}</dt><dd>${escapeHtml(r.hours)}</dd>` : ""}
      <dt>${p.price}</dt><dd>${p.priceFmt(escapeHtml(r.price))}</dd>
      <dt>${p.vegType}</dt><dd>${escapeHtml(r.veg_type)}${r.jain && r.jain !== "No" && r.jain !== "—" ? p.jainPrefix + escapeHtml(r.jain) : ""}</dd>
      <dt>${p.booking}</dt><dd>${escapeHtml(r.booking)}</dd>
    </dl>
    ${r.dishes ? `<div class="dishes"><div class="label">${p.dishesLabel}</div>${escapeHtml(r.dishes)}</div>` : ""}
    ${ratings.length || (r.michelin && r.michelin !== "—") ? `<div class="ratings">
      ${ratings.map(x => `<span class="rating">${escapeHtml(x)}</span>`).join("")}
      ${r.michelin && r.michelin !== "—" ? `<span class="rating michelin">${escapeHtml(r.michelin)}</span>` : ""}
    </div>` : ""}
    <div class="actions">
      ${closed ? "" : `<a class="action-btn primary" href="${gmapsUrl(r)}" target="_blank" rel="noopener noreferrer"><span class="icon">📍</span>${p.maps}</a>`}
      ${tel ? `<a class="action-btn" href="tel:${tel}"><span class="icon">📞</span>${p.call}</a>` : ""}
      ${webHref ? `<a class="action-btn" href="${webHref}" target="_blank" rel="noopener noreferrer"><span class="icon">🔗</span>${p.website}</a>` : ""}
    </div>
    ${statusWarn ? `<div class="flag warn"><strong>${p.status}</strong> ${escapeHtml(r.status)}</div>` : ""}
    ${showFlag && !statusWarn ? `<div class="${flagClass}"><strong>${p.reviewQ}</strong> ${escapeHtml(r.review_flag)}</div>` : ""}
    ${r.notes ? `<div class="notes-block">${escapeHtml(r.notes)}</div>` : ""}
  </div>`;
}

function catLabel(catKey) {
  const s = t();
  if (catKey.startsWith("A.")) return s.catA;
  if (catKey.startsWith("B.")) return s.catB;
  if (catKey.startsWith("C.")) return s.catC;
  if (catKey.startsWith("D.")) return s.catD;
  return catKey;
}

const markers = DATA.map(r => {
  const m = L.marker([r.lat, r.lng], { icon: makeIcon(r) });
  m.bindPopup(popupHtml(r), { maxWidth: 380 });
  m._record = r;
  return m;
});
const layer = L.layerGroup(markers).addTo(map);

// ─── State / filters ───────────────────────────────────────
const state = {
  cats: new Set(["A. Chinese / Buddhist 齋", "B. Modern Plant-Based / Fine", "C. Mainstream w/ Strong Veg", "D. Indian / ME / Med"]),
  tiers: new Set(["S","A","B","C","D"]),
  q: "", veg: "", criticOnly: false, trustedOnly: false, hideClosed: true,
  minScore: 0,
};

function passes(r) {
  if (!state.cats.has(r.category)) return false;
  if (state.hideClosed && (r.score === 0 || (r.status||"").toUpperCase().includes("CLOSED") || (r.status||"").toUpperCase().includes("UNCERTAIN"))) return false;
  if (state.tiers.size < 5 && !state.tiers.has(r.tier)) return false;
  if (r.score < state.minScore) return false;
  if (state.veg === "vegan" && !(r.veg_type||"").toLowerCase().includes("vegan")) return false;
  if (state.veg === "jain") {
    const j = (r.jain||"").toLowerCase();
    if (!(j === "yes" || j.includes("yes") || j.includes("on request"))) return false;
  }
  if (state.criticOnly) {
    const m = (r.michelin||"").toLowerCase();
    if (!m || m === "—") return false;
  }
  if (state.trustedOnly && (r.review_flag||"").toLowerCase() !== "trusted") return false;
  if (state.q) {
    const q = state.q.toLowerCase();
    const hay = [r.name_en, r.name_zh, r.subtype, r.district, r.address, r.dishes, r.notes, r.veg_type, r.michelin].join(" ").toLowerCase();
    if (!hay.includes(q)) return false;
  }
  return true;
}

function applyFilters() {
  markers.forEach((m, i) => {
    const r = DATA[i];
    if (passes(r)) { if (!map.hasLayer(m)) layer.addLayer(m); }
    else { if (map.hasLayer(m)) layer.removeLayer(m); }
  });
  renderList();
}

function shortMichelin(s) {
  if (s.includes("★★★")) return "★★★";
  if (s.includes("★★")) return "★★";
  if (s.includes("★")) return "★";
  if (s.toLowerCase().includes("bib")) return "Bib";
  if (s.toLowerCase().includes("tatler")) return "Tatler";
  return s.slice(0, 18);
}

function renderList() {
  const s = t();
  const list = document.getElementById("list");
  const stats = document.getElementById("stats-text");
  const mCount = document.getElementById("m-count");
  const filtered = DATA.map((r, i) => ({ r, i })).filter(x => passes(x.r));
  filtered.sort((a, b) => {
    if (a.r.score !== b.r.score) return b.r.score - a.r.score;
    return a.r.name_en.localeCompare(b.r.name_en);
  });
  stats.textContent = s.statsShown(filtered.length, DATA.length);
  if (mCount) mCount.textContent = s.countShown(filtered.length);
  if (filtered.length === 0) {
    list.innerHTML = `<div style="padding:32px 18px;text-align:center;color:var(--text-mute);font-size:13px;">${s.nothingMatches}</div>`;
    return;
  }
  list.innerHTML = filtered.map(({ r, i }) => {
    const tierClass = r.tier === "—" ? "dash" : r.tier;
    const catShort = r.category.split(".")[0];
    const closed = (r.status||"").toUpperCase().includes("CLOSED");
    const primary = (currentLang === "zh" && r.name_zh && r.name_zh !== "—") ? r.name_zh : r.name_en;
    const secondary = (currentLang === "zh" && r.name_zh && r.name_zh !== "—") ? r.name_en : (r.name_zh && r.name_zh !== "—" ? r.name_zh : "");
    return `<div class="item" data-i="${i}" ${closed ? 'style="opacity:0.55"' : ""}>
      <div class="score-badge ${tierClass}">${r.score === 0 ? "—" : Math.round(r.score)}</div>
      <div>
        <div class="row1">
          <span class="name">${escapeHtml(primary)}</span>
          ${secondary ? `<span class="zh">${escapeHtml(secondary)}</span>` : ""}
        </div>
        <div class="meta">
          <span class="cat-pill" style="background:${r.color}">${catShort}</span>
          <span class="pill">${escapeHtml(r.district)}</span>
          ${r.michelin && r.michelin !== "—" ? `<span class="pill michelin">${escapeHtml(shortMichelin(r.michelin))}</span>` : ""}
          ${closed ? `<span class="pill closed">${s.popup.closed}</span>` : ""}
        </div>
      </div>
    </div>`;
  }).join("");
}

// ─── UI bindings ───────────────────────────────────────────
document.querySelectorAll("#cat-filters .chip").forEach(chip => {
  chip.addEventListener("click", () => {
    const c = chip.dataset.cat;
    if (state.cats.has(c)) { state.cats.delete(c); chip.classList.remove("active"); }
    else { state.cats.add(c); chip.classList.add("active"); }
    applyFilters();
  });
});
document.querySelectorAll(".tier-chip").forEach(chip => {
  chip.addEventListener("click", () => {
    const t = chip.dataset.tier;
    if (state.tiers.has(t)) { state.tiers.delete(t); chip.classList.remove("active"); }
    else { state.tiers.add(t); chip.classList.add("active"); }
    applyFilters();
  });
});
const searchEl = document.getElementById("search");
searchEl.addEventListener("input", e => { state.q = e.target.value.trim(); applyFilters(); });
document.getElementById("veg-filter").addEventListener("change", e => { state.veg = e.target.value; applyFilters(); });
document.getElementById("critic-only").addEventListener("change", e => { state.criticOnly = e.target.checked; applyFilters(); });
document.getElementById("trusted-only").addEventListener("change", e => { state.trustedOnly = e.target.checked; applyFilters(); });
document.getElementById("hide-closed").addEventListener("change", e => { state.hideClosed = e.target.checked; applyFilters(); });
document.getElementById("score-slider").addEventListener("input", e => {
  state.minScore = +e.target.value;
  document.getElementById("score-val").textContent = e.target.value;
  applyFilters();
});
document.getElementById("reset-btn").addEventListener("click", () => {
  state.cats = new Set(["A. Chinese / Buddhist 齋", "B. Modern Plant-Based / Fine", "C. Mainstream w/ Strong Veg", "D. Indian / ME / Med"]);
  state.tiers = new Set(["S","A","B","C","D"]);
  state.q = ""; state.veg = ""; state.criticOnly = false; state.trustedOnly = false; state.hideClosed = true; state.minScore = 0;
  document.querySelectorAll("#cat-filters .chip").forEach(c => c.classList.add("active"));
  document.querySelectorAll(".tier-chip").forEach(c => c.classList.add("active"));
  searchEl.value = "";
  document.getElementById("veg-filter").value = "";
  document.getElementById("critic-only").checked = false;
  document.getElementById("trusted-only").checked = false;
  document.getElementById("hide-closed").checked = true;
  document.getElementById("score-slider").value = 0;
  document.getElementById("score-val").textContent = "0";
  applyFilters();
});

document.getElementById("list").addEventListener("click", e => {
  const item = e.target.closest(".item");
  if (!item) return;
  const i = +item.dataset.i;
  const m = markers[i];
  document.querySelectorAll(".item.selected").forEach(x => x.classList.remove("selected"));
  item.classList.add("selected");
  if (!map.hasLayer(m)) layer.addLayer(m);
  if (isMobile()) collapseSheet();
  map.setView(m.getLatLng(), 15);
  m.openPopup();
});

// ─── Welcome / About modal ─────────────────────────────────
const modalBg = document.getElementById("modal-bg");
function openModal() { modalBg.classList.add("open"); document.body.style.overflow = "hidden"; }
function closeModal() { modalBg.classList.remove("open"); document.body.style.overflow = ""; try { localStorage.setItem("hkv-seen-welcome-v4", "1"); } catch (_) {} }
document.getElementById("modal-close").addEventListener("click", closeModal);
modalBg.addEventListener("click", e => { if (e.target === modalBg) closeModal(); });
document.addEventListener("keydown", e => { if (e.key === "Escape" && modalBg.classList.contains("open")) closeModal(); });
document.getElementById("info-btn").addEventListener("click", openModal);
document.getElementById("mobile-fab").addEventListener("click", openModal);

// ─── Language toggle bindings ─────────────────────────────
function toggleLang() {
  setLang(currentLang === "en" ? "zh" : "en");
}
function setLang(lang) {
  currentLang = lang;
  try { localStorage.setItem("hkv-lang", lang); } catch (_) {}
  applyLanguage();
}
function applyLanguage() {
  const s = t();
  // text content
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    let val = s[key];
    if (typeof val === "function") val = val(COUNT_TOTAL);
    if (val !== undefined) el.textContent = val;
  });
  // innerHTML (where formatting is allowed)
  document.querySelectorAll("[data-i18n-html]").forEach(el => {
    const key = el.dataset.i18nHtml;
    let val = s[key];
    if (typeof val === "function") val = val(COUNT_TOTAL);
    if (val !== undefined) el.innerHTML = val;
  });
  // attributes
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    if (s[key]) el.setAttribute("placeholder", s[key]);
  });
  document.querySelectorAll("[data-i18n-title]").forEach(el => {
    const key = el.dataset.i18nTitle;
    if (s[key]) el.setAttribute("title", s[key]);
  });
  // Lang button labels
  const langBtn = document.getElementById("lang-btn");
  const mobileLangFab = document.getElementById("mobile-lang-fab");
  if (langBtn) langBtn.textContent = s.langBtnLabel;
  if (mobileLangFab) mobileLangFab.textContent = s.langBtnLabel;
  // <html lang> attribute
  document.documentElement.lang = lang === "zh" ? "zh-Hant-HK" : "en-GB";
  // Re-render dynamic bits
  renderLegend();
  // Re-bind every popup with translated content
  markers.forEach((m, i) => m.setPopupContent(popupHtml(DATA[i])));
  // Re-render list (uses t() for stats)
  renderList();
}
document.getElementById("lang-btn").addEventListener("click", toggleLang);
document.getElementById("mobile-lang-fab").addEventListener("click", toggleLang);
applyLanguage();

try { if (!localStorage.getItem("hkv-seen-welcome-v4")) openModal(); } catch (_) { openModal(); }

// ─── Mobile bottom-sheet ───────────────────────────────────
const sidebar = document.getElementById("sidebar");
const header = document.getElementById("sidebar-header");
function expandSheet() { sidebar.classList.add("expanded"); }
function collapseSheet() { sidebar.classList.remove("expanded"); }
function toggleSheet() { sidebar.classList.toggle("expanded"); }
header.addEventListener("click", e => {
  if (isMobile()) {
    if (e.target.closest(".icon-btn")) return;
    toggleSheet();
  }
});

let dragStartY = null;
header.addEventListener("touchstart", e => { dragStartY = e.touches[0].clientY; }, { passive: true });
header.addEventListener("touchmove", e => {
  if (dragStartY == null) return;
  const dy = e.touches[0].clientY - dragStartY;
  if (Math.abs(dy) > 28) {
    if (dy < 0) expandSheet(); else collapseSheet();
    dragStartY = null;
  }
}, { passive: true });

searchEl.addEventListener("focus", () => { if (isMobile()) expandSheet(); });

document.addEventListener("keydown", e => {
  if (e.key === "/" && document.activeElement.tagName !== "INPUT" && !modalBg.classList.contains("open")) {
    e.preventDefault();
    searchEl.focus();
  }
});

applyFilters();
</script>
</body>
</html>"""

html_out = (HTML
            .replace("__DATA__", records_json)
            .replace("__COUNT__", str(len(records)))
            .replace("__S__", str(s_count))
            .replace("__A__", str(a_count)))
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html_out)
print(f"Saved: {OUT}")
print(f"Records: {len(records)} | S: {s_count} | A: {a_count}")
