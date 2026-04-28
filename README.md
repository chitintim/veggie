# 🌱 HK Veg

Finding a decent veggie restaurant in Hong Kong shouldn't be this annoying. OpenRice is full of paid 5★ reviews. HappyCow recycles the same 10 expat spots. Google reviews split bimodal between 5s and 1s with nothing in the middle.

So I roped in Claude and built this — **103 vegetarian-friendly restaurants in Hong Kong**, ranked by a transparent quality score that doesn't get fooled by paid reviews.

## What you get

- **Interactive map** ([`index.html`](./index.html)) — Leaflet-based, dark UI, mobile-friendly. Filter by category, tier, score, vegan-only, Jain-friendly, critic-recognised, trusted-reviews-only.
- **Spreadsheet database** ([`data/HK_Vegetarian_Restaurants_Database.xlsx`](./data/HK_Vegetarian_Restaurants_Database.xlsx)) — Top Picks tab + master sheet + per-category tabs + README with methodology.

## Categories

- 🟡 **Chinese 齋** — dedicated Buddhist veg, mock-meat, traditional dim sum
- 🟢 **Modern plant-based** — newer-wave vegan/vegetarian places
- 🟠 **Mainstream w/ veg menu** — non-veg restaurants where the veg side isn't an afterthought
- 🟣 **Indian / ME / Med** — pure-veg & naturally veg-heavy cuisines

## How the score works

Each place gets a 0–100 score:

1. **Bayesian-weighted user ratings** across Google, OpenRice, HappyCow. A 4.9★ with 8 reviews can't outrank a 4.5★ with 800.
2. **Critic bonus**: `+15` for ★★★ Michelin, `+10` ★★, `+7` ★, `+4` Bib Gourmand / Tatler / Time Out.
3. **Penalties** for suspect reviews (bimodal OpenRice patterns) and dodgy operating status.

Tiers: **S** (85+), **A** (75–84), **B** (65–74), **C** (55–64), **D** (<55). Closed places sink to the bottom.

Full methodology lives in the README sheet of the xlsx.

## Run it

The map is a single self-contained HTML file. Just open it:

```bash
open index.html
```

Or serve over HTTP if your browser blocks local file features:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Rebuild the data + map

If you want to update / add restaurants:

```bash
cd scripts
pip install openpyxl
python3 build_db_v2.py     # rebuilds data/HK_Vegetarian_Restaurants_Database.xlsx
python3 build_map_v3.py    # rebuilds index.html
```

The data lives in `scripts/build_db.py` (base list) and `scripts/build_db_v2.py` (newer additions + scoring). Edit those, re-run, redeploy.

## Caveats

- Restaurant operating status shifts constantly in HK. The database flags closures (Branto, Bedu, Soil to Soul, Greenwoods Raw) and uncertain places (Veda, Chilli Fagara, Belon, Hansik Goo post-relocation). Phone or check Instagram before high-stakes plans.
- Marker positions on the map are district-centroid + small jitter, not exact addresses. Use the Google Maps button in the popup for actual navigation.
- Ratings shown as "X.X (N+ reviews)" are aggregated/rounded; counts shift weekly.

## Credits

Compiled April 2026 with Claude doing the heavy lifting — data research, scoring formula, map UI, the lot.

Style notes nicked from [chitintim.github.io](https://chitintim.github.io).

— Tim
