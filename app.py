"""TasteTrail: a polished AI restaurant recommendation experience for Tricity."""
import pandas as pd
import plotly.express as px
import streamlit as st

from src.recommender import apply_search_and_sort, score_restaurants
from src.styles import apply_styles
from src.ui import footer, metric, money, restaurant_card

st.set_page_config(page_title="TasteTrail | Tricity Dining", page_icon="🍽️", layout="wide", initial_sidebar_state="expanded")


@st.cache_data(show_spinner="Curating the Tricity food scene…")
def load_restaurants():
    df = pd.read_csv("data/tricity_restaurants.csv")
    df["Veg"] = df["Veg"].map({"Yes": "Vegetarian", "No": "Non-vegetarian"})
    return df


def init_state():
    defaults = {"favorites": set(), "selected": None, "page": "Home", "theme": "Light", "home_limit": 24}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def choose_place(name):
    st.session_state.selected = name
    st.session_state.page = "Place"


def go_page(target):
    st.session_state.page = target
    if target != "Place":
        st.session_state.selected = None


def toggle_favorite(name):
    if name in st.session_state.favorites:
        st.session_state.favorites.remove(name)
        st.toast("Removed from saved restaurants", icon="💔")
    else:
        st.session_state.favorites.add(name)
        st.toast("Saved for your next plan", icon="❤️")


def save_profile():
    st.session_state.city = st.session_state.profile_location
    st.session_state.favorite_cuisines = st.session_state.profile_cuisines
    st.toast(f"Profile saved — recommendations now use {st.session_state.city}.", icon="✅")


def reset_filters():
    for key in ["search", "city", "cuisine", "budget", "rating", "diet", "delivery", "sort"]:
        st.session_state.pop(key, None)
    st.session_state.home_limit = 24


def show_more_home():
    st.session_state.home_limit += 24


def apply_active_filters(ranked, preferences):
    """Local UI filter layer, kept here to avoid reload-order issues in Streamlit."""
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


init_state()
restaurants = load_restaurants()
apply_styles(st.session_state.theme)

# Consumer-style app header; this replaces Streamlit's developer header.
brand_col, location_col, user_col, menu_col = st.columns([3.4, 2.1, 1, .45])
with brand_col:
    st.markdown("<div class='brand'>taste<span class='brand-dot'>trail</span></div>", unsafe_allow_html=True)
with location_col:
    st.markdown("<div class='topbar-location'>📍 Chandigarh · Mohali · Panchkula</div>", unsafe_allow_html=True)
with user_col:
    st.markdown("<div class='topbar-user'>👤 Jiya</div>", unsafe_allow_html=True)
with menu_col:
    with st.popover("☰", help="Open account menu"):
        st.markdown("**Jiya's account**")
        st.caption("Tricity explorer")
        st.button("Home", key="menu-home", on_click=go_page, args=("Home",), use_container_width=True)
        st.button("Discover", key="menu-discover", on_click=go_page, args=("Discover",), use_container_width=True)
        st.button("Dashboard", key="menu-dashboard", on_click=go_page, args=("Dashboard",), use_container_width=True)
        st.button("Saved restaurants", key="menu-saved", on_click=go_page, args=("Saved",), use_container_width=True)
        st.button("My profile", key="menu-profile", on_click=go_page, args=("Profile",), use_container_width=True)
        st.button("About TasteTrail", key="menu-about", on_click=go_page, args=("About",), use_container_width=True)
        st.divider()
        st.caption("Current location: " + (st.session_state.get("city", "Anywhere in Tricity").replace("Anywhere in ", "")))

