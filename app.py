import streamlit as st

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
    process_checkout
)

import sqlite3
import pandas as pd
from streamlit_option_menu import option_menu

_CATEGORY_META = {
    "Camera":         ("bi-camera-video-fill", "linear-gradient(135deg,#203a43,#1a8fa8)"),
    "Lighting":       ("bi-lightbulb-fill", "linear-gradient(135deg,#1a8fa8,#5bc0de)"),
    "Smart Plug":     ("bi-plug-fill", "linear-gradient(135deg,#1a8fa8,#28a745)"),
    "Hub/Controller": ("bi-cpu-fill", "linear-gradient(135deg,#6f42c1,#1a8fa8)"),
    "Sensors":        ("bi-activity", "linear-gradient(135deg,#ff7e5f,#feb47b)"),
    "Networking":     ("bi-wifi", "linear-gradient(135deg,#00c6ff,#0072ff)"),
    "Audio":          ("bi-speaker-fill", "linear-gradient(135deg,#7f00ff,#e100ff)"),
}


# ================================================================
# GLOBAL CSS — injected once at the top, never inside page blocks.
# This prevents stacking / override conflicts.
# ================================================================
def inject_global_css():
    st.markdown("""
    <!-- Bootstrap Icons CDN — enables monochromatic icon system site-wide -->
    <link rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        /* ============================================================
           BRAND COLOR TOKENS
        ============================================================ */
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

        /* ============================================================
           LAYOUT CLEANUP
        ============================================================ */
        footer, #MainMenu { visibility: hidden; }
        header[data-testid="stHeader"]  { background: transparent !important; }
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
            max-width: 96% !important;
        }
        div[data-testid="InputInstructions"] { display: none !important; }
        hr { border-color: var(--border-light) !important; opacity: 1; }
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] input { cursor: pointer !important;
        }

        /* ============================================================
           SIDEBAR — elevated floating card aesthetic
           (shadow gives the illusion of floating over content)
        ============================================================ */
        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            box-shadow: 4px 0 28px rgba(0, 0, 0, 0.09) !important;
            border-right: 1px solid #f2f2f2 !important;
        }

        /* ============================================================
           TEAL PRIMARY BUTTONS
           (scoped to kind=primary only — doesn't affect danger/secondary)
        ============================================================ */
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
        /* Secondary/plain buttons — keep minimal */
        div[data-testid="stButton"] > button:not([kind="primary"]) {
            border-radius: 8px !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            color: var(--text-muted) !important;
        }

        /* ============================================================
           CATEGORY CHIP PILLS
        ============================================================ */
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

        /* ============================================================
           PRODUCT CARD HOVER
        ============================================================ */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            transition: box-shadow 0.25s ease, transform 0.2s ease;
            border-radius: 14px !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            box-shadow: 0 8px 32px rgba(26,143,168,0.14) !important;
            transform: translateY(-3px) !important;
        }

        /* ============================================================
           METRIC VALUE — teal accent
        ============================================================ */
        div[data-testid="stMetricValue"] {
            color: var(--teal-accent) !important;
            font-weight: 700 !important;
        }
        
        /* ============================================================
           HORIZONTAL SHOWCASE SCROLL (Samsung-style)
        ============================================================ */
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
        .showcase-scroll::-webkit-scrollbar-thumb {
            background: #c8d8dc; border-radius: 10px;
        }
        .showcase-card {
            min-width: 250px;
            max-width: 250px;
            background: #ffffff;
            border: 1px solid var(--border-light);
            border-radius: 16px;
            padding: 0 0 18px 0;
            scroll-snap-align: start;
            box-shadow: 0 2px 12px rgba(0,0,0,0.05);
            transition: box-shadow 0.25s ease, transform 0.2s ease;
            overflow: hidden;
        }
        .showcase-card:hover {
            box-shadow: 0 8px 28px rgba(26,143,168,0.14);
            transform: translateY(-4px);
        }
        .showcase-card-img {
            height: 120px;
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 14px;
        }
        .showcase-card-body { padding: 0 16px; }
        .s-cat {
            font-size: 10.5px;
            color: var(--teal-accent);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.4px;
            margin-bottom: 5px;
        }
        .s-name {
            font-size: 16px; font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 6px; line-height: 1.3;
        }
        .s-desc {
            font-size: 12.5px; color: var(--text-muted);
            margin-bottom: 12px; line-height: 1.5;
        }
        .s-price { font-size: 17px; font-weight: 700; color: var(--teal-accent); }

        /* ============================================================
           CART BADGE (sidebar)
        ============================================================ */
        .cart-badge {
            margin: 10px 12px 0 12px;
            padding: 10px 14px;
            background: linear-gradient(135deg, var(--teal-mid), var(--teal-accent));
            border-radius: 10px;
            display: flex; align-items: center; gap: 10px;
        }
        .cart-badge span { color: white; font-weight: 600; font-size: 13.5px; }

        /* ============================================================
           SAMSUNG ACCOUNT WATERMARK
        ============================================================ */
        .samsung-watermark {
            position: fixed; bottom: 18px; right: 26px;
            color: #c5d8dc; font-size: 17px; font-weight: 700;
            letter-spacing: 0.5px; z-index: 50; pointer-events: none;
            user-select: none;
        }
        /* ── FIX 1: Primary button — use data-testid (more reliable than kind attr) ── */
        button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #203a43, #1a8fa8) !important;
            border: none !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
        }
        button[data-testid="baseButton-primary"]:hover {
            opacity: 0.88 !important;
            transform: translateY(-1px) !important;
        }

        /* ══════════════════════════════════════════════════════
           FIX 4: INPUT DOUBLE-BORDER — single clean border only
           Root cause: CSS border on input + Streamlit wrapper
           border + st.container(border=True) = 3 stacked borders
        ═══════════════════════════════════════════════════════ */
        div[data-testid="stTextInput"] input {
            border: none !important;
            border-radius: 6px !important;
            box-shadow: none !important;
            background: transparent !important;
            padding: 6px 12px !important;
            cursor: text !important;
            pointer-events: all !important;
            font-size: 14px !important;
        }
        /* Single border lives here — on the wrapper only */
        div[data-testid="stTextInput"] > div[data-baseweb="input"] {
            border: 1.5px solid #e0e0e0 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
            pointer-events: all !important;
        }
        div[data-testid="stTextInput"] > div[data-baseweb="input"]:focus-within {
            border-color: #1a8fa8 !important;
            box-shadow: 0 0 0 3px rgba(26,143,168,0.10) !important;
        }
        div[data-testid="stTextInput"] > div[data-baseweb="input"]:hover {
            border-color: #1a8fa8 !important;
        }

        /* ══════════════════════════════════════════════════════
           FIX 3: ABOUT US METRICS — revert to black
           Remove the global teal override; scope teal only to
           sidebar cart badge where it was intentional
        ═══════════════════════════════════════════════════════ */
        div[data-testid="stMetricValue"] {
            color: #111111 !important;
            font-weight: 800 !important;
        }

        /* ══════════════════════════════════════════════════════
           FIX 6: SEARCH CURSOR — full surface interactive
        ═══════════════════════════════════════════════════════ */
        div[data-testid="stTextInput"],
        div[data-testid="stTextInput"] > div,
        div[data-testid="stTextInput"] > div > div,
        div[data-testid="stTextInput"] > div[data-baseweb="input"] {
            cursor: text !important;
            pointer-events: all !important;
            position: relative !important;
            z-index: 5 !important;
        }

        /* ══════════════════════════════════════════════════════
           FIX 7: CART BUTTON — teal primary (reliable selector)
        ═══════════════════════════════════════════════════════ */
        button[data-testid="baseButton-primary"],
        button[kind="primary"],
        .stButton button[data-testid^="baseButton"] {
            background: linear-gradient(135deg, #203a43, #1a8fa8) !important;
            border: none !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            transition: opacity 0.2s ease !important;
        }
        button[data-testid="baseButton-primary"]:hover {
            opacity: 0.88 !important;
        }
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #203a43, #1a8fa8) !important;
            border: none !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            width: 100% !important;
        }

        /* ══════════════════════════════════════════════════════
           FIX 2: FAQ last box — light teal only
        ═══════════════════════════════════════════════════════ */
        .faq-contact-box {
            margin-top: 24px;
            text-align: center;
            padding: 20px;
            background: #e8f5f8 !important;
            border-radius: 12px;
            border: 1px solid #c0dde4;
        }
    </style>
    """, unsafe_allow_html=True)


