"""TasteTrail Tricity — a score-based restaurant recommendation dashboard."""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="TasteTrail Tricity", page_icon="🍽️", layout="wide")


@st.cache_data
def load_restaurants():
    df = pd.read_csv("data/tricity_restaurants.csv")
    df["Veg"] = df["Veg"].map({"Yes": "Vegetarian", "No": "Non-vegetarian"})
    return df


def currency(value):
    return f"₹{int(value):,}"


def recommendation_score(df, selected_cities, selected_cuisines, budget, minimum_rating, food_type, delivery_only):
    """Rank every result by preference match plus restaurant quality and value."""
    ranked = df.copy()
    score = ranked["Rating"] * 18 + ranked["Popularity"] * 0.20
    # A restaurant matching a selected preference gets a meaningful positive boost.
    if selected_cities:
        score += ranked["City"].isin(selected_cities).astype(int) * 24
    if selected_cuisines:
        score += ranked["Cuisine"].isin(selected_cuisines).astype(int) * 20
    if food_type != "Any":
        score += (ranked["Veg"] == food_type).astype(int) * 16
    if delivery_only:
        score += (ranked["Delivery"] == "Yes").astype(int) * 9
    score += np.clip((budget - ranked["Cost"]) / max(budget, 1), -1, 1) * 10
    score += np.clip((ranked["Rating"] - minimum_rating), -1, 1) * 8
    ranked["Match"] = np.round(np.clip(score, 0, 100)).astype(int)
    return ranked.sort_values(["Match", "Rating", "Popularity"], ascending=False)


def set_selected(name):
    st.session_state.selected = name


def toggle_favorite(name):
    if name in st.session_state.favorites:
        st.session_state.favorites.remove(name)
        st.toast("Removed from favorites", icon="💔")
    else:
        st.session_state.favorites.add(name)
        st.toast("Saved to favorites", icon="❤️")


restaurants = load_restaurants()
if "favorites" not in st.session_state:
    st.session_state.favorites = set()
if "selected" not in st.session_state:
    st.session_state.selected = None

