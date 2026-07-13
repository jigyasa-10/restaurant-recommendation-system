"""Reusable consumer-facing UI components."""
from html import escape
import streamlit as st


def money(value):
    return f"₹{int(value):,}"


def metric(value, label, icon):
    st.markdown(f"<div class='metric-card'><div class='metric-num'>{icon} {value}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)


def restaurant_card(row, favorites, on_select, on_favorite, dark_mode):
    rating_class = "rating dark-rating" if dark_mode else "rating"
    with st.container(border=True, height=440):
        st.markdown(f"<img class='restaurant-image' src='{escape(row.Image)}' alt='{escape(row.Restaurant)}'>", unsafe_allow_html=True)
        st.markdown(f"<div class='place-name'>{escape(row.Restaurant)}</div><div class='place-meta'>📍 {escape(row.Area)}, {escape(row.City)}</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='{rating_class}'>★ {row.Rating:.1f}</span>&nbsp;&nbsp;<b>{money(row.Cost)} for two</b>&nbsp;&nbsp;<span class='pill ai-pill'>✦ AI pick</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='pill'>{escape(row.Cuisine)}</span><span class='pill'>{escape(row.Best_For)}</span><span class='pill'>{'🚚 Delivery' if row.Delivery == 'Yes' else 'Dine-in'}</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='why'>Why it fits: {escape(row.Why)}</div>", unsafe_allow_html=True)
        a, b = st.columns([1.28, .92])
        a.button("Explore", key=f"go-{row.ID}", on_click=on_select, args=(row.Restaurant,), use_container_width=True, type="primary")
        label = "♥ Saved" if row.Restaurant in favorites else "♡ Save"
        b.button(label, key=f"save-{row.ID}", on_click=on_favorite, args=(row.Restaurant,), use_container_width=True)


def footer():
    st.markdown("<div class='footer'><b>TasteTrail</b> · Your AI dining companion for Chandigarh, Mohali & Panchkula &nbsp; | &nbsp; Made for better plans, one table at a time.</div>", unsafe_allow_html=True)