# ================================================================
# SESSION STATE INITIALIZER — run once, never inside page blocks
# ================================================================
def init_session_state():
    defaults = {
        "cart": [],
        "customer_logged_in": False,
        "admin_logged_in": False,
        "current_customer": None,
        "account_mode": "login",
        "show_login_message": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ================================================================
# SIDEBAR NAVIGATION
# ================================================================
def render_sidebar():
    menu_options = ["Home", "Filters", "Account", "Settings", "FAQ", "About Us"]
    menu_icons   = ["house-fill", "funnel-fill", "person-fill",
                    "gear-fill", "question-circle-fill", "info-square-fill"]

    if st.session_state.get("admin_logged_in"):
        menu_options.append("Admin")
        menu_icons.append("terminal-fill")

    with st.sidebar:
        # Brand block — no version string here
        st.markdown("""
        <div style='padding: 18px 16px 10px 16px;'>
            <span style='font-weight:800; font-size:19px;
                         letter-spacing:-0.5px; color:#111;'>
                Main Menu
            </span><br>
        </div>
        <hr style='margin: 0 0 6px 0; border-color:#f0f0f0;'>
        """, unsafe_allow_html=True)

        # "Main Menu" label — single instance, non-clickable
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
                "container":         {"padding": "0!important",
                                      "background-color": "transparent"},
                "icon":              {"font-size": "15px", "color": "#203a43"},
                "nav-link": {
                    "font-size":     "14px",
                    "text-align":    "left",
                    "margin":        "2px 0",
                    "color":         "#333",
                    "font-weight":   "500",
                    "--hover-color": "#f0f5f6",
                    "border-radius": "8px",
                    "padding":       "9px 14px",
                },
                "nav-link-selected": {
                    "background-color": "#e8f5f8",
                    "color":            "#1a8fa8",
                    "font-weight":      "700",
                },
            }
        )

        # Cart badge — only when cart has items
        cart_count = len(st.session_state.get("cart", []))
        if cart_count > 0:
            st.markdown(f"""
            <div style='margin: 8px 12px 0 12px; padding: 9px 14px;
                        background: linear-gradient(135deg, #203a43, #1a8fa8);
                        border-radius: 10px; display:flex;
                        align-items:center; gap:10px;'>
                <i class="bi bi-cart3"
                   style="color:white; font-size:16px;"></i>
                <span style="color:white; font-weight:600; font-size:13px;">
                    {cart_count} item{'s' if cart_count != 1 else ''} in cart
                </span>
            </div>
            """, unsafe_allow_html=True)

        # NO version string anywhere in sidebar — completely removed

    return page

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

    # NO swipe text — clean interface
    return f"""
    <div style="margin:0 0 8px 0;">
        <span style="font-size:10.5px;font-weight:700;color:#1a8fa8;
                     text-transform:uppercase;letter-spacing:1.6px;">
            <i class="bi bi-stars"></i>&nbsp; Featured Devices
        </span>
    </div>
    <div class="showcase-scroll" style="padding-bottom:8px;">{cards}</div>"""

