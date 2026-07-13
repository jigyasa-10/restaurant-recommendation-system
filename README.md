# TasteTrail Tricity — Restaurant Recommendation System

A Streamlit restaurant discovery app for Chandigarh, Mohali, and Panchkula. It includes a cleaned 180-place catalogue, weighted score-based recommendations, sorting, saved favorites, detailed pages, Google Maps links, images, and interactive analytics.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The cleaned catalogue lives in `data/tricity_restaurants.csv`. To recreate it, run `python data/generate_tricity_dataset.py`.