with st.sidebar:
    st.markdown("<div class='brand'>taste<span class='brand-dot'>trail</span></div><div class='nav-note'>AI dining companion</div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div class='nav-note'>FIND YOUR TABLE</div>", unsafe_allow_html=True)
    query = st.text_input("Search", placeholder="Restaurant, area, dish…", key="search")
    city = st.selectbox("Current location", ["Anywhere in Tricity", "Chandigarh", "Mohali", "Panchkula"], key="city")
    cuisine = st.selectbox("Cuisine", ["Any cuisine"] + sorted(restaurants.Cuisine.unique()), key="cuisine")
    budget = st.slider("Budget for two", 300, 2500, 1200, 100, key="budget")
    rating = st.slider("Minimum rating", 3.5, 4.9, 4.1, .1, key="rating")
    diet = st.selectbox("Food preference", ["Any preference", "Vegetarian", "Non-vegetarian"], key="diet")
    delivery = st.toggle("Delivery available", key="delivery")
    sort_by = st.selectbox("Sort results", ["AI recommendation", "Highest rated", "Most popular", "Lowest cost", "Highest cost"], key="sort")
    st.button("Clear filters", on_click=reset_filters, use_container_width=True)
    st.divider()
    st.markdown("<div class='nav-note'>YOUR PROFILE</div>", unsafe_allow_html=True)
    st.markdown(f"**👤 Jiya**  \n<span class='muted'>📍 {city.replace('Anywhere in ', '') if city != 'Anywhere in Tricity' else 'Tricity'}</span>", unsafe_allow_html=True)
    st.caption(f"❤️ {len(st.session_state.favorites)} saved restaurants")

preferences = {"city": city, "cuisine": cuisine, "budget": budget, "rating": rating, "diet": diet, "delivery": delivery}
with st.spinner("AI is tailoring your dining shortlist…"):
    ranked = score_restaurants(restaurants, preferences)
    filtered = apply_active_filters(ranked, preferences)
    results = apply_search_and_sort(filtered, query, sort_by)

page = st.session_state.page


def show_detail(place):
    if st.button("← Back to recommendations"):
        st.session_state.page = "Discover"
        st.session_state.selected = None
        st.rerun()
    st.markdown(f"<div class='kicker'>{place.City} · {place.Area} · AI score {place.AI_Score}/99</div>", unsafe_allow_html=True)
    st.title(place.Restaurant)
    photo, summary = st.columns([1.08, 1])
    with photo:
        st.markdown(f"<img class='detail-image' src='{place.Image}' alt='{place.Restaurant}'>", unsafe_allow_html=True)
    with summary:
        st.markdown(f"<div class='detail-banner'><h3>★ {place.Rating:.1f} &nbsp; · &nbsp; {place.Cuisine}</h3><p>{place.Description}</p><span class='pill ai-pill'>✦ {place.Why}</span></div>", unsafe_allow_html=True)
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            metric(money(place.Cost), "for two", "₹")
        with c2:
            metric("Yes" if place.Delivery == "Yes" else "No", "delivery", "🚚")
        with c3:
            metric(f"{place.Popularity}/100", "local buzz", "🔥")
        st.write("")
        st.markdown("**Perfect for** &nbsp; " + " ".join(f"<span class='pill'>{tag}</span>" for tag in [place.Best_For, "Date night", "Groups"]), unsafe_allow_html=True)
        st.write("")
        label = "♥ Remove from saved" if place.Restaurant in st.session_state.favorites else "♡ Save this place"
        st.button(label, key="detail-save", on_click=toggle_favorite, args=(place.Restaurant,), type="primary")
    visit, dishes = st.columns(2)
    with visit:
        st.subheader("Plan your visit")
        st.markdown(f"**Address**  \n{place.Address}")
        st.markdown(f"**Call**  \n{place.Phone}")
        st.markdown(f"**Hours**  \n{place.Timings}")
        query_maps = f"{place.Restaurant} {place.Area} {place.City}".replace(" ", "+")
        st.link_button("📍 Open directions in Google Maps", f"https://www.google.com/maps/search/?api=1&query={query_maps}")
    with dishes:
        st.subheader("Worth ordering")
        st.markdown(f"**Popular dishes**  \n{place.Popular_Dishes}")
        st.markdown(f"**Menu highlights**  \n{place.Menu}")
    st.subheader("What diners are saying")
    reviews = [("Ananya S.", "The food was full of flavour and the staff made our evening feel special."), ("Rohan K.", "Great ambience, quick service, and I would happily return for the signature dishes."), ("Mehak G.", "A reliable choice in the area—especially good for an unhurried catch-up.")]
    cols = st.columns(3)
    for column, (name, text) in zip(cols, reviews):
        with column:
            st.markdown(f"<div class='review'><b>{name}</b> <span class='rating'>★ 4.8</span><br><br><span class='muted'>{text}</span></div>", unsafe_allow_html=True)