# ================================================================
# PAGE: HOME (Storefront)
# Purpose: Hero banner, category chips, 3-column product grid
# ================================================================
def page_home():
    # ── Header ──────────────────────────────────────────────────────
    h1, h2, h3 = st.columns([1, 2.2, 0.55])

    with h1:
        st.markdown("""
        <div style='padding-top:5px;'>
            <span style='font-weight:900;font-size:24px;letter-spacing:-0.8px;color:#111;'>
                Prime TechHub</span><br>
            <span style='color:#999;font-size:11px;font-weight:500;'>Smart Home Devices</span>
        </div>""", unsafe_allow_html=True)

    with h2:
        # CSS scoped to this column only — fixes ghost label hit-testing
        st.markdown("""
        <style>
            /* Remove invisible label ghost that eats pointer events */
            div[data-testid="stTextInput"] label {
                height: 0 !important;
                overflow: hidden !important;
                margin: 0 !important;
                padding: 0 !important;
                pointer-events: none !important;
            }
            /* Full surface clickable — override any stacking suppression */
            div[data-testid="stTextInput"],
            div[data-testid="stTextInput"] > div,
            div[data-testid="stTextInput"] > div[data-baseweb="input"],
            div[data-testid="stTextInput"] input {
                pointer-events: all !important;
                cursor: text !important;
                position: relative !important;
                z-index: 20 !important;
            }
            /* Single clean border — no double border */
            div[data-testid="stTextInput"] > div[data-baseweb="input"] {
                border: 1.5px solid #e0e0e0 !important;
                border-radius: 25px !important;
                background: #f8f9fa !important;
                box-shadow: none !important;
                transition: border-color 0.2s, box-shadow 0.2s !important;
            }
            div[data-testid="stTextInput"] > div[data-baseweb="input"]:focus-within,
            div[data-testid="stTextInput"] > div[data-baseweb="input"]:hover {
                border-color: #1a8fa8 !important;
                background: #ffffff !important;
                box-shadow: 0 0 0 3px rgba(26,143,168,0.10) !important;
            }
            div[data-testid="stTextInput"] input {
                border: none !important;
                background: transparent !important;
                box-shadow: none !important;
                font-size: 14px !important;
                padding: 8px 16px !important;
            }
        </style>
        """, unsafe_allow_html=True)

        search_query = st.text_input(
            "Search products",
            placeholder="  Search smart devices 🔍…",
            label_visibility="collapsed",
            key="home_search"
        )

        # ── Live suggestion dropdown ──────────────────────────
        if search_query.strip():
            all_products = get_products()
            q = search_query.strip().lower()

            # Match against name AND category
            mask = (
                all_products["name"].str.lower().str.contains(q, na=False) |
                all_products["category"].str.lower().str.contains(q, na=False)
            )
            matches = all_products[mask & (all_products["stock"] > 0)]

            if matches.empty:
                st.markdown("""
                <div style='background:#fff8f0; border:1px solid #ffe0b2;
                            border-radius:8px; padding:10px 14px;
                            font-size:13px; color:#888; margin-top:4px;'>
                    <i class="bi bi-search"></i>
                    &nbsp; No matching smart home products found.
                </div>
                """, unsafe_allow_html=True)
            else:
                # Suggestion pills — clicking loads product detail
                for _, m in matches.head(5).iterrows():
                    if st.button(
                        f"  {m['name']}  ·  PKR {m['price']:,.0f}",
                        key=f"suggest_{m['id']}",
                        use_container_width=True
                    ):
                        st.session_state["selected_product"] = m.to_dict()
                        st.session_state["page_override"] = None
                        st.rerun()

    with h3:
        cart_count = len(st.session_state.get("cart", []))
        # FIX 7: Removed "items" label text. Button click routes to Cart.
        if st.button(f"🛒  {cart_count}", type="primary", key="hdr_cart_btn"):
            st.session_state["page_override"] = "Cart"
            st.rerun()

    st.markdown("<hr style='margin:0.4rem 0 0.7rem 0;'>", unsafe_allow_html=True)

    # ── Hero Banner (reduced padding — compact) ──────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
                padding:22px 28px 20px 28px; border-radius:14px; text-align:center;
                color:white; margin-bottom:18px;
                box-shadow:0 6px 24px rgba(15,32,39,0.18);">
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
            <span style="font-size:11.5px;color:#7ecdd8;">
                <i class="bi bi-wifi"></i>&nbsp;Wi-Fi Ready</span>
            <span style="font-size:11.5px;color:#7ecdd8;">
                <i class="bi bi-shield-lock"></i>&nbsp;AES-256 Secure</span>
            <span style="font-size:11.5px;color:#7ecdd8;">
                <i class="bi bi-box-seam"></i>&nbsp;Same-Day Dispatch</span>
            <span style="font-size:11.5px;color:#7ecdd8;">
                <i class="bi bi-arrow-return-left"></i>&nbsp;30-Day Returns</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Everything below this line stays exactly as-is in your current code ──
    products_df = get_products()

    if not products_df.empty:
        st.markdown(_build_showcase_html(products_df), unsafe_allow_html=True)
        # FIX 5: Vertical breathing room between showcase and grid
        st.markdown("<div style='margin-bottom:22px;'></div>", unsafe_allow_html=True)

    # ── Divider + Section title ──────────────────────────────────
    st.markdown("""
    <div style="display:flex; align-items:center; margin:8px 0 14px 0; gap:12px;">
        <span style="font-size:11px; font-weight:700; color:#1a8fa8;
                     text-transform:uppercase; letter-spacing:1.6px; white-space:nowrap;">
            <i class="bi bi-grid-3x3-gap-fill"></i>&nbsp; All Devices
        </span>
        <hr style="flex:1; margin:0; border-color:#ececec;">
    </div>
    """, unsafe_allow_html=True)

    # ── Category Filter Chips ────────────────────────────────────
    # To add a new category: just append it to this list.
    CATEGORIES = [
        "All", "Camera", "Lighting", "Smart Plug",
        "Hub/Controller", "Sensors", "Networking", "Audio"
    ]
    category_filter = st.radio(
        "Category", CATEGORIES,
        horizontal=True, label_visibility="collapsed"
    )
    st.write("")

    # ── Fetch + Filter ───────────────────────────────────────────
    if products_df.empty:
        st.warning("Inventory is empty. Add products via the Admin tab.")
        return

    filtered_df = products_df.copy()
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]

    safe_search = st.session_state.get("home_search", "")
    clean_query = safe_search.strip().lower().replace("-","").replace(" ","")
    if clean_query:
        filtered_df["_cn"] = (filtered_df["name"].str.lower()
                              .str.replace("-","",regex=False)
                              .str.replace(" ","",regex=False))
        filtered_df = filtered_df[filtered_df["_cn"].str.contains(clean_query, na=False)]

    filtered_df = filtered_df[filtered_df["stock"] > 0]

    if filtered_df.empty:
        st.info("No devices match your search or filter. Try a different category.")
        return

    st.caption(f"Showing **{len(filtered_df)}** device{'s' if len(filtered_df) != 1 else ''}")

    # ── 3-Column Product Grid ────────────────────────────────────
    # To change columns: update NUM_COLUMNS only.
    NUM_COLUMNS = 3
    cols = st.columns(NUM_COLUMNS)

    # Icon map for categories — extend this dict to add more categories
    CAT_ICONS = {
        "Camera":         "bi-camera-video-fill",
        "Lighting":       "bi-lightbulb-fill",
        "Smart Plug":     "bi-plug-fill",
        "Hub/Controller": "bi-cpu-fill",
        "Sensors":        "bi-activity",
        "Networking":     "bi-wifi",
        "Audio":          "bi-speaker-fill",
    }

    for i, (_, row) in enumerate(filtered_df.iterrows()):
        col = cols[i % NUM_COLUMNS]
        cat_icon = CAT_ICONS.get(row["category"], "bi-box-fill")

        with col:
            with st.container(border=True):
                # Category icon + label
                st.markdown(f"""
                <div style="font-size:11px; font-weight:700; color:#1a8fa8;
                            text-transform:uppercase; letter-spacing:1.2px; margin-bottom:6px;">
                    <i class="bi {cat_icon}"></i>&nbsp; {row['category']}
                </div>""", unsafe_allow_html=True)

                # Product name
                st.markdown(f"""
                <div style="font-size:17px; font-weight:600; color:#111;
                            margin-bottom:5px; line-height:1.3;">
                    {row['name']}
                </div>""", unsafe_allow_html=True)

                # Description
                if row.get("description"):
                    st.caption(row["description"])

                # Price
                st.markdown(f"""
                <div style="font-size:18px; font-weight:800; color:#1a8fa8;
                            margin:10px 0 8px 0;">
                    PKR {row['price']:,.0f}
                </div>""", unsafe_allow_html=True)

                # Stock indicator
                if row["stock"] <= 5:
                    st.markdown(f"""
                    <div style="font-size:12px; color:#c0392b; font-weight:600;
                                margin-bottom:8px;">
                        <i class="bi bi-exclamation-triangle-fill"></i>
                        &nbsp;Only {row['stock']} left
                    </div>""", unsafe_allow_html=True)
                elif row["stock"] <= 20:
                    st.markdown(f"""
                    <div style="font-size:12px; color:#e67e22; font-weight:600;
                                margin-bottom:8px;">
                        <i class="bi bi-dash-circle-fill"></i>
                        &nbsp;Low Stock — {row['stock']} remaining
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="font-size:12px; color:#27ae60; font-weight:600;
                                margin-bottom:8px;">
                        <i class="bi bi-check-circle-fill"></i>
                        &nbsp;In Stock ({row['stock']} units)
                    </div>""", unsafe_allow_html=True)

                # Add to Cart button
                if st.button(
                    "Add to Cart", type="primary",
                    key=f"add_{row['id']}", use_container_width=True
                ):
                    st.session_state["cart"].append({
                        "id": row["id"],
                        "name": row["name"],
                        "price": row["price"]
                    })
                    st.toast(f"✅ {row['name']} added to cart!")


