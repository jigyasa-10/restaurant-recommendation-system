"""Dark-mode-safe, consumer product styling."""
import streamlit as st


def apply_styles(mode: str) -> None:
    palettes = {
        "Light": {"bg": "#fffaf6", "surface": "#ffffff", "surface2": "#fff4ea", "text": "#1d2922", "muted": "#667169", "line": "#ede4db", "accent": "#ef6c3b", "accent2": "#155a43"},
        "Dark": {"bg": "#101714", "surface": "#17211c", "surface2": "#203128", "text": "#f4f6f3", "muted": "#b7c2ba", "line": "#304239", "accent": "#ff945f", "accent2": "#7bd0a8"},
    }
    p = palettes["Dark" if mode == "Dark" else "Light"]
    st.markdown(f"""
    <style>
      :root {{ color-scheme: {"dark" if mode == "Dark" else "light"}; }}
      .stApp {{ background: {p['bg']}; color: {p['text']}; }}
      .block-container {{ max-width: 1440px; padding: 1.25rem 2rem 3.5rem; }}
      #MainMenu, footer, header[data-testid="stHeader"] {{visibility: hidden;}}
      [data-testid="stSidebar"] {{ background: {p['surface']}; border-right: 1px solid {p['line']}; }}
      [data-testid="stSidebar"] > div:first-child {{ padding-top: 1rem; }}
      h1, h2, h3, p, span, label, div {{ color: inherit; }}
      .brand {{ font-weight:800; font-size:1.52rem; letter-spacing:-.06em; color:{p['text']}; }}
      .brand-dot {{ color:{p['accent']}; }} .muted {{ color:{p['muted']}; }}
      .topbar {{ display:flex; align-items:center; justify-content:space-between; padding:.25rem 0 1rem; border-bottom:1px solid {p['line']}; margin-bottom:1.25rem; }}
      .topbar-location {{ color:{p['muted']}; font-weight:600; font-size:.9rem; }}
      .topbar-user {{ font-weight:750; color:{p['text']}; }}
      .nav-note {{ color:{p['muted']}; font-size:.78rem; letter-spacing:.08em; font-weight:700; text-transform:uppercase; }}
      .hero {{ background:linear-gradient(115deg,#173e2d 0%,#216149 51%,#d96435 130%); border-radius:28px; padding:3rem 3.2rem; color:#fff; overflow:hidden; position:relative; }}
      .hero:after {{ content:'✦'; position:absolute; right:6%; top:-38px; color:#ffbd79; opacity:.55; font-size:13rem; }}
      .hero h1 {{ color:#fff; font-size:clamp(2.25rem,4vw,4.2rem); max-width:740px; line-height:1.02; letter-spacing:-.055em; margin:.3rem 0 .85rem; }}
      .hero p {{ color:#e8f2ec; font-size:1.08rem; max-width:610px; }}
      .kicker {{ color:{p['accent']}; font-size:.73rem; font-weight:800; letter-spacing:.11em; text-transform:uppercase; }}
      .hero .kicker {{ color:#ffd4ab; }}
      .metric-card {{ background:{p['surface']}; border:1px solid {p['line']}; border-radius:18px; padding:1rem 1.1rem; height:100%; box-sizing:border-box; }}
      .metric-num {{ font-size:1.55rem; font-weight:800; letter-spacing:-.04em; color:{p['text']}; }}
      .metric-label {{ color:{p['muted']}; font-size:.84rem; margin-top:.16rem; }}
      .restaurant-image {{ height:184px; width:100%; object-fit:cover; border-radius:12px; display:block; }}
      .place-name {{ font-size:1.13rem; font-weight:800; letter-spacing:-.025em; margin-top:.66rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
      .place-meta {{ color:{p['muted']}; font-size:.84rem; margin:.15rem 0 .56rem; }}
      .rating {{ background:#e4f6e9; color:#17633c; border-radius:8px; padding:.26rem .45rem; font-size:.79rem; font-weight:800; }}
      .dark-rating {{ background:#224c35; color:#b8f5c9; }}
      .pill {{ display:inline-block; background:{p['surface2']}; color:{p['accent']}; border-radius:99px; padding:.26rem .55rem; font-size:.72rem; font-weight:700; margin:.2rem .18rem .2rem 0; }}
      .ai-pill {{ background:{p['accent2']}; color:#fff; }}
      .why {{ color:{p['muted']}; font-size:.75rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; margin:.35rem 0; }}
      [data-testid="stVerticalBlockBorderWrapper"] {{ background:{p['surface']}; border-color:{p['line']}; border-radius:17px; transition: transform .18s ease, box-shadow .18s ease; }}
      [data-testid="stVerticalBlockBorderWrapper"]:hover {{ transform:translateY(-4px); box-shadow:0 14px 28px rgba(20,35,27,.14); }}
      .detail-banner {{ background:{p['surface2']}; border-radius:18px; padding:1.1rem 1.3rem; color:{p['text']}; }}
      .detail-image {{ height:370px; width:100%; object-fit:cover; border-radius:20px; }}
      .review {{ background:{p['surface']}; border:1px solid {p['line']}; padding:.9rem 1rem; border-radius:14px; margin-bottom:.7rem; }}
      .footer {{ border-top:1px solid {p['line']}; margin-top:3rem; padding:1.8rem 0; color:{p['muted']}; font-size:.86rem; }}
      .stButton button, .stLinkButton a {{ border-radius:10px !important; font-weight:700 !important; border-color:{p['line']} !important; min-height:2.45rem; }}
      .stButton button[kind="primary"] {{ background:{p['accent']} !important; color:white !important; border-color:{p['accent']} !important; }}
      [data-baseweb="input"] > div, [data-baseweb="select"] > div {{ background:{p['surface']} !important; border-color:{p['line']} !important; color:{p['text']} !important; }}
      .stApp label, .stApp [data-testid="stWidgetLabel"], .stApp [data-testid="stWidgetLabel"] *, .stApp [data-baseweb="radio"] label, .stApp [data-baseweb="radio"] label *, .stApp [data-baseweb="select"] *, .stApp [data-baseweb="input"] input, .stApp [data-baseweb="input"] input::placeholder {{ color:{p['text']} !important; }}
      .stApp [data-baseweb="popover"], .stApp [data-baseweb="popover"] > div, .stApp [data-baseweb="menu"] {{ background:{p['surface']} !important; color:{p['text']} !important; border-color:{p['line']} !important; }}
      .stApp [data-baseweb="popover"] .stButton button {{ background:{p['surface']} !important; color:{p['text']} !important; }}
      .stApp [data-baseweb="select"] svg, .stApp [data-baseweb="input"] svg {{ fill:{p['text']} !important; }}
      .stApp [data-testid="stWidgetLabel"] div, .stApp [data-testid="stWidgetLabel"] p, .stApp [data-testid="stWidgetLabel"] span,
      .stApp [data-baseweb="radio"] div, .stApp [data-baseweb="radio"] span, .stApp [data-baseweb="radio"] p,
      .stApp [data-testid="stSlider"] div, .stApp [data-testid="stSlider"] p, .stApp [data-testid="stSlider"] span,
      .stApp [data-testid="stSidebar"] [data-testid="stWidgetLabel"] *, .stApp [data-testid="stSidebar"] [data-testid="stSlider"] * {{ color:{p['text']} !important; }}
      .stApp [data-testid="stPopover"] button, .stApp [data-baseweb="popover"] button {{ color:{p['text']} !important; }}
      @media(max-width:700px) {{ .block-container {{padding: .9rem 1rem 2rem;}} .hero {{ padding:2rem 1.45rem; border-radius:20px; }} .detail-image {{height:260px;}} }}
    </style>
    """, unsafe_allow_html=True)