st.markdown("""
<style>
    .block-container { max-width: 1420px; padding-top: 1.4rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { border-right: 1px solid #f0e7df; }
    .hero { background: linear-gradient(115deg,#1b3427 0%,#326b50 55%,#ed9847 140%); border-radius: 24px; color: #fff; padding: 2.25rem 2.6rem; margin: .2rem 0 1.4rem; }
    .hero h1 { font-size: 2.9rem; margin: 0; letter-spacing: -1.5px; }
    .hero p { margin: .45rem 0 0; font-size: 1.08rem; opacity: .9; }
    .eyebrow { color: #dd8a3c; font-weight: 700; letter-spacing: .11em; font-size: .75rem; text-transform: uppercase; }
    .card-title { font-size: 1.15rem; font-weight: 750; margin: .55rem 0 .18rem; }
    .chip { background: #fff4e9; color: #a7500c; border-radius: 99px; padding: .22rem .52rem; font-size: .76rem; margin-right: .25rem; white-space: nowrap; }
    .detail-hero { background:#f7f1e9; border-radius: 18px; padding: 1.1rem 1.35rem; }
    div[data-testid="stMetric"] { background:#fbf7f2; border-radius:13px; padding:.7rem 1rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🍽️ TasteTrail")
    st.caption("TRICITY FOOD DISCOVERY")
    st.divider()
    query = st.text_input("Search restaurant or café", placeholder="e.g. café, tandoor, biryani")
    cities = st.multiselect("Select location", ["Chandigarh", "Mohali", "Panchkula"])
    cuisines = st.multiselect("Cuisine", sorted(restaurants.Cuisine.unique()))
    budget = st.slider("Budget for two", 300, 2500, 1200, step=100)
    min_rating = st.slider("Minimum rating", 1.0, 5.0, 4.0, step=0.1)
    preference = st.radio("Food preference", ["Any", "Vegetarian", "Non-vegetarian"])
    delivery_only = st.toggle("Delivery available only")
    sort_option = st.selectbox("Sort by", ["Best match", "Highest rating", "Lowest cost", "Highest cost", "Most popular"])
    st.divider()
    st.markdown(f"❤️ **{len(st.session_state.favorites)}** saved places")

# Keep user constraints strict, then use score to rank suitable choices.
results = restaurants[(restaurants.Cost <= budget) & (restaurants.Rating >= min_rating)].copy()
if query:
    results = results[results.Restaurant.str.contains(query, case=False, na=False) | results.Cuisine.str.contains(query, case=False, na=False)]
if cities:
    results = results[results.City.isin(cities)]
if cuisines:
    results = results[results.Cuisine.isin(cuisines)]
if preference != "Any":
    results = results[results.Veg == preference]
if delivery_only:
    results = results[results.Delivery == "Yes"]
results = recommendation_score(results, cities, cuisines, budget, min_rating, preference, delivery_only)
if not results.empty and sort_option != "Best match":
    sort_col, asc = {"Highest rating": ("Rating", False), "Lowest cost": ("Cost", True), "Highest cost": ("Cost", False), "Most popular": ("Popularity", False)}[sort_option]
    results = results.sort_values([sort_col, "Rating"], ascending=[asc, False])


def restaurant_card(row):
    with st.container(border=True):
        st.image(row.Image, use_container_width=True)
        st.markdown(f"<div class='card-title'>{row.Restaurant}</div>", unsafe_allow_html=True)
        st.caption(f"📍 {row.Area}, {row.City}")
        st.markdown(f"⭐ **{row.Rating:.1f}** &nbsp; · &nbsp; {currency(row.Cost)} for two &nbsp; · &nbsp; <span class='chip'>{row.Match}% match</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='chip'>{row.Cuisine}</span><span class='chip'>{row.Veg}</span><span class='chip'>🚚 {row.Delivery}</span>", unsafe_allow_html=True)
        st.write("")
        a, b = st.columns([1.3, 1])
        a.button("View place", key=f"view-{row.ID}", on_click=set_selected, args=(row.Restaurant,), use_container_width=True)
        label = "♥ Saved" if row.Restaurant in st.session_state.favorites else "♡ Save"
        b.button(label, key=f"fav-{row.ID}", on_click=toggle_favorite, args=(row.Restaurant,), use_container_width=True)


if st.session_state.selected:
    place = restaurants[restaurants.Restaurant == st.session_state.selected].iloc[0]
    if st.button("← Back to discovery"):
        st.session_state.selected = None
        st.rerun()
    st.markdown(f"<p class='eyebrow'>{place.City} · {place.Area}</p>", unsafe_allow_html=True)
    st.title(place.Restaurant)
    photo, info = st.columns([1.05, 1])
    with photo:
        st.image(place.Image, use_container_width=True)
    with info:
        st.markdown(f"<div class='detail-hero'><h3>⭐ {place.Rating:.1f} &nbsp; · &nbsp; {place.Cuisine}</h3><p>{place.Description}</p></div>", unsafe_allow_html=True)
        st.write("")
        x, y, z = st.columns(3)
        x.metric("Cost for two", currency(place.Cost))
        y.metric("Delivery", "Available" if place.Delivery == "Yes" else "Not available")
        z.metric("Popularity", f"{place.Popularity}/100")
        st.write("")
        if place.Restaurant in st.session_state.favorites:
            st.button("♥ Remove from favorites", on_click=toggle_favorite, args=(place.Restaurant,))
        else:
            st.button("♡ Add to favorites", on_click=toggle_favorite, args=(place.Restaurant,), type="primary")
    details, menu = st.columns(2)
    with details:
        st.subheader("Visit & contact")
        st.write(f"**Address**  \\n+{place.Address}")
        st.write(f"**Phone**  \\n+{place.Phone}")
        st.write(f"**Timings**  \\n+{place.Timings}")
        maps_query = f"{place.Restaurant}, {place.Area}, {place.City}"
        st.link_button("📍 Get directions in Google Maps", f"https://www.google.com/maps/search/?api=1&query={maps_query.replace(' ', '+').replace(',', '')}")
    with menu:
        st.subheader("Food worth ordering")
        st.write(f"**Popular dishes**  \\n+{place.Popular_Dishes}")
        st.write(f"**Menu highlights**  \\n+{place.Menu}")
else:
    st.markdown("""
    <section class="hero"><span class="eyebrow" style="color:#ffd199">CHANDIGARH · MOHALI · PANCHKULA</span>
    <h1>Your next great meal is nearby.</h1><p>Explore cafés and restaurants curated for your taste, budget and plans.</p></section>
    """, unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Curated places", f"{len(restaurants)}")
    m2.metric("Across Tricity", "3 cities")
    m3.metric("Average rating", f"{restaurants.Rating.mean():.1f} ⭐")
    m4.metric("Delivery partners", f"{(restaurants.Delivery == 'Yes').sum()} places")
    st.markdown(f"<p class='eyebrow'>SMART RANKING</p>", unsafe_allow_html=True)
    st.header("Best matches for you")
    st.caption(f"{len(results)} places match your filters. Rankings consider your preferences, rating, popularity and value.")
    if results.empty:
        st.warning("No places fit all your selections. Try a higher budget or lower rating.")
    else:
        for start in range(0, len(results), 3):
            cols = st.columns(3)
            for column, (_, item) in zip(cols, results.iloc[start:start + 3].iterrows()):
                with column:
                    restaurant_card(item)

    st.divider()
    top, trending, favorites = st.tabs(["🏆 Top rated", "🔥 Trending now", "❤️ Your favorites"])
    with top:
        st.dataframe(restaurants.nlargest(10, "Rating")[["Restaurant", "City", "Cuisine", "Rating", "Cost"]], hide_index=True, use_container_width=True)
    with trending:
        st.dataframe(restaurants.nlargest(10, "Popularity")[["Restaurant", "City", "Cuisine", "Rating", "Popularity"]], hide_index=True, use_container_width=True)
    with favorites:
        saved = restaurants[restaurants.Restaurant.isin(st.session_state.favorites)]
        if saved.empty:
            st.info("Tap ♡ Save on a restaurant card to build your personal list.")
        else:
            st.dataframe(saved[["Restaurant", "City", "Cuisine", "Rating", "Cost"]], hide_index=True, use_container_width=True)

    st.divider()
    st.header("Tricity food dashboard")
    left, right = st.columns(2)
    with left:
        cuisine_chart = restaurants.Cuisine.value_counts().head(8).reset_index()
        cuisine_chart.columns = ["Cuisine", "Restaurants"]
        st.plotly_chart(px.bar(cuisine_chart, x="Restaurants", y="Cuisine", orientation="h", color="Restaurants", title="Most represented cuisines", color_continuous_scale="YlOrBr"), use_container_width=True)
    with right:
        city_chart = restaurants.groupby("City", as_index=False).agg(Restaurants=("ID", "count"), Average_Rating=("Rating", "mean"))
        st.plotly_chart(px.bar(city_chart, x="City", y="Restaurants", color="Average_Rating", text="Restaurants", title="Restaurants by city", color_continuous_scale="Teal"), use_container_width=True)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.histogram(restaurants, x="Cost", nbins=8, color="Veg", title="Cost distribution", color_discrete_sequence=["#e58b42", "#36765a"]), use_container_width=True)
    with right:
        ratings = restaurants.groupby("Cuisine", as_index=False).Rating.mean().sort_values("Rating", ascending=False).head(8)
        st.plotly_chart(px.bar(ratings, x="Cuisine", y="Rating", title="Average restaurant ratings", range_y=[3.5, 5], color="Rating", color_continuous_scale="Viridis"), use_container_width=True)