# ================================================================
# PAGE: FILTERS
# Purpose: Same grid but with full sidebar filter controls
# ================================================================
def page_filters():
    st.markdown("## 🔍 Browse & Filter Devices")
    st.caption("Narrow down your perfect smart home setup.")

    products_df = get_products()
    if products_df.empty:
        st.info("Inventory is empty.")
        return

    col_filter, col_results = st.columns([1, 3])

    with col_filter:
        st.markdown("#### Filters")
        selected_cats = st.multiselect(
            "Category",
            options=sorted(products_df["category"].unique().tolist()),
            default=[]
        )
        min_price = int(products_df["price"].min())
        max_price = int(products_df["price"].max())
        price_range = st.slider("Price Range (PKR)", min_price, max_price, (min_price, max_price), step=500)
        in_stock_only = st.checkbox("In-Stock Only", value=True)

    with col_results:
        filtered = products_df.copy()
        if selected_cats:
            filtered = filtered[filtered["category"].isin(selected_cats)]
        filtered = filtered[(filtered["price"] >= price_range[0]) & (filtered["price"] <= price_range[1])]
        if in_stock_only:
            filtered = filtered[filtered["stock"] > 0]

        if filtered.empty:
            st.info("No products match your filters.")
        else:
            st.caption(f"Showing **{len(filtered)}** product(s)")
            NUM_COLUMNS = 3
            cols = st.columns(NUM_COLUMNS)
            for i, (_, row) in enumerate(filtered.iterrows()):
                col = cols[i % NUM_COLUMNS]
                with col:
                    with st.container(border=True):
                        st.markdown(f"<div style='font-size: 18px; font-weight: 500;'>{row['name']}</div>", unsafe_allow_html=True)
                        st.caption(f"📂 {row['category']}")
                        st.markdown(f"<div style='font-size: 17px; font-weight: 700; margin: 8px 0;'>PKR {row['price']:,.0f}</div>", unsafe_allow_html=True)
                        if st.button("Add to Cart", key=f"filter_add_{row['id']}", use_container_width=True):
                            st.session_state["cart"].append({"id": row["id"], "name": row["name"], "price": row["price"]})
                            st.toast(f"✅ Added {row['name']} to cart!")


