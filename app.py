import streamlit as st
import time
# ================================================================
# RULE 1: set_page_config() must be FIRST — never called twice.
# ================================================================
st.set_page_config(
    page_title="Prime TechHub",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# RULE 2: All DB logic lives in database.py — never duplicated here.
# ================================================================
from database import (
    init_db,
    verify_admin,
    register_customer,
    verify_customer,
    get_products,
    get_customer_orders,
    process_checkout,
    update_customer_password
)

import sqlite3
import pandas as pd
import time
import random
from streamlit_option_menu import option_menu

_CATEGORY_META = {
    "Camera":         ("bi-camera-video-fill", "linear-gradient(135deg,#203a43,#1a8fa8)"),
    "Lighting":       ("bi-lightbulb-fill", "linear-gradient(135deg,#1a8fa8,#5bc0de)"),
    "Smart Plug":     ("bi-plug-fill", "linear-gradient(135deg,#1a8fa8,#28a745)"),
    "Hub/Controller": ("bi-cpu-fill", "linear-gradient(135deg,#6f42c1,#1a8fa8)"),
    "Sensors":        ("bi-activity", "linear-gradient(135deg,#ff7e5f,#feb47b)"),
    "Networking":     ("bi-wifi", "linear-gradient(135deg,#00c6ff,#0072ff)"),
    "Audio":          ("bi-speaker-fill", "linear-gradient(135deg,#7f00ff,#e100ff)"),
    "Security":       ("bi-shield-fill", "linear-gradient(135deg,#dc3545,#fd7e14)"),
    "Climate":        ("bi-thermometer-half", "linear-gradient(135deg, #2980b9, #2c3e50)"),
}

# ================================================================
# CATEGORY IMAGE URLS — Unsplash photos mapped per category.
# Used in render_product_detail() for the full-page detail view.
# Gradient icon fallback activates automatically if image fails.
# ================================================================
_CATEGORY_UNSPLASH = {
    "Camera":
        "https://plus.unsplash.com/premium_photo-1729574957020-69b6ae3652d9?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0",
     "Lighting":
        "https://images.unsplash.com/photo-1738045419183-79fd0707ffe5?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0",
     "Smart Plug":
        "https://images.unsplash.com/photo-1733985741997-35bd14981faf?fm=jpg&q=60&w=700&auto=format&fit=crop&ixlib=rb-4.1.0",
    "Hub/Controller":
        "https://images.unsplash.com/photo-1752262167753-37a0ec83f614?fm=jpg&q=60&w=700&auto=format&fit=crop&ixlib=rb-4.1.0",
    "Sensors":
        "https://images.unsplash.com/photo-1636569608385-58efc32690ea?fm=jpg&q=60&w=700&auto=format&fit=crop&ixlib=rb-4.1.0",
    "Networking":
        "https://images.unsplash.com/photo-1750712263185-edde9f359e33?fm=jpg&q=60&w=700&auto=format&fit=crop&ixlib=rb-4.1.0",
    "Audio":
        "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=700&auto=format&fit=crop&q=80",
    "Security":
        "https://images.unsplash.com/photo-1558002038-1055907df827?w=700&auto=format&fit=crop&q=80",
    "Climate":
        "https://images.unsplash.com/photo-1545259741-2ea3ebf61fa3?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0,"
}

# ================================================================
# GLOBAL CSS — injected once at the top, never inside page blocks.
# ================================================================
def inject_global_css():
    st.markdown("""
    <link rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        :root {
            --teal-dark:    #0f2027;
            --teal-mid:     #203a43;
            --teal-base:    #2c5364;
            --teal-accent:  #1a8fa8;
            --teal-light:   #e8f5f8;
            --text-primary: #111111;
            --text-muted:   #5f6368;
            --border-light: #e8e8e8;
        }

        footer, #MainMenu { visibility: hidden; }
        header[data-testid="stHeader"]  { background: transparent !important; }
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 100% !important;
            margin-left: 0 !important;
        }
        div[data-testid="stButton"] > button p {
            white-space: nowrap !important;
        }
        div[data-testid="InputInstructions"] { display: none !important; }
        hr { border-color: var(--border-light) !important; opacity: 1; }
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] input { cursor: pointer !important; }

        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            box-shadow: 4px 0 28px rgba(0, 0, 0, 0.09) !important;
            border-right: 1px solid #f2f2f2 !important;
        }

        div[data-testid="stFormSubmitButton"] > button,
        div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(135deg, var(--teal-mid), var(--teal-accent)) !important;
            border: none !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            letter-spacing: 0.3px;
            transition: opacity 0.2s ease, transform 0.15s ease !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover,
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            opacity: 0.88 !important;
            transform: translateY(-1px) !important;
        }
        div[data-testid="stButton"] > button:not([kind="primary"]) {
            border-radius: 8px !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            color: var(--text-muted) !important;
        }

        [data-testid="stRadio"] [role="radio"] { display: none; }
        [data-testid="stRadio"] label {
            background-color: #f8f9fa;
            padding: 8px 18px !important;
            border-radius: 25px;
            border: 1px solid var(--border-light);
            transition: all 0.2s ease;
            cursor: pointer;
        }
        [data-testid="stRadio"] label:hover { border-color: var(--teal-accent); }
        [data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(135deg, var(--teal-mid), var(--teal-accent)) !important;
            border-color: var(--teal-accent) !important;
        }
        [data-testid="stRadio"] label:has(input:checked) p {
            color: #ffffff !important;
            font-weight: 600;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            transition: box-shadow 0.25s ease, transform 0.2s ease;
            border-radius: 14px !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: 0 8px 32px rgba(26,143,168,0.14) !important;
            transform: translateY(-3px) !important;
        }

        div[data-testid="stMetricValue"] {
            color: #111111 !important;
            font-weight: 800 !important;
        }

        .showcase-scroll {
            display: flex;
            overflow-x: auto;
            gap: 16px;
            padding: 8px 2px 20px 2px;
            scroll-snap-type: x mandatory;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: thin;
            scrollbar-color: #c8d8dc transparent;
        }
        .showcase-scroll::-webkit-scrollbar { height: 4px; }
        .showcase-scroll::-webkit-scrollbar-thumb { background: #c8d8dc; border-radius: 10px; }
        .showcase-card {
            min-width: 250px; max-width: 250px; background: #ffffff;
            border: 1px solid var(--border-light); border-radius: 16px;
            padding: 0 0 18px 0; scroll-snap-align: start;
            box-shadow: 0 2px 12px rgba(0,0,0,0.05);
            transition: box-shadow 0.25s ease, transform 0.2s ease; overflow: hidden;
        }
        .showcase-card:hover { box-shadow: 0 8px 28px rgba(26,143,168,0.14); transform: translateY(-4px); }
        .showcase-card-img { height: 120px; display: flex; align-items: center; justify-content: center; margin-bottom: 14px; }
        .showcase-card-body { padding: 0 16px; }
        .s-cat { font-size: 10.5px; color: var(--teal-accent); font-weight: 700; text-transform: uppercase; letter-spacing: 1.4px; margin-bottom: 5px; }
        .s-name { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; line-height: 1.3; }
        .s-desc { font-size: 12.5px; color: var(--text-muted); margin-bottom: 12px; line-height: 1.5; }
        .s-price { font-size: 17px; font-weight: 700; color: var(--teal-accent); }

        .samsung-watermark {
            position: fixed; bottom: 18px; right: 26px;
            color: #c5d8dc; font-size: 17px; font-weight: 700;
            letter-spacing: 0.5px; z-index: 50; pointer-events: none; user-select: none;
        }

        button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #203a43, #1a8fa8) !important;
            border: none !important; color: #ffffff !important;
            font-weight: 600 !important; border-radius: 8px !important;
        }
        button[data-testid="baseButton-primary"]:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

        div[data-testid="stTextInput"] input {
            border: none !important; border-radius: 6px !important;
            box-shadow: none !important; background: transparent !important;
            padding: 6px 12px !important; cursor: text !important;
            pointer-events: all !important; font-size: 14px !important;
        }
        div[data-testid="stTextInput"] > div[data-baseweb="input"] {
            border: 1.5px solid #e0e0e0 !important; border-radius: 8px !important;
            background: #ffffff !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
            pointer-events: all !important;
        }
        div[data-testid="stTextInput"] > div[data-baseweb="input"]:focus-within {
            border-color: #1a8fa8 !important; box-shadow: 0 0 0 3px rgba(26,143,168,0.10) !important;
        }
        div[data-testid="stTextInput"] > div[data-baseweb="input"]:hover { border-color: #1a8fa8 !important; }

        div[data-testid="stTextInput"],
        div[data-testid="stTextInput"] > div,
        div[data-testid="stTextInput"] > div > div,
        div[data-testid="stTextInput"] > div[data-baseweb="input"] {
            cursor: text !important; pointer-events: all !important;
            position: relative !important; z-index: 5 !important;
        }

        button[data-testid="baseButton-primary"],
        button[kind="primary"],
        .stButton button[data-testid^="baseButton"] {
            background: linear-gradient(135deg, #203a43, #1a8fa8) !important;
            border: none !important; color: #ffffff !important;
            font-weight: 600 !important; border-radius: 8px !important;
            transition: opacity 0.2s ease !important;
        }
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #203a43, #1a8fa8) !important;
            border: none !important; color: #ffffff !important;
            font-weight: 600 !important; border-radius: 8px !important; width: 100% !important;
        }

        .faq-contact-box {
            margin-top: 24px; text-align: center; padding: 20px;
            background: #e8f5f8 !important; border-radius: 12px; border: 1px solid #c0dde4;
        }

        div[data-testid="stForm"] div[data-baseweb="input"] {
            background-color: #f1f5f9 !important; border: 1.5px solid #e2e8f0 !important;
            border-radius: 8px !important; box-shadow: none !important;
        }
        div[data-testid="stForm"] div[data-baseweb="input"] input {
            background-color: transparent !important; border: none !important;
            box-shadow: none !important; padding: 8px 14px !important;
        }
        div[data-testid="stForm"] div[data-baseweb="input"] div {
            background-color: transparent !important; border: none !important;
        }
        div[data-testid="stForm"] div[data-baseweb="input"]:focus-within {
            background-color: #ffffff !important;
            box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.18) !important;
        }

        /* ── Cart button: full surface, no z-index bleed from selectbox ── */
        div[data-testid="stColumns"] div[data-testid="stButton"] {
            position: relative !important; z-index: 30 !important;
        }
        div[data-testid="stColumns"] div[data-testid="stButton"] button {
            pointer-events: all !important; cursor: pointer !important;
            width: 100% !important; position: relative !important; z-index: 30 !important;
        }
        div[data-baseweb="select"] { position: relative !important; z-index: 15 !important; }
        div[data-baseweb="popover"] { z-index: 16 !important; }

        /* ── Cart receipt styling ── */
        .receipt-row {
            display: flex; justify-content: space-between;
            padding: 6px 0; font-size: 13.5px; border-bottom: 1px solid #f5f5f5;
        }
        .receipt-row .r-label { color: #666; }
        .receipt-row .r-value { font-weight: 600; color: #111; }
        .receipt-total {
            display: flex; justify-content: space-between;
            padding: 10px 0 4px 0; font-size: 17px; font-weight: 800;
        }
        .receipt-total .r-label { color: #111; }
        .receipt-total .r-value { color: #1a8fa8; }

        /* Vertical gap fix: input in sidebar form */
        div[data-testid="stForm"] div[data-testid="stTextInput"] { margin-bottom: -10px !important; }
        div[data-testid="stForm"] div[data-testid="stTextInput"]:last-of-type { margin-bottom: 0 !important; 
        }
        /* Remove the default browser password eye icon */
        input[type="password"]::-ms-reveal,
        input[type="password"]::-ms-clear {
        display: none !important;
        }

        input[type="password"]::-webkit-contacts-auto-fill-button,
        input[type="password"]::-webkit-credentials-auto-fill-button {
        display: none !important;
        }
        /* ── Category pills: breathing room above + below, no early wrap ── */
        div[data-testid="stRadio"] {
            margin-top: 10px !important;
            margin-bottom: 6px !important;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            width: 100% !important;
            gap: 10px !important;
            padding-bottom: 10px !important;
            padding-top: 4px !important;
            scrollbar-width: thin !important;
            scrollbar-color: #c8d8dc transparent !important;
        }
        div[data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar { height: 4px !important; }
        div[data-testid="stRadio"] > div[role="radiogroup"]::-webkit-scrollbar-thumb {
            background: #c8d8dc !important; border-radius: 10px !important;
        }
        div[data-testid="stRadio"] label {
            margin-bottom: 0 !important;
            line-height: 1 !important;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
        }
        /* Pull selectbox up exactly the invisible label height Streamlit reserves */
        div[data-testid="stColumn"]:nth-child(2) div[data-testid="stSelectbox"] {
            margin-top: -12px !important;
        }
        div[data-testid="stColumn"]:nth-child(3) div[data-testid="stButton"] {
            margin-top: 8px !important;
        }
        /* Cart button: tiny top nudge down to meet midline */
        div[data-testid="stColumn"]:nth-child(3) div[data-testid="stButton"] {
            margin-top: 4px !important;
        }
    </style>
    """, unsafe_allow_html=True)


# ================================================================
# SESSION STATE — cart is a dict: {str(product_id): {qty, name, price, category}}
# page_override allows cart button to route without sidebar nav
# ================================================================
def init_session_state():
    defaults = {
        "cart":                {},      # DICT — key=str(id), value={qty,name,price,category}
        "customer_logged_in":  False,
        "admin_logged_in":     False,
        "current_customer":    None,
        "account_mode":        "login",
        "show_login_message":  False,
        "page_override":       None,    # set by cart header button
        "_last_sidebar_page":  "Home",  # detect sidebar nav changes
        "selected_product":    None,    # int product ID when viewing detail, else None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ================================================================
# SIDEBAR NAVIGATION
# ================================================================
def render_sidebar():
    menu_options = ["Home", "Account", "Settings", "FAQ", "About Us"]
    menu_icons   = ["house-fill", "person-fill",
                    "gear-fill", "question-circle-fill", "info-square-fill"]

    if st.session_state.get("admin_logged_in"):
        menu_options.append("Admin")
        menu_icons.append("terminal-fill")

    with st.sidebar:
        st.markdown("""
        <div style='padding: 18px 16px 10px 16px;'>
            <span style='font-weight:800; font-size:19px; letter-spacing:-0.5px; color:#111;'>
                Main Menu
            </span><br>
        </div>
        <hr style='margin: 0 0 6px 0; border-color:#f0f0f0;'>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='padding: 4px 16px 8px 16px;'>
            <span style='font-size: 10px; font-weight: 700; color: #bbb;
                         text-transform: uppercase; letter-spacing: 1.8px;'>
                Prime TechHub
            </span>
        </div>
        """, unsafe_allow_html=True)

        page = option_menu(
            menu_title=None,
            options=menu_options,
            icons=menu_icons,
            default_index=0,
            styles={
                "container":         {"padding": "0!important", "background-color": "transparent"},
                "icon":              {"font-size": "15px", "color": "#203a43"},
                "nav-link": {
                    "font-size":     "14px", "text-align": "left",
                    "margin":        "2px 0", "color": "#333", "font-weight": "500",
                    "--hover-color": "#f0f5f6", "border-radius": "8px", "padding": "9px 14px",
                },
                "nav-link-selected": {"background-color": "#e8f5f8", "color": "#1a8fa8", "font-weight": "700"},
            }
        )

        # Cart badge — total quantity across all items
        cart      = st.session_state.get("cart", {})
        cart_qty  = sum(v["qty"] for v in cart.values()) if cart else 0
        if cart_qty > 0:
            st.markdown(f"""
            <div style='margin: 8px 12px 0 12px; padding: 9px 14px;
                        background: linear-gradient(135deg, #203a43, #1a8fa8);
                        border-radius: 10px; display:flex; align-items:center; gap:10px;'>
                <i class="bi bi-cart3" style="color:white; font-size:16px;"></i>
                <span style="color:white; font-weight:600; font-size:13px;">
                    {cart_qty} item{'s' if cart_qty != 1 else ''} in cart
                </span>
            </div>
            """, unsafe_allow_html=True)

    return page


# ================================================================
# SHOWCASE HTML
# ================================================================
def _build_showcase_html(products_df):
    featured = products_df.drop_duplicates(subset=["category"]).head(8)
    cards = ""
    for _, row in featured.iterrows():
        icon, gradient = _CATEGORY_META.get(
            row["category"], ("bi-box-fill", "linear-gradient(135deg,#1a2a3a,#2c5364)")
        )
        desc_raw = str(row.get("description", ""))
        desc = desc_raw[:55] + "…" if len(desc_raw) > 55 else desc_raw

        cards += f"""
        <div class="showcase-card">
            <div class="showcase-card-img" style="background:{gradient};">
                <i class="bi {icon}" style="font-size:42px;color:rgba(255,255,255,0.88);"></i>
            </div>
            <div class="showcase-card-body">
                <div class="s-cat">{row["category"]}</div>
                <div class="s-name">{row["name"]}</div>
                <div class="s-desc">{desc}</div>
                <div class="s-price">PKR {row["price"]:,.0f}</div>
            </div>
        </div>"""

    return f"""
    <div style="margin:0 0 8px 0;">
        <span style="font-size:10.5px;font-weight:700;color:#1a8fa8;
                     text-transform:uppercase;letter-spacing:1.6px;">
            <i class="bi bi-stars"></i>&nbsp; Featured Devices
        </span>
    </div>
    <div class="showcase-scroll" style="padding-bottom:8px;">{cards}</div>"""

# ================================================================
# render_product_detail(product_id)
# Standalone detail view. Called by page_home() when
# selected_product is set. Hides the grid completely.
# Image loads from _CATEGORY_UNSPLASH; gradient icon fallback
# fires automatically via HTML onerror if image fails (offline).
# ================================================================
def render_product_detail(product_id: int):
    products_df = get_products()
    if products_df.empty:
        st.session_state["selected_product"] = None
        return

    match = products_df[products_df["id"] == product_id]
    if match.empty:
        st.session_state["selected_product"] = None
        return

    row      = match.iloc[0]
    pid      = str(int(row["id"]))
    cat      = str(row.get("category", ""))
    stock    = int(row.get("stock", 0))
    icon, gradient = _CATEGORY_META.get(
        cat, ("bi-box-fill", "linear-gradient(135deg,#1a2a3a,#2c5364)")
    )
    img_url  = _CATEGORY_UNSPLASH.get(cat, "")

    # ── Back button — forced to front layer above sidebar overlay ──
    st.markdown("""
    <style>
        /* Scope: only the first button block in the main content area */
        section[data-testid="stMain"] div[data-testid="stButton"]:first-of-type,
        section[data-testid="stMain"] div[data-testid="stButton"]:first-of-type > button {
            position: relative !important;
            z-index: 999999 !important;
            pointer-events: all !important;
        }
        /* Also push the button container above the sidebar collapse control */
        button[data-testid="collapsedControl"] { z-index: 99 !important; }
    </style>
    """, unsafe_allow_html=True)
    if st.button("← Back to Shop", key="back_to_shop_btn"):
        st.session_state["selected_product"] = None
        st.rerun()

    st.markdown("<hr style='margin:0.5rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    col_img, col_info = st.columns([1, 1.15])

    # ── LEFT: product image + specs ───────────────────────────────
    with col_img:
        # Image with inline onerror fallback to gradient icon
        safe_gradient  = gradient.replace("'", "\\'")
        safe_icon      = icon
        fallback_style = (
            f"background:{safe_gradient};height:290px;display:flex;"
            f"align-items:center;justify-content:center;border-radius:16px;"
        )
        if img_url:
            st.markdown(f"""
            <div style='border-radius:18px; overflow:hidden;
                        box-shadow:0 8px 32px rgba(0,0,0,0.13); margin-bottom:16px;'>
                <img src="{img_url}"
                     style='width:100%; height:290px; object-fit:cover; display:block;'
                     onerror="this.parentElement.innerHTML='<div style=\\'background:{gradient};height:290px;display:flex;align-items:center;justify-content:center;\\'><i class=\\'bi {icon}\\' style=\\'font-size:80px;color:rgba(255,255,255,0.9);\\'></i></div>'">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='{fallback_style}box-shadow:0 8px 32px rgba(0,0,0,0.13);margin-bottom:16px;'>
                <i class="bi {icon}" style="font-size:80px;color:rgba(255,255,255,0.9);"></i>
            </div>
            """, unsafe_allow_html=True)

        # Specs panel
        st.markdown(f"""
        <div style='background:#f8f9fa;border-radius:12px;padding:14px 16px;'>
            <div style='font-size:10px;font-weight:700;color:#1a8fa8;
                        text-transform:uppercase;letter-spacing:1.4px;margin-bottom:10px;'>
                <i class="bi bi-list-check"></i>&nbsp; Key Specifications
            </div>
            <div style='font-size:13px;color:#444;line-height:2.2;'>
                <div><strong>Category:</strong>&nbsp; {cat}</div>
                <div><strong>Connectivity:</strong>&nbsp; Wi-Fi 2.4 / 5 GHz</div>
                <div><strong>Compatibility:</strong>&nbsp; Alexa · Google · Siri</div>
                <div><strong>Warranty:</strong>&nbsp; 1-Year Limited Hardware</div>
                <div><strong>Returns:</strong>&nbsp; 30-Day Money-Back</div>
            </div>]
        </div>
        """, unsafe_allow_html=True)

    # ── RIGHT: name, price, description, stock, qty, add to cart ─
    with col_info:
        st.markdown(f"""
        <div style='font-size:10.5px;font-weight:700;color:#1a8fa8;
                    text-transform:uppercase;letter-spacing:1.4px;margin-bottom:8px;'>
            <i class="bi {icon}"></i>&nbsp; {cat}
        </div>
        <h2 style='margin:0 0 4px 0;font-size:26px;font-weight:800;
                   color:#111;line-height:1.2;'>
            {row['name']}
        </h2>
        <div style='font-size:32px;font-weight:900;color:#1a8fa8;
                    margin:14px 0 6px 0;letter-spacing:-0.5px;'>
            PKR {row['price']:,.0f}
        </div>
        <p style='color:#555;font-size:14.5px;line-height:1.85;margin-bottom:18px;'>
            {row.get('description', '')}
        </p>
        """, unsafe_allow_html=True)

        # Stock status
        if stock == 0:
            st.error("❌ Currently out of stock — check back soon")
        elif stock <= 5:
            st.error(f"⚠️ Only {stock} left — order soon!")
        elif stock <= 20:
            st.warning(f"⏳ Low stock — {stock} units remaining")
        else:
            st.success(f"✅ In Stock — {stock} units available")

        if stock > 0:
            qty = st.number_input(
                "Quantity",
                min_value=1, max_value=min(stock, 20),
                value=1, step=1,
                key=f"dpd_qty_{pid}"
            )
            if st.button("🛒  Add to Cart", type="primary",
                         use_container_width=True, key=f"dpd_atc_{pid}"):
                cart = st.session_state["cart"]
                if pid in cart:
                    cart[pid]["qty"] += int(qty)
                else:
                    cart[pid] = {
                        "qty":      int(qty),
                        "name":     row["name"],
                        "price":    float(row["price"]),
                        "category": cat,
                    }
                st.toast(f"✅ {qty}× {row['name']} added to cart!")

        # Trust badges
        st.markdown("""
        <div style='margin-top:20px;padding:14px 16px;background:#f8f9fa;
                    border-radius:12px;font-size:13px;color:#555;line-height:2.3;'>
            <div><i class="bi bi-truck" style='color:#1a8fa8'></i>&nbsp;
                 <strong>Free delivery</strong> on orders over PKR 5,000</div>
            <div><i class="bi bi-arrow-counterclockwise" style='color:#1a8fa8'></i>&nbsp;
                 <strong>30-day returns</strong> — no questions asked</div>
            <div><i class="bi bi-shield-check" style='color:#1a8fa8'></i>&nbsp;
                 <strong>1-year hardware warranty</strong> included</div>
            <div><i class="bi bi-lock-fill" style='color:#1a8fa8'></i>&nbsp;
                 <strong>Secure checkout</strong> — SSL encrypted</div>
        </div>
        """, unsafe_allow_html=True)
        
# ── NEW: Featured section with real Streamlit click callbacks ──
def _render_featured_section(products_df):
    """
    Uses st.container(key=...) — Streamlit ≥1.32 renders this as a real
    DOM node with class `st-key-featured_scroll_box`, so CSS can reliably
    target the columns inside it (markdown-wrapping doesn't work).
    """
    featured = products_df.drop_duplicates(subset=["category"]).head(9)
    if featured.empty:
        return

    st.markdown("""
    <style>
       /* Featured scroll: natural overflow, card width drives scroll prompt */
        .st-key-featured_scroll_box div[data-testid="stHorizontalBlock"] {
            overflow-x: auto !important;
            overflow-y: hidden !important;
            flex-wrap: nowrap !important;
            width: 100% !important;
            padding-bottom: 16px !important;
            scrollbar-width: thin !important;
            scrollbar-color: #c8d8dc transparent !important;
            /* NO max-width — that caused white leak */
        }
        .st-key-featured_scroll_box div[data-testid="stHorizontalBlock"]::-webkit-scrollbar {
            height: 4px !important;
        }
        .st-key-featured_scroll_box div[data-testid="stHorizontalBlock"]::-webkit-scrollbar-thumb {
            background: #c8d8dc !important;
            border-radius: 10px !important;
        }
        /* Each card fixed at 260px — viewport ÷ card width = natural visible count */
        /* ~1000px content area ÷ 260px = ~3.8 cards → 4th card partially visible → scroll cue */
        .st-key-featured_scroll_box div[data-testid="stColumn"] {
            min-width: 260px !important;
            max-width: 260px !important;
            flex: 0 0 260px !important;
        }
    </style>
    <div style="margin:0 0 10px 0;">
        <span style="font-size:10.5px;font-weight:700;color:#1a8fa8;
                     text-transform:uppercase;letter-spacing:1.6px;">
            <i class="bi bi-stars"></i>&nbsp; Featured Devices
        </span>
    </div>
    """, unsafe_allow_html=True)

    with st.container(key="featured_scroll_box"):
        feat_cols = st.columns(len(featured))
        for fc, (_, row) in zip(feat_cols, featured.iterrows()):
            icon, gradient = _CATEGORY_META.get(
                row["category"], ("bi-box-fill", "linear-gradient(135deg,#1a2a3a,#2c5364)")
            )
            with fc:
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="background:{gradient};height:90px;border-radius:10px;
                                display:flex;align-items:center;justify-content:center;
                                margin-bottom:10px;">
                        <i class="bi {icon}" style="font-size:34px;
                           color:rgba(255,255,255,0.92);"></i>
                    </div>
                    <div style="font-size:9.5px;font-weight:700;color:#1a8fa8;
                                text-transform:uppercase;letter-spacing:1.2px;
                                margin-bottom:3px;">{row['category']}</div>
                    <div style="font-size:13px;font-weight:600;color:#111;
                                line-height:1.3;margin-bottom:3px;
                                white-space:nowrap;overflow:hidden;
                                text-overflow:ellipsis;">{row['name']}</div>
                    <div style="font-size:14px;font-weight:800;color:#1a8fa8;
                                margin-bottom:8px;">PKR {row['price']:,.0f}</div>
                    """, unsafe_allow_html=True)
                    if st.button("View →", key=f"feat_{row['id']}", use_container_width=True):
                        st.session_state["selected_product"] = int(row["id"])
                        st.rerun()

# ================================================================
# PAGE: HOME
# ================================================================
def page_home():
    # --- UI RENDER BUFFER ---
    # Gives the browser 150ms to wipe the old page before drawing the new grid
    time.sleep(0.20)
    # Cache products in session state for this render cycle only
    # (re-fetches once per sidebar navigation, not on every widget click)
    if "cached_products" not in st.session_state:
        st.session_state["cached_products"] = get_products()
    products_df = st.session_state["cached_products"]
    # ── Detail view gate: if a product is selected, show detail instead of grid ──
    if st.session_state.get("selected_product") is not None:
        products_df_all = get_products()
        if not products_df_all.empty:
            match = products_df_all[products_df_all["id"] == st.session_state["selected_product"]]
            if not match.empty:
                render_product_detail(int(match.iloc[0]["id"]))
                return
        st.session_state["selected_product"] = None   # product not found — reset

    # ── Existing header columns start here (unchanged) ──
    h1, h2, h3 = st.columns([1, 1.8, 0.9])

    with h1:
        st.markdown("""
        <div style='padding-top:5px;'>
            <span style='font-weight:900;font-size:24px;letter-spacing:-0.8px;color:#111;'>
                Prime TechHub</span><br>
            <span style='color:#999;font-size:11px;font-weight:500;'>Smart Home Devices</span>
        </div>""", unsafe_allow_html=True)

    with h2:
        st.markdown("""
        <style>
            div[data-testid="stTextInput"] label {
                height: 0 !important; overflow: hidden !important;
                margin: 0 !important; padding: 0 !important; pointer-events: none !important;
            }
            div[data-testid="stTextInput"],
            div[data-testid="stTextInput"] > div,
            div[data-testid="stTextInput"] > div[data-baseweb="input"],
            div[data-testid="stTextInput"] input {
                pointer-events: all !important; cursor: text !important;
                position: relative !important; z-index: 20 !important;
            }
            div[data-testid="stTextInput"] > div[data-baseweb="input"] {
                border: 1.5px solid #e0e0e0 !important; border-radius: 25px !important;
                background: #f8f9fa !important; box-shadow: none !important;
                transition: border-color 0.2s, box-shadow 0.2s !important;
            }
            div[data-testid="stTextInput"] > div[data-baseweb="input"]:focus-within,
            div[data-testid="stTextInput"] > div[data-baseweb="input"]:hover {
                border-color: #1a8fa8 !important; background: #ffffff !important;
                box-shadow: 0 0 0 3px rgba(26,143,168,0.10) !important;
            }
            div[data-testid="stTextInput"] input {
                border: none !important; background: transparent !important;
                box-shadow: none !important; font-size: 14px !important; padding: 8px 16px !important;
            }
        </style>
        """, unsafe_allow_html=True)

        products_df_for_search = get_products()
        all_names = products_df_for_search["name"].tolist() if not products_df_for_search.empty else []

        selected_product_name = st.selectbox(
            "Search products", options=all_names, index=None,
            placeholder="  Search smart devices 🔍…",
            label_visibility="collapsed", key="home_search"
        )

    with h3:
        # Cart total quantity
        cart     = st.session_state.get("cart", {})
        cart_qty = sum(v["qty"] for v in cart.values()) if cart else 0
        if st.button(f"🛒  {cart_qty}", type="primary", key="hdr_cart_btn"):
            st.session_state["page_override"] = "Cart"
            st.rerun()

    st.markdown("<hr style='margin:0.4rem 0 0.7rem 0;'>", unsafe_allow_html=True)

    # Hero Banner
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
                padding:22px 28px 20px 28px; border-radius:14px; text-align:center;
                color:white; margin-bottom:18px; box-shadow:0 6px 24px rgba(15,32,39,0.18);">
        <div style="font-size:9.5px;font-weight:700;letter-spacing:2.5px;
                    color:#7ecdd8;text-transform:uppercase;margin-bottom:8px;">
            <i class="bi bi-shield-check"></i>&nbsp; Trusted Smart Home Platform
        </div>
        <h1 style="margin:0;font-size:1.9em;font-weight:800;letter-spacing:-0.5px;">
            Smart Living, Simplified.
        </h1>
        <p style="margin:8px auto 0 auto;font-size:0.92em;color:#b8d4da;
                  max-width:460px;line-height:1.5;">
            Upgrade every corner of your home with Prime TechHub's curated smart device ecosystem.
        </p>
        <div style="margin-top:14px;display:flex;justify-content:center;gap:20px;flex-wrap:wrap;">
            <span style="font-size:11.5px;color:#7ecdd8;"><i class="bi bi-wifi"></i>&nbsp;Wi-Fi Ready</span>
            <span style="font-size:11.5px;color:#7ecdd8;"><i class="bi bi-shield-lock"></i>&nbsp;AES-256 Secure</span>
            <span style="font-size:11.5px;color:#7ecdd8;"><i class="bi bi-box-seam"></i>&nbsp;Same-Day Dispatch</span>
            <span style="font-size:11.5px;color:#7ecdd8;"><i class="bi bi-arrow-return-left"></i>&nbsp;30-Day Returns</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # products_df already loaded from session cache at top of function
    if not products_df.empty:
        _render_featured_section(products_df)
    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; align-items:center; margin:8px 0 14px 0; gap:12px;">
        <span style="font-size:11px; font-weight:700; color:#1a8fa8;
                     text-transform:uppercase; letter-spacing:1.6px; white-space:nowrap;">
            <i class="bi bi-grid-3x3-gap-fill"></i>&nbsp; All CATAGORIES
        </span>
        <hr style="flex:1; margin:0; border-color:#ececec;">
    </div>
    """, unsafe_allow_html=True)

    CATEGORIES = ["All", "Camera", "Lighting", "Smart Plug", "Hub/Controller", "Sensors", "Networking", "Audio", "Security", "Climate"]
    category_filter = st.radio("Category", CATEGORIES, horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    if products_df.empty:
        st.warning("Inventory is empty. Add products via the Admin tab.")
        return

    filtered_df = products_df.copy()
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]

    safe_search = st.session_state.get("home_search") or ""
    clean_query = safe_search.strip().lower().replace("-", "").replace(" ", "")
    if clean_query:
        filtered_df["_cn"] = (filtered_df["name"].str.lower()
                              .str.replace("-", "", regex=False)
                              .str.replace(" ", "", regex=False))
        filtered_df = filtered_df[filtered_df["_cn"].str.contains(clean_query, na=False)]

    filtered_df = filtered_df[filtered_df["stock"] > 0]

    if filtered_df.empty:
        st.info("No devices match your search or filter. Try a different category.")
        return

    st.caption(f"Showing **{len(filtered_df)}** device{'s' if len(filtered_df) != 1 else ''}")

    NUM_COLUMNS = 3
    cols = st.columns(NUM_COLUMNS)
    CAT_ICONS = {
        "Camera": "bi-camera-video-fill", "Lighting": "bi-lightbulb-fill",
        "Smart Plug": "bi-plug-fill", "Hub/Controller": "bi-cpu-fill",
        "Sensors": "bi-activity", "Networking": "bi-wifi", "Audio": "bi-speaker-fill",
        "Security": "bi-shield-fill","Climate": "bi-thermometer-half",
    }

    for i, (_, row) in enumerate(filtered_df.iterrows()):
        col       = cols[i % NUM_COLUMNS]
        cat_icon  = CAT_ICONS.get(row["category"], "bi-box-fill")
        pid       = str(row["id"])

        with col:
            with st.container(border=True):
                # ── Thumbnail: Unsplash image with gradient fallback ──
                _thumb_url  = _CATEGORY_UNSPLASH.get(row.get("category", ""), "")
                _, _grad    = _CATEGORY_META.get(
                    row.get("category", ""),
                    ("bi-box-fill", "linear-gradient(135deg,#1a2a3a,#2c5364)")
                )
                if _thumb_url:
                    st.markdown(f"""
                    <div style='border-radius:10px;overflow:hidden;
                                height:110px;margin-bottom:8px;'>
                        <img src="{_thumb_url}"
                             style='width:100%;height:110px;
                                    object-fit:cover;display:block;'
                             onerror="this.parentElement.innerHTML='<div style=\\'background:{_grad};height:110px;border-radius:10px;display:flex;align-items:center;justify-content:center;\\'><i class=\\'bi {cat_icon}\\' style=\\'font-size:32px;color:rgba(255,255,255,0.9);\\'></i></div>';">
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background:{_grad};border-radius:10px;height:110px;
                                display:flex;align-items:center;justify-content:center;
                                margin-bottom:8px;'>
                        <i class="bi {cat_icon}" style="font-size:32px;
                           color:rgba(255,255,255,0.9);"></i>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="font-size:11px; font-weight:700; color:#1a8fa8;
                            text-transform:uppercase; letter-spacing:1.2px; margin-bottom:6px;">
                    <i class="bi {cat_icon}"></i>&nbsp; {row['category']}
                </div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <div style="font-size:17px; font-weight:600; color:#111;
                            margin-bottom:5px; line-height:1.3;">{row['name']}</div>
                """, unsafe_allow_html=True)

                if row.get("description"):
                    st.caption(row["description"])

                st.markdown(f"""
                <div style="font-size:18px; font-weight:800; color:#1a8fa8; margin:10px 0 8px 0;">
                    PKR {row['price']:,.0f}
                </div>""", unsafe_allow_html=True)

                if row["stock"] <= 5:
                    st.markdown(f'<div style="font-size:12px;color:#c0392b;font-weight:600;margin-bottom:8px;"><i class="bi bi-exclamation-triangle-fill"></i>&nbsp;Only {row["stock"]} left</div>', unsafe_allow_html=True)
                elif row["stock"] <= 20:
                    st.markdown(f'<div style="font-size:12px;color:#e67e22;font-weight:600;margin-bottom:8px;"><i class="bi bi-dash-circle-fill"></i>&nbsp;Low Stock — {row["stock"]} remaining</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="font-size:12px;color:#27ae60;font-weight:600;margin-bottom:8px;"><i class="bi bi-check-circle-fill"></i>&nbsp;In Stock ({row["stock"]} units)</div>', unsafe_allow_html=True)

                # ── View Details + Add to Cart ──────────────────────
                btn_left, btn_right = st.columns(2)
                with btn_left:
                    if st.button("View Details", key=f"det_{row['id']}", use_container_width=True):
                        st.session_state["selected_product"] = int(row["id"])
                        st.rerun()
                with btn_right:
                    if st.button("Add to Cart", type="primary", key=f"add_{row['id']}", use_container_width=True):
                        cart = st.session_state["cart"]
                        if pid in cart:
                            cart[pid]["qty"] += 1
                        else:
                            cart[pid] = {
                                "qty":      1,
                                "name":     row["name"],
                                "price":    float(row["price"]),
                                "category": row.get("category", ""),
                            }
                        st.toast(f"✅ {row['name']} added to cart!")

# ================================================================
# PAGE: CART & CHECKOUT
# - Cart viewable by all (no login wall at top)
# - Login required only at checkout step
# - Cart stored as dict: {str(id): {qty, name, price, category}}
# - Receipt shows Subtotal + GST (17%) + Platform Fee + Total
# ================================================================
def page_cart():

    # ── CASE A: Show receipt after successful checkout ────────────
    if "receipt" in st.session_state:
        r = st.session_state["receipt"]
        st.markdown("""
        <div style='background:linear-gradient(135deg,#0f2027,#203a43);
                    padding:22px 28px; border-radius:14px; color:white; margin-bottom:22px;'>
            <div style='font-size:10px;font-weight:700;color:#7ecdd8;
                        text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;'>
                <i class="bi bi-check-circle-fill"></i>&nbsp; Order Confirmed
            </div>
            <h3 style='margin:0;font-size:22px;font-weight:800;'>Payment Successful 🎉</h3>
            <p style='margin:6px 0 0 0;font-size:13px;color:#b8d4da;'>
                Thank you for shopping with Prime TechHub.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(f"### Digital Receipt — `{r['order_id']}`")
            c1, c2 = st.columns(2)
            c1.markdown(f"**Customer:** {r['name']}")
            c1.markdown(f"**Address:** {r['address']}")
            c2.markdown(f"**Payment:** {r['method']}")
            c2.markdown(f"**Items ordered:** {r['items_count']}")
            st.divider()
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("Subtotal",     f"PKR {r['subtotal']:,.0f}")
            rc2.metric("GST (17%)",    f"PKR {r['tax']:,.0f}")
            rc3.metric("Total Paid",   f"PKR {r['total']:,.0f}")

        st.write("")
        if st.button("✅ Continue Shopping", type="primary", use_container_width=True):
            del st.session_state["receipt"]
            st.session_state["page_override"] = "Home"
            st.rerun()
        return

    # ── Page header ───────────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0f2027,#203a43);
                padding:20px 26px; border-radius:14px; color:white; margin-bottom:20px;'>
        <div style='font-size:10px;font-weight:700;color:#7ecdd8;
                    text-transform:uppercase;letter-spacing:2px;margin-bottom:6px;'>
            <i class="bi bi-cart3-fill"></i>&nbsp; Shopping Cart
        </div>
        <h3 style='margin:0;font-size:20px;font-weight:800;'>Review Your Order</h3>
    </div>
    """, unsafe_allow_html=True)

    cart = st.session_state.get("cart", {})

    # ── CASE B: Empty cart ────────────────────────────────────────
    if not cart:
        st.markdown("""
        <div style='text-align:center;padding:50px 20px;'>
            <i class="bi bi-cart-x" style="font-size:52px;color:#ccc;"></i>
            <h4 style='color:#999;margin:16px 0 6px 0;'>Your cart is empty</h4>
            <p style='color:#bbb;font-size:13px;'>
                Browse the Home page to shop smart devices.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Devices", type="primary", use_container_width=False):
            st.session_state["page_override"] = "Home"
            st.rerun()
        return

    # ── Two-column layout: items | receipt+checkout ───────────────
    col_items, col_receipt = st.columns([1.4, 1])

    subtotal       = 0.0
    pids_to_remove = []

    # ── LEFT: Cart Items ──────────────────────────────────────────
    with col_items:
        st.markdown("#### Cart Items")

        for pid, info in list(cart.items()):
            qty        = info["qty"]
            price      = info["price"]
            line_total = price * qty
            subtotal  += line_total

            with st.container(border=True):
                top_col, price_col = st.columns([2.5, 1])

                with top_col:
                    st.markdown(f"""
                    <div style='font-size:15px;font-weight:600;color:#111;margin-bottom:2px;'>
                        {info['name']}
                    </div>
                    <div style='font-size:11px;color:#1a8fa8;font-weight:600;
                                text-transform:uppercase;letter-spacing:1px;'>
                        {info.get('category','')}
                    </div>""", unsafe_allow_html=True)

                with price_col:
                    st.markdown(f"""
                    <div style='text-align:right;font-size:15px;font-weight:700;
                                color:#1a8fa8;padding-top:4px;'>
                        PKR {line_total:,.0f}
                    </div>
                    """, unsafe_allow_html=True)

                # Quantity controls + Remove
                btn_minus, qty_display, btn_plus, btn_remove = st.columns([0.6, 0.8, 0.6, 1])

                with btn_minus:
                    if st.button("−", key=f"minus_{pid}", use_container_width=True):
                        if cart[pid]["qty"] > 1:
                            cart[pid]["qty"] -= 1
                        else:
                            pids_to_remove.append(pid)
                        st.rerun()

                with qty_display:
                    st.markdown(f"""
                    <div style='text-align:center;font-size:15px;font-weight:700;
                                padding-top:6px;color:#111;'>{qty}</div>
                    """, unsafe_allow_html=True)

                with btn_plus:
                    if st.button("+", key=f"plus_{pid}", use_container_width=True):
                        cart[pid]["qty"] += 1
                        st.rerun()

                with btn_remove:
                    if st.button("Remove", key=f"rm_{pid}", use_container_width=True):
                        pids_to_remove.append(pid)
                        st.rerun()

        # Apply removals
        for pid in pids_to_remove:
            st.session_state["cart"].pop(pid, None)

        st.divider()
        if st.button("🗑️ Clear Entire Cart", use_container_width=True):
            st.session_state["cart"] = {}
            st.rerun()

    # ── RIGHT: Receipt breakdown + Checkout ──────────────────────
    with col_receipt:
        st.markdown("#### Order Receipt")

        TAX_RATE     = 0.17   # Pakistan GST
        PLATFORM_FEE = 99.0   # Flat platform fee
        tax          = subtotal * TAX_RATE
        total        = subtotal + tax + PLATFORM_FEE

        with st.container(border=True):
            # Line items
            for pid, info in cart.items():
                rc, rp = st.columns([2, 1])
                rc.caption(f"{info['name']} ×{info['qty']}")
                rp.caption(f"PKR {info['price'] * info['qty']:,.0f}")

            st.divider()

            st.markdown(f"""
            <div class="receipt-row">
                <span class="r-label">Subtotal</span>
                <span class="r-value">PKR {subtotal:,.0f}</span>
            </div>
            <div class="receipt-row">
                <span class="r-label">GST (17%)</span>
                <span class="r-value">PKR {tax:,.0f}</span>
            </div>
            <div class="receipt-row">
                <span class="r-label">Platform Fee</span>
                <span class="r-value">PKR {PLATFORM_FEE:,.0f}</span>
            </div>
            <div class="receipt-total">
                <span class="r-label">Total</span>
                <span class="r-value">PKR {total:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)

        st.write("")

        # ── Checkout requires login ───────────────────────────────
        if not st.session_state.get("customer_logged_in"):
            st.markdown("""
            <div style='background:#f8f9fa;border:1px solid #e8f5f8;border-radius:10px;
                        padding:14px 16px;margin-bottom:12px;text-align:center;'>
                <i class="bi bi-lock-fill" style="color:#1a8fa8;font-size:20px;"></i>
                <p style='margin:6px 0 0 0;font-size:13px;color:#555;'>
                    <strong>Sign in</strong> to complete your purchase.<br>
                    Your cart items are saved.
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Sign In to Checkout →", type="primary", use_container_width=True):
                st.session_state["page_override"] = "Account"
                st.rerun()
            return

        # ── Checkout form (signed-in customers only) ──────────────
        with st.form("checkout_form", clear_on_submit=False):
            st.markdown("**📦 Delivery Details**")
            c_name    = st.text_input("Full Name",
                                      value=st.session_state["current_customer"]["name"])
            c_phone   = st.text_input("Phone Number", placeholder="+92 XXX XXXXXXX")
            c_address = st.text_area("Delivery Address", height=72,
                                     placeholder="House no, Street, City")

            st.markdown("**💳 Payment Method**")
            pay_method = st.radio("Payment", ["Cash on Delivery (COD)", "Credit/Debit Card"],
                                  label_visibility="collapsed")
            c_card = ""
            if pay_method == "Credit/Debit Card":
                c_card = st.text_input("Card Number", placeholder="4242 4242 4242 4242")
                st.caption("Sandbox test card: `4242 4242 4242 4242`")

            submitted = st.form_submit_button("Confirm & Pay 🔒", use_container_width=True)

            if submitted:
                if not c_name or not c_address or not c_phone:
                    st.error("Please fill in all delivery fields.")
                elif pay_method == "Credit/Debit Card" and \
                     c_card.replace(" ", "") != "4242424242424242":
                    st.error("Invalid card. Use sandbox: 4242 4242 4242 4242")
                else:
                    with st.spinner("🔒 Processing secure payment…"):
                        time.sleep(1.2)
                        customer_id = st.session_state["current_customer"]["id"]

                        # Build flat list for process_checkout (one entry per unit)
                        cart_list = []
                        for pid, info in st.session_state["cart"].items():
                            for _ in range(info["qty"]):
                                cart_list.append({
                                    "id":    int(pid),
                                    "name":  info["name"],
                                    "price": info["price"],
                                })

                        if process_checkout(cart_list, customer_id):
                            st.session_state["receipt"] = {
                                "order_id":    f"PTH-{random.randint(1000, 9999)}",
                                "name":        c_name,
                                "address":     c_address,
                                "method":      pay_method,
                                "items_count": sum(v["qty"] for v in st.session_state["cart"].values()),
                                "subtotal":    subtotal,
                                "tax":         tax,
                                "total":       total,
                            }
                            st.session_state["cart"] = {}
                            st.rerun()
                        else:
                            st.error("Checkout failed. Please try again.")


# ================================================================
# PAGE: ACCOUNT
# ================================================================
def page_account():
    # --- UI RENDER BUFFER ---
    time.sleep(0.15)
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
                padding:22px 32px 22px 32px; border-radius:14px;
                margin-bottom:28px; box-shadow:0 6px 24px rgba(15,32,39,0.18);">
        <div style="display:flex; align-items:center; justify-content:space-between;">
            <div>
                <div style="font-size:10.5px; font-weight:700; color:#7ecdd8;
                            text-transform:uppercase; letter-spacing:2px; margin-bottom:5px;">
                    <i class="bi bi-person-circle"></i>&nbsp; My Account
                </div>
                <span style="font-size:22px; font-weight:800; color:white; letter-spacing:-0.3px;">
                    Prime TechHub
                </span>
            </div>
            <div style="text-align:right;">
                <i class="bi bi-shield-check" style="font-size:28px; color:rgba(126,205,216,0.6);"></i>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="samsung-watermark">Prime TechHub Account</div>', unsafe_allow_html=True)

    if st.session_state["customer_logged_in"] and st.session_state["current_customer"]:
        customer = st.session_state["current_customer"]
        st.markdown(f"""
        <h4 style='margin-bottom:4px; font-size:22px;'>
            Hello, {customer['name'].split()[0]} <span style='font-size:18px;'>👋</span>
        </h4>
        <p style='color:#888; font-size:13px; margin-top:0;'>
            Welcome back to your Prime TechHub dashboard.
        </p>""", unsafe_allow_html=True)

        with st.container(border=True):
            m1, m2 = st.columns(2)
            m1.metric("Account Status", "Verified ✅")
            m2.metric("Membership", "Standard")
            st.divider()
            st.markdown(f"""
            <div style='font-size:14px; color:#555;'>
                <i class="bi bi-envelope-fill" style='color:#1a8fa8;'></i>
                &nbsp; <strong>Email:</strong> {customer['email']}
            </div>""", unsafe_allow_html=True)
            st.write("")
            st.markdown("**<i class='bi bi-bag-fill'></i> &nbsp;Recent Orders:**", unsafe_allow_html=True)
            orders = get_customer_orders(customer["id"])
            if orders:
                df_o = pd.DataFrame(orders, columns=["Product", "Price (PKR)", "Date"])
                st.dataframe(df_o, use_container_width=True, hide_index=True)
            else:
                st.info("No orders yet. Start shopping from the Home tab!")

        if st.button("Sign Out", type="primary", use_container_width=True):
            st.session_state["customer_logged_in"] = False
            st.session_state["current_customer"]   = None
            st.rerun()

    elif st.session_state["admin_logged_in"]:
        st.success("✅ Signed in as **System Administrator**.")
        st.info("Use the **Admin** tab in the sidebar to manage inventory and sales.")
        if st.button("Sign Out", type="primary", use_container_width=True):
            st.session_state["admin_logged_in"] = False
            st.rerun()

    else:
        _, col_mid, _ = st.columns([1, 1.4, 1])
        with col_mid:
            if st.session_state["account_mode"] == "login":
                st.markdown("""
                <h4 style='text-align:center; margin-bottom:3px; font-size:22px;
                           font-weight:700; color:#111;'>SIGN IN</h4>
                <p style='text-align:center; color:#888; font-size:13px; margin-top:0;'>
                    to continue to your Prime TechHub account
                </p>""", unsafe_allow_html=True)

                with st.container(border=True):
                    with st.form("login_form", clear_on_submit=False):
                        email    = st.text_input("Email / Username")
                        password = st.text_input("Password", type="password")
                        btn_login = st.form_submit_button("SIGN IN", use_container_width=True)
                        if btn_login:
                            admin = verify_admin(email, password)
                            if admin:
                                st.session_state["admin_logged_in"] = True
                                st.rerun()
                            else:
                                customer = verify_customer(email, password)
                                if customer:
                                    st.session_state["customer_logged_in"] = True
                                    st.session_state["current_customer"]   = customer
                                    st.rerun()
                                else:
                                    st.error("Account not found. Please check your credentials.")

                st.markdown("""
                <p style='text-align:center; color:#ccc; font-size:12px;
                           margin:10px 0 8px 0; font-weight:600;'>— &nbsp;OR&nbsp; —</p>
                """, unsafe_allow_html=True)

                st.markdown("""
                <a href="https://github.com/Aysha-Nur/Prime-TechHub#authentication-notice"
                   target="_blank" style="text-decoration:none;">
                    <div style="background:white; border:1px solid #dadce0; border-radius:7px;
                                padding:9px 20px; display:flex; align-items:center;
                                justify-content:center; gap:10px; cursor:pointer;
                                box-shadow:0 1px 4px rgba(0,0,0,0.06); margin-bottom:10px;
                                transition:box-shadow 0.22s ease;">
                        <img src="https://img.icons8.com/color/48/google-logo.png" style="width:17px;"/>
                        <span style="font-size:13.5px;font-weight:600;color:#5f6368;">
                            Sign in with Google
                        </span>
                    </div>
                </a>""", unsafe_allow_html=True)

                st.button(
                    "New to Prime TechHub? Create an account →",
                    on_click=lambda: st.session_state.update({"account_mode": "signup"}),
                    use_container_width=True
                )

            else:
                st.markdown("""
                <h4 style='text-align:center; margin-bottom:3px; font-size:22px;
                           font-weight:700; color:#111;'>Create Account</h4>
                <p style='text-align:center; color:#888; font-size:13px; margin-top:0;'>
                    Join Prime TechHub for a smarter home experience
                </p>""", unsafe_allow_html=True)

                with st.container(border=True):
                    with st.form("signup_form", clear_on_submit=False):
                        name     = st.text_input("Full Name")
                        email    = st.text_input("Email Address")
                        password = st.text_input("Password", type="password")
                        btn_reg  = st.form_submit_button("CREATE ACCOUNT", use_container_width=True)
                        if btn_reg:
                            if not name or not email or not password:
                                st.error("Please fill in all fields.")
                            else:
                                if register_customer(name, email, password):
                                    customer = verify_customer(email, password)
                                    st.session_state["customer_logged_in"] = True
                                    st.session_state["current_customer"]   = customer
                                    st.rerun()
                                else:
                                    st.error("This email is already registered. Please sign in.")

                st.button(
                    "Already have an account? Sign in →",
                    on_click=lambda: st.session_state.update({"account_mode": "login"}),
                    use_container_width=True
                )


# ================================================================
# PAGE: ADMIN DASHBOARD
# ================================================================
def page_admin():
    # --- UI RENDER BUFFER ---
    time.sleep(0.15)
    if not st.session_state.get("admin_logged_in"):
        st.error("🔒 Access Denied. Please sign in as Administrator from the Account tab.")
        return

    st.markdown("### ⚙️ Admin Dashboard — Inventory Management")
    tab1, tab2, tab3 = st.tabs(["➕ Add Product", "📊 Sales Ledger", "🗑️ Remove Product"])

    with tab1:
        st.markdown("#### Add New Device to Inventory")
        with st.form("add_product_form", clear_on_submit=True):
            p_name  = st.text_input("Product Name")
            p_cat   = st.selectbox("Category", ["Camera", "Lighting", "Smart Plug", "Hub/Controller", "Sensors", "Networking", "Audio"])
            p_price = st.number_input("Price (PKR)", min_value=0.0, step=100.0)
            p_stock = st.number_input("Stock Quantity", min_value=0, step=1)
            p_desc  = st.text_area("Description")
            submitted = st.form_submit_button("Add to Inventory", use_container_width=True)
            if submitted:
                if not p_name:
                    st.error("Product name is required.")
                else:
                    conn = sqlite3.connect("techhub.db")
                    conn.execute(
                        "INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)",
                        (p_name, p_cat, p_price, int(p_stock), p_desc)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"✅ '{p_name}' added to inventory!")

    with tab2:
        st.markdown("#### All Sales Records")
        conn = sqlite3.connect("techhub.db")
        try:
            orders_df = pd.read_sql_query(
                "SELECT o.id, c.name AS customer, o.product_name, o.price, o.sale_date "
                "FROM orders o LEFT JOIN customers c ON o.customer_id = c.id "
                "ORDER BY o.sale_date DESC", conn
            )
        except Exception:
            orders_df = pd.DataFrame()
        conn.close()
        if orders_df.empty:
            st.info("No sales recorded yet.")
        else:
            st.dataframe(orders_df, use_container_width=True, hide_index=True)
            st.metric("Total Revenue (PKR)", f"{orders_df['price'].sum():,.2f}")

    with tab3:
        st.markdown("#### Remove Device from Inventory")
        products_df = get_products()
        if products_df.empty:
            st.info("Inventory is empty.")
        else:
            item_to_delete = st.selectbox("Select product to remove:", products_df["name"].tolist())
            if st.button("🗑️ Delete Item", type="primary"):
                conn = sqlite3.connect("techhub.db")
                conn.execute("DELETE FROM products WHERE name = ?", (item_to_delete,))
                conn.commit()
                conn.close()
                st.success(f"Removed '{item_to_delete}' from inventory.")
                st.rerun()

    st.divider()
    if st.button("Sign Out of Admin", use_container_width=True):
        st.session_state["admin_logged_in"] = False
        st.rerun()


# ================================================================
# PAGE: SETTINGS
# ================================================================
def page_settings():
    # --- UI RENDER BUFFER ---
    time.sleep(0.15)
    st.markdown("### ⚙️ Account Settings")
    st.caption("Manage your Prime TechHub preferences and security.")

    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔔 Notifications", "🔒 Security"])

    with tab1:
        st.markdown("#### Personal Information")
        st.text_input("Full Name", placeholder="e.g., Ayisha Malik")
        st.text_input("Email Address", placeholder="Enter your email")
        st.text_input("Phone Number", placeholder="+92 XXX XXXXXXX")
        st.button("Save Profile Changes")

    with tab2:
        st.markdown("#### Notification Preferences")
        st.toggle("Order Updates", value=True, help="Receive emails about your order status.")
        st.toggle("Promotions & Offers", value=False, help="New smart home device deals.")
        st.toggle("Security Alerts", value=True, disabled=True, help="Mandatory. Cannot be turned off.")

    with tab3:
        st.markdown("#### Change Password")

        # Only works when customer is logged in
        if not st.session_state.get("customer_logged_in") or \
           not st.session_state.get("current_customer"):
            st.info("🔒 Sign in to your account to change your password.")
        else:
            with st.form("change_password_form", clear_on_submit=True):
                current_pw  = st.text_input("Current Password", type="password")
                new_pw      = st.text_input("New Password",      type="password")
                confirm_pw  = st.text_input("Confirm New Password", type="password")
                pw_submit   = st.form_submit_button(
                    "Update Password", use_container_width=True
                )

                if pw_submit:
                    if not current_pw or not new_pw or not confirm_pw:
                        st.error("Please fill in all three password fields.")
                    elif len(new_pw) < 6:
                        st.error("New password must be at least 6 characters.")
                    elif new_pw != confirm_pw:
                        st.error("New password and confirmation do not match.")
                    elif new_pw == current_pw:
                        st.warning("New password must be different from the current one.")
                    else:
                        customer_id = st.session_state["current_customer"]["id"]
                        result = update_customer_password(
                            customer_id, current_pw, new_pw
                        )
                        if result == 'success':
                            st.success("✅ Password updated successfully. Use your new password next time you sign in.")
                        elif result == 'wrong_password':
                            st.error("❌ Current password is incorrect.")
                        else:
                            st.error("Something went wrong. Please try again.")

        st.markdown("<hr style='margin-top:24px; margin-bottom:8px;'>", unsafe_allow_html=True)
        st.markdown("#### ⚠️ Danger Zone")
        st.markdown(
            "<p style='color:#666; font-size:13px;'>This will permanently delete your account and all order history.</p>",
            unsafe_allow_html=True
        )
        if st.button("Delete My Account", use_container_width=False):
            st.warning("Account deletion is not yet enabled in this build.")


# ================================================================
# PAGE: FAQ — UNTOUCHED
# ================================================================
def page_faq():
    # --- UI RENDER BUFFER ---
    time.sleep(0.15)
    st.markdown("### ❓ Frequently Asked Questions")
    st.caption("Everything you need to know about Prime TechHub.")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### 🚚 Shipping & Orders")
    with st.expander("How long does delivery take?"):
        st.markdown("**Standard Delivery:** 3–5 business days. **Express Delivery:** 1–2 business days. Orders placed before 2:00 PM are processed and dispatched the same day.")
    with st.expander("Can I track my order?"):
        st.info("Track your active orders in real-time by navigating to your **Account Dashboard**.")

    st.markdown("#### 🔄 Returns & Warranty")
    with st.expander("What is your return and warranty policy?"):
        st.markdown("Every Prime TechHub device includes a **30-day money-back guarantee** and a **1-year limited hardware warranty** covering manufacturing defects.")

    st.markdown("#### 🔒 Security & Privacy")
    with st.expander("Is my smart home data encrypted?"):
        st.markdown("**Yes.** Prime TechHub uses AES-256 encryption for all data in transit between your devices, our backend, and your mobile client. We never sell your telemetry data to third parties.")

    st.markdown("""
    <div class="faq-contact-box">
        <i class="bi bi-headset" style="font-size:22px;color:#1a8fa8;"></i>
        <h4 style='margin:8px 0 4px 0; color:#203a43; font-size:16px;'>Still need help?</h4>
        <p style='color:#555; font-size:13px; margin:0; line-height:1.7;'>
            Our support team is available 24/7.<br>
            <strong style='color:#1a8fa8;'>support@primetechhub.com</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# PAGE: ABOUT US — UNTOUCHED
# ================================================================
def page_about():
    # --- UI RENDER BUFFER ---
    time.sleep(0.15)
    st.markdown("### 🏢 About Prime TechHub")
    st.markdown("<p style='color:#666;'>Building the Future of Smart Home Infrastructure.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("#### 🎯 Our Mission")
            st.write("To make professional-grade smart home technology accessible, affordable, and beautifully simple for every household in Pakistan.")
    with col2:
        with st.container(border=True):
            st.markdown("#### 🛠️ Our Stack")
            st.write("Built on Python + Streamlit with SQLite, containerized via Docker, and served behind an Nginx reverse proxy for cloud-ready deployment.")
    with col3:
        with st.container(border=True):
            st.markdown("#### 🌍 Our Vision")
            st.write("Expand beyond Pakistan into a pan-South-Asian smart home platform, integrated with major cloud IoT ecosystems.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📊 Platform Highlights")
    m1, m2, m3, m4 = st.columns(4)
    for col, label, value in [
        (m1, "Products",   "25+"),
        (m2, "Categories", "9"),
        (m3, "Uptime SLA", "99.9%"),
        (m4, "Security",   "AES-256"),
    ]:
        col.markdown(f"""
        <div style='padding:16px; text-align:center;'>
            <div style='font-size:30px; font-weight:800; color:#111111;
                        line-height:1; margin-bottom:4px;'>{value}</div>
            <div style='font-size:12px; color:#888; font-weight:500;
                        text-transform:uppercase; letter-spacing:1px;'>{label}</div>
        </div>
        """, unsafe_allow_html=True)


# ================================================================
# MAIN ROUTER — handles both sidebar nav AND page_override
# (page_override is set by the cart header button)
# ================================================================
def main():
    init_db()
    init_session_state()
    inject_global_css()

    sidebar_page = render_sidebar()

    # Detect sidebar navigation click → clear any override
    last = st.session_state.get("_last_sidebar_page", "Home")
    if sidebar_page != last:
        st.session_state.pop("cached_products", None)  # force refresh on nav
        st.session_state["page_override"]      = None
        st.session_state["selected_product"]   = None   # clear detail on nav switch
        st.session_state["_last_sidebar_page"] = sidebar_page

    # Effective page: override wins (e.g. cart button), else sidebar
    active_page = st.session_state.get("page_override") or sidebar_page

    routes = {
        "Home":     page_home,
        "Cart":     page_cart,
        "Account":  page_account,
        "Admin":    page_admin,
        "Settings": page_settings,
        "FAQ":      page_faq,
        "About Us": page_about,
    }

    routes.get(active_page, page_home)()


if __name__ == "__main__":
    main()