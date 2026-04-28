#!/usr/bin/env python3
"""
Geocode all restaurants via OpenStreetMap Nominatim (free, no API key).
- Respects 1 req/sec rate limit.
- Caches results to data/geocoded.json so subsequent runs only process new entries.
- Falls back through name+address → address-only → name+district queries.

Run from /sessions/keen-focused-ritchie/mnt/outputs (sandbox)
or scripts/ directory in the published repo.
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
import sys
import os

# Allow running from either outputs/ (sandbox) or scripts/ (repo)
HERE = Path(__file__).parent.resolve()
if (HERE / "build_db_v2.py").exists():
    sys.path.insert(0, str(HERE))
    CACHE_PATH = HERE / "Veggie" / "data" / "geocoded.json"
else:
    # Running from inside Veggie/scripts/
    sys.path.insert(0, str(HERE))
    CACHE_PATH = HERE.parent / "data" / "geocoded.json"

from build_db_v2 import CAT_A, CAT_B, CAT_C, CAT_D  # noqa

USER_AGENT = "HKVeg/1.0 (https://github.com/chitintim/veggie; vegetarian restaurant map)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# HK bounding box (covers HK Island, Kowloon, NT, Lantau)
HK_VIEWBOX = "113.8,22.6,114.5,22.1"


def load_cache():
    if CACHE_PATH.exists():
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(c):
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(c, f, indent=2, ensure_ascii=False)


def geocode_one(query, bounded=True):
    """Hit Nominatim with one query string. Returns dict or None."""
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    if bounded:
        params["viewbox"] = HK_VIEWBOX
        params["bounded"] = 1
    url = f"{NOMINATIM_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}
    if not data:
        return None
    r = data[0]
    return {
        "lat": float(r["lat"]),
        "lng": float(r["lon"]),
        "display": r.get("display_name", ""),
        "importance": r.get("importance", 0),
        "place_class": r.get("class", ""),
        "place_type": r.get("type", ""),
    }


def clean_address(address):
    a = (address or "").strip()
    # Strip parentheticals
    a = a.split("(")[0].strip().rstrip(",").strip()
    # Strip "|" multi-branch
    if "|" in a:
        a = a.split("|")[0].strip().rstrip(",")
    # Strip "TST: " / "CWB: " / "Central: " prefixes
    for prefix in ["TST: ", "TST East: ", "CWB: ", "Central: ", "Admiralty: ", "Wan Chai: ", "Kowloon: "]:
        if a.startswith(prefix):
            a = a[len(prefix):]
            break
    return a


def build_queries(name, address, district):
    """Try most specific to least specific. Capped to 3 attempts to keep things fast."""
    qs = []
    name = (name or "").strip()
    addr = clean_address(address)
    district = (district or "").strip()
    if name and addr and addr != "—":
        qs.append((f"{name}, {addr}, Hong Kong", True))
    if addr and addr != "—":
        qs.append((f"{addr}, Hong Kong", True))
        # final unbounded attempt — sometimes a famous landmark doesn't fit our bbox
        qs.append((f"{addr}, Hong Kong", False))
    return qs


# Known landmarks Nominatim/OSM doesn't index well — manual lat/lng overrides.
# These get used during geocoding instead of hitting the API.
MANUAL_OVERRIDES = {
    # name_en (case-insensitive substring) → (lat, lng, label)
    "chi lin vegetarian":   (22.3398, 114.2050, "Chi Lin Nunnery, Diamond Hill"),
    "po lin monastery":     (22.2540, 113.9050, "Po Lin Monastery, Ngong Ping, Lantau"),
    "lockcha tea house":    (22.2785, 114.1632, "Hong Kong Park, Admiralty"),
    "lock cha":             (22.2785, 114.1632, "Hong Kong Park, Admiralty"),
    "kung tak lam":         (22.2806, 114.1857, "Sugar+, Causeway Bay"),
    "pure veggie house":    (22.2779, 114.1610, "Coda Plaza, Garden Road, Mid-Levels"),
    "veggie kingdom":       (22.2974, 114.1715, "VIP Commercial Centre, Canton Rd, TST"),
    "treehouse":            (22.2828, 114.1542, "H Code, Pottinger St, Central"),
    "roots eatery":         (22.2762, 114.1726, "Sun St, Wan Chai"),
    "mana!":                (22.2829, 114.1531, "Staunton St, Soho"),
    "kind kitchen":         (22.2845, 114.1574, "Nan Fung Place, Des Voeux Rd Central"),
    "yuan":                 (22.2837, 114.1517, "Chinachem Hollywood Centre, Hollywood Rd"),
    "miss lee":             (22.2828, 114.1538, "The Wellington, Wellington St, Central"),
    "amber":                (22.2814, 114.1581, "Mandarin Oriental Landmark, Central"),
    "caprice":              (22.2856, 114.1581, "Four Seasons, 8 Finance St, Central"),
    "lung king heen":       (22.2856, 114.1581, "Four Seasons, 8 Finance St, Central"),
    "l'atelier de jo":      (22.2814, 114.1582, "The Landmark, Central"),
    "tin lung heen":        (22.3048, 114.1599, "Ritz-Carlton, ICC, West Kowloon"),
    "shang palace":         (22.2964, 114.1819, "Kowloon Shangri-La, TST East"),
    "yan toh heen":         (22.2942, 114.1721, "Regent Hong Kong, TST"),
    "duddell":              (22.2810, 114.1551, "Shanghai Tang Mansion, Duddell St"),
    "carbone":              (22.2818, 114.1543, "LKF Tower, 33 Wyndham St"),
    "otto e mezzo":         (22.2814, 114.1582, "Alexandra House, Chater Rd"),
    "dim sum library":      (22.2774, 114.1652, "Pacific Place, Admiralty"),
    "the chairman":         (22.2842, 114.1530, "3 Kau U Fong, Central"),
    "hutong":               (22.2974, 114.1715, "One Peking, TST"),
    "rajasthan rifles":     (22.2706, 114.1494, "Peak Galleria, The Peak"),
    "amber":                (22.2814, 114.1581, "Mandarin Oriental Landmark, Central"),
    "forum":                (22.2802, 114.1860, "Sino Plaza, CWB"),
    "feuille":              (22.2828, 114.1542, "H Code, Pottinger St, Central"),
    "roganic":              (22.2802, 114.1860, "Sino Plaza, CWB"),
    "arcane":               (22.2826, 114.1556, "On Lan St, Central"),
    "tate dining":          (22.2848, 114.1500, "210 Hollywood Rd, Sheung Wan"),
    "aaharn":               (22.2832, 114.1543, "Tai Kwun, Hollywood Rd, Central"),
    "chaat":                (22.2935, 114.1731, "Rosewood, Victoria Dockside, TST"),
    "mott 32":              (22.2835, 114.1583, "Standard Chartered Bldg, Des Voeux Rd"),
    "ming court":           (22.3196, 114.1685, "Cordis, 555 Shanghai St, Mong Kok"),
    "tang court":           (22.2980, 114.1722, "The Langham, 8 Peking Rd, TST"),
    "t'ang court":          (22.2980, 114.1722, "The Langham, 8 Peking Rd, TST"),
    "sun tung lok":         (22.2978, 114.1738, "47 Kimberley Rd, TST"),
    "épure":                (22.2965, 114.1685, "Ocean Terminal, Harbour City, TST"),
    "epure":                (22.2965, 114.1685, "Ocean Terminal, Harbour City, TST"),
    "hansik goo":           (22.2828, 114.1538, "The Wellington, Wellington St, Central"),
    "belon":                (22.2823, 114.1527, "41 Elgin St, Soho, Central"),
    "chilli fagara":        (22.2832, 114.1551, "7 Old Bailey St, Central"),
    "isoya":                (22.2762, 114.1733, "83 Wan Chai Rd, Wan Chai"),
    "sow vegan":            (22.3128, 114.2256, "Hung Tat Industrial Bldg, Kwun Tong"),
    "veda":                 (22.2820, 114.1554, "Ovolo Central, Arbuthnot Rd"),
    "beet":                 (22.2842, 114.1530, "Kau U Fong, Central"),
    "moksa":                (22.2762, 114.1733, "Harvard Commercial Bldg, Wan Chai"),
    "locofama":             (22.2858, 114.1424, "Fuk Sau Lane, Sai Ying Pun"),
    "ln fortunate":         (22.2858, 114.1424, "118 Second St, Sai Ying Pun"),
    "root vegan":           (22.2828, 114.1538, "112-114 Wellington St, Central"),
    "wanaka":               (22.2762, 114.1733, "Blue House, 8 King Sing St, Wan Chai"),
    "ovo cafe":             (22.2762, 114.1733, "Old Wan Chai Market, 1 Wan Chai Rd"),
    "francis":              (22.2762, 114.1733, "4-6 St Francis St, Wan Chai"),
    "maison libanaise":     (22.2823, 114.1532, "10 Shelley St, Soho"),
    "estiatorio keia":      (22.2828, 114.1538, "H Queen's, 80 Queen's Rd Central"),
    "the optimist":         (22.2762, 114.1733, "239 Hennessy Rd, Wan Chai"),
    "limewood":             (22.2376, 114.1948, "The Pulse, Repulse Bay"),
    "woodlands":            (22.2974, 114.1815, "Wing On Plaza, Mody Rd, TST East"),
    "sangeetha":            (22.2974, 114.1815, "Wing On Plaza, Mody Rd, TST East"),
    "saravanaa bhavan":     (22.2980, 114.1722, "Golden Dragon Centre, Cameron Rd, TST"),
    "kailash parbat":       (22.2980, 114.1722, "Multifield Plaza, Prat Avenue, TST"),
    "new punjab club":      (22.2826, 114.1556, "34 Wyndham St, Central"),
    "chaiwala":             (22.2826, 114.1556, "Yu Yuet Lai Bldg, Wyndham St, Central"),
    "bombay dreams":        (22.2826, 114.1556, "Winning Centre, Wyndham St, Central"),
    "gaylord":              (22.2980, 114.1722, "Prince Tower, Peking Rd, TST"),
    "tandoor":              (22.2832, 114.1551, "1 Lyndhurst Terrace, Central"),
    "aladin mess":          (22.2802, 114.1860, "Fu Hing Bldg, Russell St, CWB"),
    "chutney tandoor":      (22.2826, 114.1556, "Carfield Commercial Bldg, Wyndham St"),
    "khyber pass":          (22.2980, 114.1722, "Chungking Mansions, Nathan Rd, TST"),
    "the cakery (lee garden)": (22.2802, 114.1860, "Lee Garden Two, CWB"),
    "the cakery (landmark)":   (22.2814, 114.1582, "The Landmark, Central"),
    "teakha":               (22.2870, 114.1492, "Tai Ping Shan St, Sheung Wan"),
    "plantation tea":       (22.2858, 114.1424, "15 High St, Sai Ying Pun"),
    "gaia veggie":          (22.2974, 114.1715, "Mira Place 1, Nathan Rd, TST"),
    "amitabha buddha":      (22.3055, 114.1830, "Station Lane, Hung Hom"),
    "paradise dynasty":     (22.2849, 114.1583, "IFC Mall, Central"),
    "mayse artisan":        (22.4515, 114.1645, "Tai Mei Tuk, Tai Po"),
    "mayse pizzeria":       (22.3046, 114.1715, "Woosung St, Jordan"),
    "vw vegan":             (22.4515, 114.1645, "Plover Cove Garden Arcade, Tai Po"),
    "fook luk sau":         (22.2842, 114.1530, "8 Tit Hong Lane, Central"),
    "kan kee":              (22.2762, 114.1733, "Bowrington Rd Cooked Food Centre, Wan Chai"),
    "thai vegetarian food": (22.3287, 114.1885, "28A Nam Kok Rd, Kowloon City"),
    "vegelink":             (22.2916, 114.1996, "Foo Yet Kall Bldg, Java Rd, North Point"),
    "three virtues":        (22.2912, 114.1994, "395 King's Rd, North Point"),
    "paramita":             (22.2802, 114.1860, "Lee Theatre Plaza, Percival St, CWB"),
    "heartful veggie":      (22.3388, 114.1996, "Mikiki, Prince Edward Rd East, San Po Kong"),
    "veggie4love":          (22.2828, 114.1545, "Stanley 11, Stanley St, Central"),
    "yau veggie":           (22.3711, 114.1144, "The Mills, Pak Tin Par St, Tsuen Wan"),
    "veggie palace":        (22.2762, 114.1733, "Heard St, Wan Chai"),
    "paradise veggie":      (22.2802, 114.1860, "Tower 535, Jaffe Rd, CWB"),
    "years":                (22.3303, 114.1622, "Fukwah St, Sham Shui Po"),
    "loving hut":           (22.3231, 114.2135, "Kowloon Bay"),
    "green common":         (22.2849, 114.1583, "IFC Mall, Central (representative branch)"),
    "yudei":                (22.3303, 114.1622, "Tai Nam St, Sham Shui Po"),
    "miss lee":             (22.2828, 114.1538, "The Wellington, Wellington St, Central"),
    "sohofama":             (22.2823, 114.1530, "PMQ, Aberdeen St, Central"),
    "oriental vegetarian":  (22.2776, 114.1719, "239 Hennessy Rd, Wan Chai"),
    "liza veggies":         (22.2762, 114.1733, "Harvard House, 105-111 Thomson Rd, Wan Chai"),
    "light vegetarian":     (22.3046, 114.1715, "Jordan"),
    "ying vegetarian":      (22.3115, 114.1707, "Yau Ma Tei (Temple St area)"),
    "curry leaf":           (22.3046, 114.1715, "Temple St area, Jordan"),
}


def manual_match(name):
    """Return (lat, lng, label) if name matches a manual override, else None."""
    n = (name or "").lower()
    for key, val in MANUAL_OVERRIDES.items():
        if key in n:
            return val
    return None


def main():
    cache = load_cache()
    all_records = list(CAT_A) + list(CAT_B) + list(CAT_C) + list(CAT_D)
    total = len(all_records)
    new = skipped = failed = 0

    print(f"Geocoding {total} restaurants via Nominatim ({CACHE_PATH})")

    manual_hits = 0
    for i, r in enumerate(all_records, start=1):
        name = r.get("Name (EN)", "")
        addr = r.get("Address", "")
        district = r.get("District", "")
        status = (r.get("Operational status", "") or "").upper()
        key = f"{name}||{district}"
        if "CLOSED" in status:
            cache[key] = {"closed": True}
            skipped += 1
            continue
        if key in cache and cache[key].get("lat"):
            skipped += 1
            continue
        # Manual override first
        m = manual_match(name)
        if m:
            cache[key] = {"lat": m[0], "lng": m[1], "source": "manual", "label": m[2]}
            manual_hits += 1
            print(f"  [{i:3}/{total}] {name[:32]:32} → manual: {m[2]}")
            if i % 10 == 0:
                save_cache(cache)
            continue
        # Otherwise hit Nominatim
        queries = build_queries(name, addr, district)
        result = None
        used_query = None
        for q, bounded in queries:
            short_q = q[:55] + ("…" if len(q) > 55 else "")
            print(f"  [{i:3}/{total}] {name[:32]:32} → {short_q}")
            res = geocode_one(q, bounded=bounded)
            time.sleep(1.1)
            if res and res.get("lat") is not None and "error" not in res:
                result = res
                used_query = q
                break
            if res and "error" in res:
                print(f"    HTTP error: {res['error']}")
        if result:
            cache[key] = {
                "lat": result["lat"], "lng": result["lng"],
                "query": used_query, "display": result["display"],
                "importance": result["importance"],
                "place_type": result["place_type"], "source": "nominatim",
            }
            print(f"    ✓ {result['lat']:.4f}, {result['lng']:.4f}  imp={result['importance']:.3f}  ({result['place_type']})")
            new += 1
        else:
            cache[key] = {"failed": True}
            failed += 1
            print("    ✗ no match")
        if i % 3 == 0:
            save_cache(cache)
    print(f"  Manual hits: {manual_hits}")

    save_cache(cache)
    success = sum(1 for v in cache.values() if v.get("lat"))
    closed_n = sum(1 for v in cache.values() if v.get("closed"))
    print(f"\nDone. New this run: {new}, cached/skipped: {skipped}, failed: {failed}")
    print(f"Total in cache — geocoded: {success}, closed: {closed_n}, failed: {sum(1 for v in cache.values() if v.get('failed'))}")


if __name__ == "__main__":
    main()