# ================================================================
# PAGE: CART / CHECKOUT
# Purpose: Displays cart items, shipping form, processes payment
# ================================================================
def page_cart():
    st.markdown("### 🛒 Secure Checkout")

    # --- Guard: must be logged in as customer ---
    if not st.session_state.get("customer_logged_in") or not st.session_state.get("current_customer"):
        st.warning("🔒 Please sign in to your Prime TechHub account to view your cart.")
        st.info("Go to the **Account** tab in the sidebar to log in or register.")
        return

    # --- Post-checkout receipt display ---
    if "receipt" in st.session_state:
        r = st.session_state["receipt"]
        st.success("✅ Payment Successful! Your order has been confirmed.")
        with st.container(border=True):
            st.markdown(f"### Digital Receipt: `{r['order_id']}`")
            col1, col2 = st.columns(2)
            col1.write(f"**Customer:** {r['name']}")
            col1.write(f"**Shipped To:** {r['address']}")
            col2.write(f"**Payment:** {r['method']}")
            col2.write(f"**Items:** {r['items']}")
            st.metric("Total Paid", f"PKR {r['total']:,.2f}")
        if st.button("Continue Shopping", use_container_width=True):
            del st.session_state["receipt"]
            st.rerun()
        return

    # --- Empty cart ---
    if not st.session_state.get("cart"):
        st.info("Your cart is empty. Head to the Home tab to browse our smart devices.")
        return

    # --- Cart Items + Checkout Form ---
    cart = st.session_state["cart"]
    total = sum(item["price"] for item in cart)

    col_summary, col_form = st.columns([1, 1])

    with col_summary:
        st.markdown("#### Order Summary")
        for item in cart:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{item['name']}**")
                c2.write(f"PKR {item['price']:,.0f}")
        st.markdown("---")
        st.metric("Total Amount Due", f"PKR {total:,.2f}")
        if st.button("🗑️ Clear Cart", use_container_width=True):
            st.session_state["cart"] = []
            st.rerun()

    with col_form:
        st.markdown("#### Delivery & Payment")
        with st.form("checkout_form", clear_on_submit=False):
            st.write("**1. Delivery Address**")
            c_name    = st.text_input("Full Name", value=st.session_state["current_customer"]["name"])
            c_phone   = st.text_input("Phone Number", placeholder="+92 XXX XXXXXXX")
            c_address = st.text_area("Complete Address (House, Street, City)")

            st.write("**2. Payment Gateway (Sandbox)**")
            pay_method = st.radio("Method", ["Cash on Delivery (COD)", "Credit/Debit Card"])
            st.caption("For testing: use card `4242 4242 4242 4242`")
            c_card = st.text_input("Card Number", placeholder="16-digit card number")

            submitted = st.form_submit_button("Confirm & Pay 🔒", use_container_width=True)

            if submitted:
                if not c_name or not c_address or not c_phone:
                    st.error("Please fill in your complete name, phone, and delivery address.")
                elif pay_method == "Credit/Debit Card" and c_card.replace(" ", "") != "4242424242424242":
                    st.error("Payment Failed: Invalid card. Use sandbox card 4242 4242 4242 4242.")
                else:
                    import time, random
                    with st.spinner("🔒 Processing Secure Payment..."):
                        time.sleep(1.5)
                        customer_id = st.session_state["current_customer"]["id"]
                        if process_checkout(cart, customer_id):
                            st.session_state["receipt"] = {
                                "order_id": f"PTH-{random.randint(1000, 9999)}",
                                "name": c_name,
                                "address": c_address,
                                "method": pay_method,
                                "total": total,
                                "items": len(cart)
                            }
                            st.session_state["cart"] = []
                            st.rerun()
                        else:
                            st.error("Checkout failed. Please try again.")


