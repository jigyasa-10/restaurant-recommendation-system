"""Explainable, preference-aware restaurant ranking."""
import numpy as np
import pandas as pd


def score_restaurants(df: pd.DataFrame, preferences: dict) -> pd.DataFrame:
    """Score every restaurant before ordering results.

    Preferences influence rank rather than prematurely hiding good alternatives.
    Search is the sole hard constraint: when a user types a specific place or dish,
    results are restricted to matching places.
    """
    ranked = df.copy()
    city = preferences["city"]
    cuisine = preferences["cuisine"]
    diet = preferences["diet"]
    budget = preferences["budget"]
    rating_floor = preferences["rating"]
    delivery = preferences["delivery"]

    # Quality baseline (up to 52 points) gives strong restaurants a fair chance.
    score = ranked.Rating * 7 + ranked.Popularity * 0.17
    reasons = [[] for _ in range(len(ranked))]

    def reward(mask, points, explanation):
        nonlocal score
        score += mask.astype(int) * points
        for i, matches in enumerate(mask.to_numpy()):
            if matches:
                reasons[i].append(explanation)

    if city != "Anywhere in Tricity":
        reward(ranked.City.eq(city), 18, f"Near {city}")
    if cuisine != "Any cuisine":
        reward(ranked.Cuisine.eq(cuisine), 16, f"{cuisine} craving")
    if diet != "Any preference":
        reward(ranked.Veg.eq(diet), 12, diet)
    if delivery:
        reward(ranked.Delivery.eq("Yes"), 8, "Delivers to you")

    affordable = np.clip((budget - ranked.Cost) / max(budget, 1), -1, 1)
    score += affordable * 9
    reward(ranked.Cost.le(budget), 5, "Within your budget")
    reward(ranked.Rating.ge(rating_floor), 7, f"Rated {rating_floor:.1f}+")
    reward(ranked.Rating.ge(4.6), 4, "Guest favourite")

    ranked["AI_Score"] = np.round(np.clip(score, 0, 99)).astype(int)
    ranked["Why"] = [" · ".join(items[:3]) if items else "Strong overall value" for items in reasons]
    ranked["Best_For"] = ranked.apply(best_for, axis=1)
    return ranked


def best_for(row: pd.Series) -> str:
    if row.Rating >= 4.7:
        return "Celebrations"
    if row.Cost <= 650:
        return "Quick bites"
    if row.Cuisine == "Cafe":
        return "Coffee dates"
    if row.Popularity >= 90:
        return "Trending now"
    return "Family meals"


def apply_search_and_sort(ranked: pd.DataFrame, query: str, sort_by: str) -> pd.DataFrame:
    results = ranked.copy()
    if query.strip():
        needle = query.strip()
        searchable = results[["Restaurant", "Area", "City", "Cuisine", "Description", "Popular_Dishes"]].fillna("").agg(" ".join, axis=1)
        results = results[searchable.str.contains(needle, case=False, regex=False)]
    sorters = {
        "AI recommendation": ("AI_Score", False),
        "Highest rated": ("Rating", False),
        "Lowest cost": ("Cost", True),
        "Highest cost": ("Cost", False),
        "Most popular": ("Popularity", False),
    }
    column, ascending = sorters[sort_by]
    return results.sort_values([column, "Rating", "Popularity"], ascending=[ascending, False, False])


def apply_filters(ranked: pd.DataFrame, preferences: dict) -> pd.DataFrame:
    """Apply visible sidebar filters after scoring the complete catalogue."""
    results = ranked.copy()
    if preferences["city"] != "Anywhere in Tricity":
        results = results[results.City.eq(preferences["city"])]
    if preferences["cuisine"] != "Any cuisine":
        results = results[results.Cuisine.eq(preferences["cuisine"])]
    if preferences["diet"] != "Any preference":
        results = results[results.Veg.eq(preferences["diet"])]
    if preferences["delivery"]:
        results = results[results.Delivery.eq("Yes")]
    return results[(results.Cost <= preferences["budget"]) & (results.Rating >= preferences["rating"])]