def show_dashboard():
    st.markdown("<div class='kicker'>TRICITY INTELLIGENCE</div>", unsafe_allow_html=True)
    st.title("The food scene, decoded.")
    st.caption("Live insights from TasteTrail’s curated Tricity catalogue.")
    colors = ["#ef6c3b", "#155a43", "#f4b860", "#4c8d70"]
    dark = st.session_state.theme == "Dark"
    chart_bg = "#17211c" if dark else "#ffffff"
    chart_text = "#f4f6f3" if dark else "#1d2922"
    chart_template = "plotly_dark" if dark else "plotly_white"
    common = dict(template=chart_template, paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, font_color=chart_text, margin=dict(l=0, r=0, t=50, b=0))
    c1, c2 = st.columns(2)
    with c1:
        cuisines = restaurants.Cuisine.value_counts().head(8).reset_index(); cuisines.columns = ["Cuisine", "Places"]
        fig = px.bar(cuisines, x="Places", y="Cuisine", orientation="h", color="Places", color_continuous_scale=["#ffe7d2", "#ef6c3b"], title="Most represented cuisines")
        fig.update_layout(**common, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        places = restaurants.City.value_counts().reset_index(); places.columns = ["City", "Places"]
        fig = px.pie(places, names="City", values="Places", hole=.58, color_discrete_sequence=colors, title="Restaurants across Tricity")
        fig.update_layout(**common, legend=dict(orientation="h", y=-.1))
        st.plotly_chart(fig, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(restaurants, x="Cost", nbins=9, color="Veg", barmode="overlay", color_discrete_sequence=["#155a43", "#ef6c3b"], title="Cost distribution for two")
        fig.update_layout(**common, legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        avg = restaurants.groupby("Cuisine", as_index=False).Rating.mean().sort_values("Rating", ascending=False).head(8)
        fig = px.bar(avg, x="Cuisine", y="Rating", color="Rating", range_y=[3.7, 5], color_continuous_scale=["#9ed5b9", "#155a43"], title="Highest rated food categories")
        fig.update_layout(**common, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)


def show_discover():
    st.markdown("<div class='kicker'>EXPLORE THE TRICITY</div>", unsafe_allow_html=True)
    st.title("Discover your next favourite")
    st.caption(f"{len(results)} places match your active filters. Every result is first ranked by TasteTrail’s AI, then filtered to exactly what you asked for.")
    if results.empty:
        st.info("No restaurants match every filter. Increase your budget, lower the rating, or clear filters to explore more places.")
        st.button("Clear all filters", on_click=reset_filters, type="primary")
        return
    for start in range(0, len(results), 3):
        cols = st.columns(3)
        for col, (_, row) in zip(cols, results.iloc[start:start + 3].iterrows()):
            with col:
                restaurant_card(row, st.session_state.favorites, choose_place, toggle_favorite, st.session_state.theme == "Dark")


if page == "Place" and st.session_state.selected:
    show_detail(ranked[ranked.Restaurant.eq(st.session_state.selected)].iloc[0])
elif page == "Dashboard":
    show_dashboard()
elif page == "Discover":
    show_discover()
elif page == "Saved":
    st.markdown("<div class='kicker'>YOUR SHORTLIST</div>", unsafe_allow_html=True)
    st.title("Saved for your next plan")
    saved = ranked[ranked.Restaurant.isin(st.session_state.favorites)]
    if saved.empty:
        st.info("Your saved list is waiting. Discover a place and tap Save to keep it here.")
        st.button("Explore restaurants", on_click=lambda: st.session_state.update(page="Discover"), type="primary")
    else:
        for start in range(0, len(saved), 3):
            cols = st.columns(3)
            for col, (_, row) in zip(cols, saved.iloc[start:start+3].iterrows()):
                with col: restaurant_card(row, st.session_state.favorites, choose_place, toggle_favorite, st.session_state.theme == "Dark")
elif page == "Profile":
    st.markdown("<div class='kicker'>JIYA'S SPACE</div>", unsafe_allow_html=True)
    st.title("Your TasteTrail profile")
    first, second = st.columns([1.1, .9])
    with first:
        st.markdown("### 👤 Jiya")
        st.write("Your personal dining profile helps TasteTrail make more relevant suggestions.")
        st.selectbox("Current location", ["Chandigarh", "Mohali", "Panchkula"], index=["Chandigarh", "Mohali", "Panchkula"].index(city) if city in ["Chandigarh", "Mohali", "Panchkula"] else 0, key="profile_location")
        st.multiselect("Favourite cuisines", sorted(restaurants.Cuisine.unique()), default=st.session_state.get("favorite_cuisines", ["Cafe", "North Indian"]), key="profile_cuisines")
        st.button("Save profile", on_click=save_profile, type="primary")
    with second:
        st.markdown("### Settings")
        theme = st.radio("Appearance", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1, key="profile_theme")
        if theme != st.session_state.theme:
            st.session_state.theme = theme; st.rerun()
elif page == "About":
    st.markdown("<div class='kicker'>ABOUT TASTETRAIL</div>", unsafe_allow_html=True)
    st.title("Better dining plans start here.")
    st.write("TasteTrail is a local-first AI dining companion for Chandigarh, Mohali and Panchkula. It is designed to make the familiar question—‘Where should we eat?’—quick, personal and genuinely useful.")
    a, b, c = st.columns(3)
    with a: metric("210", "curated Tricity places", "✦")
    with b: metric("6", "personalised signals", "🧠")
    with c: metric("3", "cities covered", "📍")
    st.markdown("### How recommendations work")
    st.write("Every restaurant is scored before it is shown. The score combines quality and local popularity with your location, cuisine, budget, minimum rating, diet and delivery needs. The ‘Why it fits’ note on every card makes the recommendation transparent.")
    st.markdown("### Our catalogue")
    st.write("The catalogue contains 210 detailed sample restaurants and cafés across Chandigarh, Mohali and Panchkula. Each entry includes cuisine, price for two, rating, delivery availability, area, popular dishes, menu highlights and a directions link.")
    st.markdown("### Made for real plans")
    st.write("Save possibilities for later, compare places in the Dashboard, or open a restaurant to see visit details, dishes, reviews and Google Maps directions. TasteTrail keeps discovery local, clear and fun.")
else:
    st.markdown("<section class='hero'><div class='kicker'>TRICITY'S AI DINING GUIDE</div><h1>Find a table that feels made for your plan.</h1><p>From coffee catch-ups to celebration dinners, TasteTrail learns your preferences and makes choosing effortless.</p></section>", unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    with a: metric("180", "curated places", "✦")
    with b: metric("3", "Tricity cities", "📍")
    with c: metric(f"{restaurants.Rating.mean():.1f}", "average rating", "★")
    with d: metric(f"{len(st.session_state.favorites)}", "saved by you", "♥")
    st.write("")
    st.markdown("<div class='kicker'>PERSONALISED FOR YOU</div>", unsafe_allow_html=True)
    st.header("Your AI dining shortlist")
    st.caption(f"Showing {min(len(results), st.session_state.home_limit)} of {len(results)} matches from our 210-place Tricity catalogue. Every place is scored on your preferences, dining quality, popularity and value.")
    if results.empty:
        st.info("No places match that search. Try an area, cuisine, or a popular dish instead.")
        st.button("Reset search", on_click=reset_filters)
    else:
        for start in range(0, min(len(results), st.session_state.home_limit), 3):
            cols = st.columns(3)
            for col, (_, row) in zip(cols, results.iloc[start:start+3].iterrows()):
                with col: restaurant_card(row, st.session_state.favorites, choose_place, toggle_favorite, st.session_state.theme == "Dark")
        if len(results) > st.session_state.home_limit:
            center = st.columns([1, 1, 1])[1]
            with center:
                st.button("Show 24 more restaurants", on_click=show_more_home, use_container_width=True)
        else:
            st.caption("You have reached the end of this personalised list. Use Discover to browse the complete matching catalogue.")
footer()