# ================================================================
# PAGE: ACCOUNT
# Purpose: Customer login / register / dashboard. Admin sign-in.
# ================================================================
def page_account():
    # ── Samsung-style teal top bar (static div — no position:fixed) ──
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
                padding:22px 32px 22px 32px; border-radius:14px;
                margin-bottom:28px;
                box-shadow:0 6px 24px rgba(15,32,39,0.18);">
        <div style="display:flex; align-items:center; justify-content:space-between;">
            <div>
                <div style="font-size:10.5px; font-weight:700; color:#7ecdd8;
                            text-transform:uppercase; letter-spacing:2px; margin-bottom:5px;">
                    <i class="bi bi-person-circle"></i>&nbsp; My Account
                </div>
                <span style="font-size:22px; font-weight:800; color:white;
                             letter-spacing:-0.3px;">
                    Prime TechHub
                </span>
            </div>
            <div style="text-align:right;">
                <i class="bi bi-shield-check"
                   style="font-size:28px; color:rgba(126,205,216,0.6);"></i>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Watermark — bottom right corner
    st.markdown("""
    <div class="samsung-watermark">Prime TechHub Account</div>
    """, unsafe_allow_html=True)

    # ── CASE 1: Customer logged in ────────────────────────────────
    if st.session_state["customer_logged_in"] and st.session_state["current_customer"]:
        customer = st.session_state["current_customer"]
        st.markdown(f"""
        <h4 style='margin-bottom:4px; font-size:22px;'>
            Hello, {customer['name'].split()[0]}
            <span style='font-size:18px;'>👋</span>
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
            st.markdown("**<i class='bi bi-bag-fill'></i> &nbsp;Recent Orders:**",
                        unsafe_allow_html=True)
            orders = get_customer_orders(customer["id"])
            if orders:
                df_o = pd.DataFrame(orders, columns=["Product", "Price (PKR)", "Date"])
                st.dataframe(df_o, use_container_width=True, hide_index=True)
            else:
                st.info("No orders yet. Start shopping from the Home tab!")

        if st.button("Sign Out", type="primary", use_container_width=True):
            st.session_state["customer_logged_in"] = False
            st.session_state["current_customer"] = None
            st.rerun()

    # ── CASE 2: Admin logged in ───────────────────────────────────
    elif st.session_state["admin_logged_in"]:
        st.success("✅ Signed in as **System Administrator**.")
        st.info("Use the **Admin** tab in the sidebar to manage inventory and sales.")
        if st.button("Sign Out", type="primary", use_container_width=True):
            st.session_state["admin_logged_in"] = False
            st.rerun()

    # ── CASE 3: Not logged in — Login / Signup ───────────────────
    else:
        _, col_mid, _ = st.columns([1.2, 1, 1.2])
        with col_mid:
            if st.session_state["account_mode"] == "login":
                st.markdown("""
                <h4 style='text-align:center; margin-bottom:3px; font-size:22px;
                           font-weight:700; color:#111;'>Sign In</h4>
                <p style='text-align:center; color:#888; font-size:13px; margin-top:0;'>
                    Continue to your Prime TechHub account
                </p>""", unsafe_allow_html=True)

                with st.container(border=True):
                    with st.form("login_form", clear_on_submit=False):
                        email    = st.text_input("Email / Username")
                        password = st.text_input("Password", type="password")
                        btn_login = st.form_submit_button(
                            "SIGN IN", use_container_width=True
                        )
                        if btn_login:
                            admin = verify_admin(email, password)
                            if admin:
                                st.session_state["admin_logged_in"] = True
                                st.rerun()
                            else:
                                customer = verify_customer(email, password)
                                if customer:
                                    st.session_state["customer_logged_in"] = True
                                    st.session_state["current_customer"] = customer
                                    st.rerun()
                                else:
                                    st.error("Account not found. Please check your credentials.")

                # Divider text
                st.markdown("""
                <p style='text-align:center; color:#ccc; font-size:12px;
                           margin:10px 0 8px 0; font-weight:600;'>
                    — &nbsp;OR&nbsp; —
                </p>""", unsafe_allow_html=True)

                # Google button (decorative)
                st.markdown("""
                <a href="https://github.com/Aysha-Nur/Prime-TechHub#authentication-notice"
                   target="_blank" style="text-decoration:none;">
                    <div style="background:white; border:1px solid #dadce0;
                                border-radius:7px; padding:9px 20px;
                                display:flex; align-items:center; justify-content:center;
                                gap:10px; cursor:pointer;
                                box-shadow:0 1px 4px rgba(0,0,0,0.06);
                                margin-bottom:10px;
                                transition:background 0.2s ease;">
                        <img src="https://img.icons8.com/color/48/google-logo.png"
                             style="width:17px;"/>
                        <span style="font-size:13.5px; font-weight:600;
                                     color:#5f6368;">
                            Sign in with Google
                        </span>
                    </div>
                </a>""", unsafe_allow_html=True)

                st.button(
                    "New to Prime TechHub? Create an account →",
                    on_click=lambda: st.session_state.update({"account_mode": "signup"}),
                    use_container_width=True
                )

            else:  # signup mode
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
                        btn_reg  = st.form_submit_button(
                            "CREATE ACCOUNT", use_container_width=True
                        )
                        if btn_reg:
                            if not name or not email or not password:
                                st.error("Please fill in all fields.")
                            else:
                                if register_customer(name, email, password):
                                    customer = verify_customer(email, password)
                                    st.session_state["customer_logged_in"] = True
                                    st.session_state["current_customer"] = customer
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
# Purpose: Add products, view sales ledger, remove products
# Note: Only visible in sidebar after admin login via Account tab
# ================================================================
def page_admin():
    # Guard: must be admin
    if not st.session_state.get("admin_logged_in"):
        st.error("🔒 Access Denied. Please sign in as Administrator from the Account tab.")
        return

    st.markdown("### ⚙️ Admin Dashboard — Inventory Management")

    tab1, tab2, tab3 = st.tabs(["➕ Add Product", "📊 Sales Ledger", "🗑️ Remove Product"])

    # TAB 1: Add Product
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

    # TAB 2: Sales Ledger
    with tab2:
        st.markdown("#### All Sales Records")
        conn = sqlite3.connect("techhub.db")
        try:
            orders_df = pd.read_sql_query(
                "SELECT o.id, c.name AS customer, o.product_name, o.price, o.sale_date "
                "FROM orders o LEFT JOIN customers c ON o.customer_id = c.id "
                "ORDER BY o.sale_date DESC",
                conn
            )
        except Exception:
            orders_df = pd.DataFrame()
        conn.close()

        if orders_df.empty:
            st.info("No sales recorded yet.")
        else:
            st.dataframe(orders_df, use_container_width=True, hide_index=True)
            total_revenue = orders_df["price"].sum()
            st.metric("Total Revenue (PKR)", f"{total_revenue:,.2f}")

    # TAB 3: Remove Product
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
        st.text_input("Current Password", type="password")
        st.text_input("New Password", type="password")
        st.button("Update Password")

        st.markdown("<hr style='margin-top: 24px; margin-bottom: 8px;'>", unsafe_allow_html=True)
        st.markdown("#### ⚠️ Danger Zone")
        st.markdown("<p style='color:#666; font-size:13px;'>This will permanently delete your account and all order history.</p>", unsafe_allow_html=True)
        # Using a separate non-primary button for danger zone to avoid global style conflicts
        if st.button("Delete My Account", use_container_width=False):
            st.warning("Account deletion is not yet enabled in this build.")


# ================================================================
# PAGE: FAQ
# ================================================================
def page_faq():
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

    # FIX 2: Only this box gets teal background — uses scoped class
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
# PAGE: ABOUT US
# ================================================================
def page_about():
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
    # FIX 3: Hard-coded black metric values — immune to global CSS overrides
    m1, m2, m3, m4 = st.columns(4)
    for col, label, value in [
        (m1, "Products",   "15+"),
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
# MAIN ROUTER — the only entry point
# ================================================================
def main():
    # Step 1: Initialize database
    init_db()

    # Step 2: Initialize session state
    init_session_state()

    # Step 3: Inject CSS once
    inject_global_css()

    # Step 4: Render sidebar and get active page
    page = render_sidebar()

    # Step 5: Route to the correct page function
    if page == "Home":
        page_home()
    elif page == "Filters":
        page_filters()
    elif page == "Cart":
        page_cart()
    elif page == "Account":
        page_account()
    elif page == "Admin":
        page_admin()
    elif page == "Settings":
        page_settings()
    elif page == "FAQ":
        page_faq()
    elif page == "About Us":
        page_about()


if __name__ == "__main__":
    main()