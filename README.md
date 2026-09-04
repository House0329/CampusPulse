# CampusPulse

CampusPulse is a task-aware study-space decision prototype that turns synthetic space attributes into explainable comparisons on a schematic campus map.

中文：CampusPulse 是一个面向学习任务的选址原型。它用合成的地点属性，在示意校园地图上给出可解释的比较，而不是真实导航或真实学生调查。

**Synthetic campus data · Schematic map · For prototype evaluation only.**

## Repository

GitHub: https://github.com/House0329/CampusPulse

## What this project is

A lightweight Streamlit prototype for choosing where to study **given what you need to do today**. Users pick a task, a schematic starting point, and up to three priorities. The app ranks 18 fictional spaces, shows a Top 3 on an inline SVG map, explains the match, and lets you compare 2–3 places.

A good study space is not universally “good” — it is good for a particular task, at a particular moment, for a particular set of priorities.

## What this project is not

- Not a real campus map or navigation tool.
- Not a dataset of observed student surveys.
- Not a recruited user study. `research/synthetic_evaluation.csv` is illustrative layout / acceptance-target data only.

See [DATA_NOTE.md](DATA_NOTE.md) and [research/README.md](research/README.md).

## Run

Python 3.11+ recommended.

```bash
pip install -r requirements.txt
python scripts/build_dataset.py
python scripts/generate_synthetic_eval.py
python -m pytest
streamlit run app.py
```

Runtime stack is only **Streamlit + Pandas + NumPy**. Tests use **pytest**. There is no database, no map tiles, no scikit-learn, and no API calls.

## How matching works

1. Each task has a **design preset** (weights sum to 1). These are design defaults, not survey results.
2. Up to three priority chips each add `+0.08` before the weights are renormalised.
3. Ratings are scaled to 0–1. Distance is schematic walking effort on a 0–100 canvas, not metres.
4. `Match = 100 × (0.70 × attribute score + 0.30 × task fit)`.
5. Each recommendation shows two positive reasons and one trade-off. Raw weights are never shown.

Space types (Deep Focus, Quick Work, Social Study, Group Collaboration) come from a **precomputed** NumPy K-Means run. PCA coordinates are stored for analysis plots only; they are not map coordinates.

## Project layout

```text
app.py                 Streamlit entry
src/                   data, matching, explain, SVG map, UI
data/locations.csv     18 synthetic spaces + cluster + PCA
scripts/               rebuild dataset / illustrative eval
tests/                 unit, scenario, and AppTest checks
research/              synthetic evaluation (illustrative)
assets/screenshots/    capture instructions
```

## Screenshots

Product captures of the four surfaces, plus 390 px mobile views:

- `assets/screenshots/01_discover.png`
- `assets/screenshots/02_results_map.png`
- `assets/screenshots/03_detail.png`
- `assets/screenshots/04_compare.png`
- `assets/screenshots/01_discover_mobile.png`
- `assets/screenshots/02_results_mobile.png`

How they were framed: [assets/screenshots/README.md](assets/screenshots/README.md).

The 12-section write-up is `CampusPulse_case_study.pdf`. Evaluation charts inside it are labelled **synthetic / illustrative**.

## Portfolio notes

Suggested case-study arc: problem (overall rating cannot answer “where should I study *today*?”) → constraints (synthetic prototype) → dataset and clustering → task-first matching → map / why / compare → functional tests + labelled synthetic benchmark → limits and a future real-campus study.

If you later run a small formative test (6–8 students is enough), report it separately. Do not rewrite the synthetic benchmark as if it were that study.

## Package for submission

Zip the `CampusPulse/` folder itself (one top-level folder, not nested). Exclude `.git/`, `__pycache__/`, `.pytest_cache/`, `.venv/`, logs, and editor folders. Target: zip under 3 MB without a demo video.

## License / use

Educational and portfolio prototyping only. Do not treat locations, ratings, or evaluation numbers as facts about any university.
