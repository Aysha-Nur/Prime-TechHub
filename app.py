import streamlit as st
# --- NEW: FORCE ENTERPRISE WIDE LAYOUT ---
st.set_page_config(page_title="Prime TechHub", layout="wide", initial_sidebar_state="collapsed")
import sqlite3
import pandas as pd

from database import get_customer_orders, process_checkout, verify_admin

st.set_page_config(page_title="Prime TechHub", layout="wide")
# UI POLISH: Force the cursor to be a pointer (hand) on dropdowns
st.markdown("""
    <style>
    /* Target the selectbox container and input field to show the pointer hand */
    div[data-baseweb="select"] > div, div[data-baseweb="select"] input {
        cursor: pointer !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- NEW: DATABASE SETUP FUNCTION ---
def setup_database():
    """Creates all necessary database tables, including the new customers table."""
    conn = sqlite3.connect('techhub.db')
    c = conn.cursor()
    
    # Existing tables
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, price REAL, stock INTEGER, description TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT, price REAL)''')
    
    # NEW: Customer accounts table
    c.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, email TEXT UNIQUE, password TEXT)''')
    
    # Ensure at least one admin exists
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
        
    conn.commit()
    conn.close()

# --- DATABASE HELPER FUNCTIONS ---
def get_products():
    """Reads all products from the database."""
    conn = sqlite3.connect('techhub.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return df
def register_customer(full_name, email, password):
    """Saves a new customer to the database."""
    conn = sqlite3.connect('techhub.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customers (full_name, email, password) VALUES (?, ?, ?)", (full_name, email, password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError: # This triggers if the email is already registered
        success = False
    conn.close()
    return success

def verify_customer(email, password):
    """Checks customer login credentials."""
    conn = sqlite3.connect('techhub.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"id": user[0], "name": user[1], "email": user[2]}
    return None

def verify_login(username, password):
    """Checks admin credentials."""
    conn = sqlite3.connect('techhub.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def add_product(name, category, price, stock, desc):
    """Inserts a new product into the database."""
    conn = sqlite3.connect('techhub.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)",
                   (name, category, price, stock, desc))
    conn.commit()
    conn.close()

def get_orders():
    """Reads all sales records from the database."""
    conn = sqlite3.connect('techhub.db')
    # Read the orders table. If it crashes (e.g., table doesn't exist yet), return an empty dataframe.
    try:
        df = pd.read_sql_query("SELECT * FROM orders", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

# --- MAIN APPLICATION ROUTING ---
def main():
    setup_database() # <--- NEW: This ensures your database updates silently in the background
    
    from streamlit_option_menu import option_menu

    # --- ENTERPRISE UI STYLING (Layout Fixes) ---
    st.markdown("""
        <style>
            /* Hide Default Streamlit Clutter */
            footer {visibility: hidden;}
            header {background-color: transparent !important;}
            
            /* ABSOLUTE ZERO TOP SPACE - Pulls app completely to the ceiling */
            .block-container {
                padding-top: 0rem !important; 
                padding-bottom: 0rem !important;
                margin-top: 0rem !important;
                max-width: 95% !important; 
            }
            div[data-testid="stAppViewBlockContainer"] {
                padding-top: 1rem !important;
            }
            
            /* Nordic Minimalist Global Overrides */
            hr {
                border-color: #E0E0E0 !important;
                opacity: 1.0;
            }
            
            /* Hide the default "Press Enter to apply" text */
            div[data-testid="InputInstructions"] {
                display: none !important;
            }
        </style>
        """, unsafe_allow_html=True)

   # =====================================================================
    # 1. ENTERPRISE LEFT SIDEBAR NAVIGATION
    # =====================================================================
    menu_options = ["Home", "Filters", "Cart", "Account", "Settings", "FAQ", "About Us"]
    menu_icons = ["house", "funnel", "cart3", "person", "gear", "question-circle", "info-square"] 
    
    if st.session_state.get('admin_logged_in', False):
        menu_options.append("Admin")
        menu_icons.append("terminal")

    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        page = option_menu(
            menu_title="Prime TechHub", 
            options=menu_options,
            icons=menu_icons,
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent", "border": "none"},
                "icon": {"font-size": "18px", "color": "#111111"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "4px 0px", "color": "#111111", "font-weight": "600", "--hover-color": "#F5F5F5", "border-radius": "8px"},
                "nav-link-selected": {"background-color": "#E6E8ED", "color": "#111111", "font-weight": "bold"},
                "menu-title": {"cursor": "default"}
            }
        )

    # =====================================================================
    # 2. DYNAMIC GLOBAL HEADER (Only displays on Home & Filters)
    # =====================================================================
    if page in ["Home", "Filters"]:
        head_c1, head_c2, head_c3 = st.columns([1, 2, 1])
        
        with head_c1:
            st.markdown("""
                <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%;'>
                    <span style='font-weight: 900; font-size: 38px; letter-spacing: -1px; line-height: 1; color: black;'>Prime TechHub</span>
                    <span style='color: black; font-size: 14px; margin-top: 4px;'>Smart Home Devices</span>
                </div>
                """, unsafe_allow_html=True)
            
        with head_c2:
            st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
            product_names = [
                "Aura Smart Bulb (RGB)", 
                "Acoustic Echo Smart Speaker", 
                "AquaLeak Smart Sensor", 
                "BioMetric Smart Lock Pro", 
                "Camera - PrimeVision 4K", 
                "Doorbell Cam Pro"
            ]
            
            global_search = st.selectbox(
                "Search", 
                options=product_names, 
                index=None, 
                placeholder="Search devices...", 
                label_visibility="collapsed"
            )
            
        with head_c3:
            st.write("")
    else:
        # Failsafe: Ensures the variable exists so code on other pages doesn't crash
        global_search = None

    # 1. STOREFRONT PAGE
    if page == "Home":
        # --- HORIZONTAL CATEGORY PILLS ---
        category_filter = st.radio(
            "Filter by Category",
            ["All", "Camera", "Lighting", "Smart Plug", "Hub/Controller", "Sensors", "Networking", "Audio"],
            horizontal=True, 
            label_visibility="collapsed"
        )
        st.write("") # Small spacing below categories

        # Fetch products
        products_df = get_products()
        
        if products_df.empty:
            st.warning("The inventory is currently empty. Please add items via the Admin Dashboard.")
        else:
             
            is_searching = False

            # Apply filters
            if category_filter != "All":
                products_df = products_df[products_df['category'] == category_filter]
                is_searching = True
            
            # --- FIX: NOW USING THE GLOBAL SEARCH BAR AT THE TOP ---
            safe_search = global_search if global_search is not None else ""
            clean_query = safe_search.strip().lower().replace("-", "").replace(" ", "")
            if clean_query:
                is_searching = True
                
                products_df['clean_name'] = products_df['name'].str.lower().str.replace("-", "", regex=False).str.replace(" ", "", regex=False)
                
                products_df = products_df[products_df['clean_name'].str.contains(clean_query, na=False)]
            
            
            products_df = products_df[products_df['stock'] > 0]


            if products_df.empty and is_searching:
                st.warning("We're sorry, no such products found. Please try different keywords or browse our categories.")
            elif products_df.empty and not is_searching:
                st.info("No active devices available in the inventory right now.")
            else:
                if 'cart' not in st.session_state:
                    st.session_state['cart'] = []
                    
                # --- FIX: ENTERPRISE E-COMMERCE GRID LAYOUT ---
                # This breaks products into 3 neat columns instead of a massive vertical list
                NUM_COLUMNS = 3 
                cols = st.columns(NUM_COLUMNS)
                
                for i, (index, row) in enumerate(products_df.iterrows()):
                    # Distribute products evenly across the columns
                    col_idx = i % NUM_COLUMNS 
                    
                    with cols[col_idx]:
                        # Wrap each product in a neat "Card" box
                        with cols[col_idx]:
                            # Wrap each product in a neat "Card" box
                            with st.container(border=True):
                                # SURGICAL FIX: Un-bolded product name (22px), smaller but bold price (18px)
                                st.markdown(f"<div style='font-size: 22px; font-weight: 400; margin-bottom: 5px;'>{row['name']}</div>", unsafe_allow_html=True)
                                st.caption(f"📂 {row['category']}")
                                st.markdown(f"<div style='font-size: 18px; font-weight: 700; margin-top: 10px; margin-bottom: 10px;'>{row['price']:,.2f} PKR</div>", unsafe_allow_html=True)
                                
                                # Stock alert
                                if row['stock'] <= 20:
                                    st.error(f"⚠️ Low Stock: {row['stock']} left")
                                else:
                                    st.success(f"📦 {row['stock']} available")
                                    
                                # Full-width add to cart button
                                if st.button("Add to Cart", key=f"add_{row['id']}", use_container_width=True):
                                    st.session_state['cart'].append({
                                        "id": row['id'], 
                                        "name": row['name'], 
                                        "price": row['price']
                                    })
                                    st.toast(f"Added {row['name']} to cart!")
   # 2. ADMIN DASHBOARD PAGE
    elif page == "Admin Dashboard":
        st.title("Inventory Management")
        
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False

        if not st.session_state['logged_in']:
            st.subheader("Admin Login")
            # --- FIX 1: Wrap inputs in st.form to allow "Enter" key submission ---
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    if verify_login(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['show_login_message'] = True # Trigger for the green line
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        else:
            # --- FIX 2: Show success message temporarily, then vanish ---
            if st.session_state.get('show_login_message', False):
                import time
                success_msg = st.empty()
                success_msg.success("Logged in successfully.")
                time.sleep(2)
                success_msg.empty() # Clears the message instantly
                st.session_state['show_login_message'] = False
            
            tab1, tab2, tab3 = st.tabs(["Add New Product", "Sales Ledger", "Remove Product"])
            
            # TAB 1: ADD PRODUCTS
            with tab1:
                st.subheader("Add to Inventory")
                with st.form("add_product_form"):
                    p_name = st.text_input("Product Name")
                    p_cat = st.selectbox("Category", ["Camera", "Lighting", "Smart Plug", "Hub/Controller", "Sensors", "Networking", "Audio"])
                    p_price = st.number_input("Price (PKR)", min_value=0.0, step=100.0)
                    p_stock = st.number_input("Stock Quantity", min_value=0, step=1)
                    p_desc = st.text_area("Description")
                    
                    submitted = st.form_submit_button("Add to Inventory")
                    
                    if submitted:
                        add_product(p_name, p_cat, p_price, p_stock, p_desc)
                        st.success(f"Successfully added '{p_name}' to the database!")
                        st.write("<br><br><br><br>", unsafe_allow_html=True)

            # TAB 2: VIEW SALES
            with tab2:
                st.subheader("Recent Sales History")
                orders_df = get_orders()
                if orders_df.empty:
                    st.info("No sales have been made yet.")
                else:
                    st.dataframe(orders_df, use_container_width=True, hide_index=True)
                    if 'price' in orders_df.columns:
                        total_revenue = orders_df['price'].sum()
                        st.metric(label="Total Revenue (PKR)", value=f"{total_revenue:,.2f}")
                    else:
                        st.metric(label="Total Revenue (PKR)", value="0.00")
                        
            with tab3:
                st.subheader("Remove from Database")
                del_df = get_products()
                if del_df.empty:
                    st.info("Inventory is empty.")
                else:
                    item_to_delete = st.selectbox("Select product to remove:", del_df['name'].tolist())
                    if st.button("Delete Item", type="primary"):
                        conn = sqlite3.connect('techhub.db')
                        c = conn.cursor()
                        c.execute("DELETE FROM products WHERE name = ?", (item_to_delete,))
                        conn.commit()
                        conn.close()
                        st.success(f"Permanently removed {item_to_delete}.")
                        st.rerun()

            # --- FIX 3: Logout button moved to the very bottom ---
            st.divider()
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                st.rerun()
                # 5. SETTINGS PAGE
    elif page == "Settings":
        st.markdown("<h3 style='text-align: center; margin-bottom: 5px;'>Account Settings</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; margin-bottom: 30px; font-size: 14px;'>Manage your Prime TechHub preferences and security.</p>", unsafe_allow_html=True)
        
        # Native Streamlit tabs for a clean, organized UI
        tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔔 Notifications", "🔒 Security"])
        
        with tab1:
            st.markdown("#### Personal Information")
            st.text_input("Full Name", placeholder="e.g., Shafqat Ali")
            st.text_input("Email Address", placeholder="Enter your email")
            st.text_input("Phone Number", placeholder="+92 XXX XXXXXXX")
            st.button("Save Profile Changes")
            
        with tab2:
            st.markdown("#### Notification Preferences")
            st.toggle("Order Updates", value=True, help="Receive emails about your order status.")
            st.toggle("Promotions & Offers", value=False, help="Receive emails about new smart home devices.")
            st.toggle("Security Alerts", value=True, disabled=True, help="Mandatory alerts for unusual account activity.")
            
        with tab3:
            st.markdown("#### Account Security")
            st.text_input("Current Password", type="password")
            st.text_input("New Password", type="password")
            st.button("Update Password")
            
            # --- COMPACT DANGER ZONE START ---
            # --- COMPACT DANGER ZONE START ---
            
            # FIX 1: Replaced st.divider() with an HTML line to pull the whole block UP
            st.markdown("""
                <hr style='margin-top: 20px; margin-bottom: 10px; border: none; border-top: 1px solid #e6e6e6;'>
                <h4 style='margin-top: 0px; margin-bottom: 5px; padding-bottom: 0px;'>Danger Zone</h4>
                
                <style>
                    /* FIX 2: Set margin-top to -5px to pull the button comfortably close to the text */
                    button[kind="primary"] {
                        margin-top: 10px !important;       
                        background-color: transparent !important;
                        border-color: #FF0000 !important; 
                        color: #FF0000 !important;        
                    }
                    button[kind="primary"]:hover {
                        background-color: #fff0f0 !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            st.button("Delete Account", type="primary")
            # --- COMPACT DANGER ZONE END ---

    # 6. ABOUT US PAGE
    elif page == "About Us":
        # --- HERO SECTION ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; font-weight: 700; margin-bottom: 5px;'>Building the Future of Home Infrastructure</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; margin-bottom: 35px; font-size: 16px;'>Prime TechHub is more than an e-commerce platform—it is a complete smart ecosystem.</p>", unsafe_allow_html=True)
        
        # --- THE ARCHITECTURE / STORY ---
        st.markdown("### 🏗️ Our Architecture")
        st.markdown("""
        Prime TechHub was engineered with a strict focus on **scalable IT infrastructure and secure networking**. 
        We recognized that modern smart homes require the same level of reliability as enterprise-level systems. 
        That is why we built a centralized, containerized platform that ensures your smart devices communicate seamlessly, securely, and without interruption.
        """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- CORE VALUES (3 Column Grid) ---
        st.markdown("### 🌟 Core Principles")
        
        # Native Streamlit columns create a perfect responsive grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**🔒 Security First**")
            st.markdown("<p style='font-size: 14px; color: #555; margin-top: -10px;'>Enterprise-grade encryption and local execution to keep your private home network completely safe.</p>", unsafe_allow_html=True)
            
        with col2:
            st.info("**⚡ Seamless Flow**")
            st.markdown("<p style='font-size: 14px; color: #555; margin-top: -10px;'>Designed to work flawlessly on standard bandwidth without requiring complex external bridges.</p>", unsafe_allow_html=True)
            
        with col3:
            st.info("**🌍 Global Standards**")
            st.markdown("<p style='font-size: 14px; color: #555; margin-top: -10px;'>Built to international IT administration networking standards, ensuring reliability anywhere in the world.</p>", unsafe_allow_html=True)

        st.markdown("<br><hr style='border: none; border-top: 1px solid #e6e6e6; margin-bottom: 25px;'>", unsafe_allow_html=True)
        
        # --- THE VISION / LEADERSHIP SECTION ---
        st.markdown("### 🚀 The Vision")
        st.markdown("""
        > *"Our goal is to bridge the gap between complex IT infrastructure and everyday consumer technology. Prime TechHub is a testament to what happens when rigorous network engineering meets intuitive user design."*
        """)
        
        st.markdown("<br><br>", unsafe_allow_html=True)

    # 7. FAQ & HELP CENTER
    elif page == "FAQ":
        # --- HERO SECTION ---
        st.markdown("<h2 style='text-align: center; font-weight: 700; margin-bottom: 5px;'>How can we help?</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; margin-bottom: 25px; font-size: 16px;'>Search our knowledge base or browse categories below.</p>", unsafe_allow_html=True)
        
        # Centralized Search Bar UI (Creates a premium support center aesthetic)
        col_spacer1, search_col, col_spacer2 = st.columns([1, 2, 1])
        with search_col:
            st.text_input("Search", placeholder="e.g., 'Wi-Fi pairing' or 'Reset device'...", label_visibility="collapsed")
        
        st.markdown("<br><br>", unsafe_allow_html=True)

        # --- CATEGORY 1: DEVICE SETUP & TECH ---
        # FIX: Negative top margin (-35px) sucks the gap closed and pulls the whole page up
        st.markdown("<h3 style='margin-top: -35px;'>🔌 Setup & Connectivity</h3>", unsafe_allow_html=True)
        with st.expander("Are Prime TechHub devices compatible with 5GHz Wi-Fi?"):
            st.markdown("""
            For maximum range and wall-penetration, Prime TechHub devices are currently optimized for **2.4GHz Wi-Fi networks**. 
            
            *If you have a dual-band router, ensure your phone is connected to the 2.4GHz band during the initial setup process. Once paired, you can switch your phone back to 5GHz.*
            """)
            
        with st.expander("How do I perform a hard factory reset?"):
            st.markdown("""
            If your device is unresponsive or you are moving it to a new network, follow these steps:
            1. Unplug the device for 10 seconds.
            2. Plug it back in.
            3. Press and hold the physical **Action Button** for 12-15 seconds.
            4. Release when the LED indicator blinks **rapidly in blue**.
            
            The device is now in pairing mode and ready to be set up in your dashboard.
            """)

        with st.expander("Do these devices work if my internet goes down?"):
            st.markdown("Yes. While remote access from outside your home requires an active internet connection, your pre-set local automations (like scheduled lights or thermostat rules) will continue to execute locally on your home network.")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- CATEGORY 2: ORDERS & SHIPPING ---
        st.markdown("### 📦 Orders & Shipping")
        with st.expander("How long does delivery typically take?"):
            st.markdown("""
            We offer two shipping tiers for our customers:
            * **Standard Delivery:** 3-5 business days.
            * **Express Delivery:** 1-2 business days.
            
            All orders placed before 2:00 PM are processed and shipped on the same business day.
            """)
            st.info("You can track your active orders in real-time by navigating to your Account Dashboard.")

        with st.expander("What is your return and warranty policy?"):
            st.markdown("""
            We stand by our hardware. Every Prime TechHub device comes with:
            * A **30-day money-back guarantee** for any reason.
            * A **1-year limited hardware warranty** covering any manufacturing defects.
            """)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- CATEGORY 3: SECURITY & PRIVACY ---
        st.markdown("### 🔒 Security & Privacy")
        with st.expander("Is my smart home data encrypted?"):
            st.markdown("""
            **Absolutely.** Prime TechHub utilizes AES-256 bit encryption for all data transmitted between your home devices, our servers, and your mobile application. 
            
            We do not sell your telemetry data to third-party advertisers. Your home is your private space, and our infrastructure is designed to keep it that way.
            """)
        
        # FIX: Removed the <br> and <hr> entirely to kill the double-line defect.
        # Added margin-top directly to the box to pull it closer to the expander above.
        st.markdown("""
        <div style='margin-top: 20px; text-align: center; padding: 12px; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 40px;'>
            <h4 style='margin-top: 0px; margin-bottom: 5px;'>Still need help?</h4>
            <p style='color: #666; font-size: 14px; margin-bottom: 0px;'>Our technical support team is available 24/7 to assist you with your smart home setup.</p>
            <p style='font-weight: bold; color: #111; margin-top: 5px; margin-bottom: 0px;'>support@primetechhub.com</p>
        </div>
        """, unsafe_allow_html=True)
                        
    # 3. CART PAGE
    elif page == "Cart":
        # SURGICAL FIX: Shrunk the massive checkout title to a professional h3 tag
        st.markdown("<h3 style='margin-bottom: 20px; font-size: 26px;'>🛒 Secure Checkout</h3>", unsafe_allow_html=True)
        
        # --- ENFORCE CUSTOMER LOGIN ---
        if not st.session_state.get('customer_logged_in') or st.session_state.get('current_customer') is None:
            st.warning("🔒 Please sign in to your Prime TechHub account to view your cart and checkout.")
            st.info("Navigate to the 'Account' tab in the sidebar to log in or register.")
            
        elif 'receipt' in st.session_state:
            st.success("✅ Payment Successful! Your order has been confirmed.")
            st.info(f"""
            **Digital Receipt: #{st.session_state['receipt']['order_id']}**
            * **Customer:** {st.session_state['receipt']['name']}
            * **Shipped To:** {st.session_state['receipt']['address']}
            * **Payment Method:** {st.session_state['receipt']['method']}
            * **Items Purchased:** {st.session_state['receipt']['items']}
            * **Total Paid:** {st.session_state['receipt']['total']:,.2f} PKR
            """)
            if st.button("Continue Shopping"):
                del st.session_state['receipt']
                st.rerun()
                
        elif 'cart' not in st.session_state or len(st.session_state['cart']) == 0:
            st.info("Your cart is currently empty. Visit the Storefront to add items.")
            
        else:
            total_price = sum(item['price'] for item in st.session_state['cart'])
            
            st.subheader("Order Summary")
            for item in st.session_state['cart']:
                st.write(f"- {item['name']} : {item['price']} PKR")
            st.metric(label="Total Amount due", value=f"{total_price:,.2f} PKR")
            
            st.divider()
            st.subheader("Shipping & Payment")
            
            with st.form("checkout_form"):
                st.write("**1. Delivery Address**")
                c_name = st.text_input("Full Name", value=st.session_state['current_customer']['name']) # Auto-fills their name
                c_phone = st.text_input("Phone Number")
                c_address = st.text_area("Complete Address (House, Street, City)")
                
                st.write("**2. Payment Gateway (Sandbox)**")
                pay_method = st.radio("Select Payment Method", ["Cash on Delivery (COD)", "Credit/Debit Card"])
                st.caption("For testing Credit Card, use the sandbox number: 4242 4242 4242 4242")
                c_card = st.text_input("Card Number", placeholder="16-digit card number")
                
                submitted = st.form_submit_button("Confirm & Pay")
                
                if submitted:
                    if not c_name or not c_address or not c_phone:
                        st.error("Please fill in your complete name, phone, and delivery address.")
                    elif pay_method == "Credit/Debit Card" and c_card.replace(" ", "") != "4242424242424242":
                        st.error("Payment Failed: Invalid Card Number. Please use the testing card.")
                    else:
                         # --- NEW: PASS THE CUSTOMER ID TO THE DATABASE ---
                        active_customer_id = st.session_state['current_customer']['id']
                        
                        import time
                        # --- ENTERPRISE UPGRADE: Loading Spinner ---
                        with st.spinner("🔒 Processing Secure Payment through Gateway..."):
                            time.sleep(1.5) # Simulated network delay for realism
                            
                            if process_checkout(st.session_state['cart'], active_customer_id):
                                import random
                                st.session_state['receipt'] = {
                                    "order_id": f"PTH-{random.randint(1000, 9999)}",
                                    "name": c_name,
                                    "address": c_address,
                                    "method": pay_method,
                                    "total": total_price,
                                    "items": len(st.session_state['cart'])
                                }
                                st.session_state['cart'] = [] 
                                st.rerun()
                            else:
                                st.error("Checkout failed. Database error.")

                            
   # 4. ACCOUNT PAGE
    elif page == "Account":
        # --- LOGIN PAGE TEXT STYLING ---
        st.markdown("""
            <style>
                /* 1. Targets the text input labels (Email/Username & Password) */
                div[data-testid="stTextInput"] label p {
                    color: #555555 !important;
                    font-weight: 600 !important;
                    font-size: 15px !important;
                }
                
                /* 2. Targets BOTH standard buttons AND Form Submit buttons (SIGN IN) */
                div[data-testid="stButton"] button p,
                div[data-testid="stFormSubmitButton"] button p {
                    color: #555555 !important;
                    font-weight: 600 !important;
                }
            </style>
        """, unsafe_allow_html=True)
        # --- ENTERPRISE UI STYLING (Hide "Press Enter" Tooltips) ---
        st.markdown("""
            <style>
                /* Hides tooltip */
                [data-testid="InputInstructions"] { display: none !important;
                }
                /* FIX 1: Shrinks the text of the "Create an account" button (ignores the SIGN IN button) */
                div[data-testid="stButton"] button p {
                    font-size: 13px !important; 
                }
                /* 3. THE TRUE ARROW FIX: Targets the top header bar directly, bypassing the broken ID name */
        header[data-testid="stHeader"] {
            background: transparent !important; 
            z-index: 999 !important; /* Physically pushes the arrow container ABOVE our black banner */
        }
        
        header[data-testid="stHeader"] button {
            filter: invert(1) brightness(2) !important; /* Forcefully flips the dark ink to pure white */
        }
        /* 4. Hides the browser's native extra eye icon so only Streamlit's clean eye remains */
        input::-ms-reveal,
        input::-ms-clear {
            display: none !important;
        }
        
        input::-webkit-credentials-auto-fill-button {
            display: none !important;
            visibility: hidden !important;
        }
            </style>
        """, unsafe_allow_html=True)
        
       # --- 1. PREMIUM SAMSUNG-STYLE HEADER (Thicker & Fixed) ---
        st.markdown("""
            <style>
                .samsung-header {
                    position: fixed;
                    top: 0px;
                    left: 0px;
                    width: 100vw;
                    background-color: #111111;
                    /* Increased top and bottom padding from 12/15px to 35px to make it thick */
                    padding: 25px 0px 30px 60px; 
                    z-index: 99; 
                }
            </style>
            <div class="samsung-header">
                <span style="color: #FFFFFF; font-size: 24px; font-weight: 600; letter-spacing: -0.5px;">Prime TechHub Account</span>
            </div>
            
            <div style="margin-top: 110px;"></div> 
        """, unsafe_allow_html=True)

        # Centering the UI perfectly for Wide Mode
        _, col_mid, _ = st.columns([1.5, 1, 1.5])

        # --- Safely initialize ALL session states ---
        if 'customer_logged_in' not in st.session_state:
            st.session_state['customer_logged_in'] = False
        if 'admin_logged_in' not in st.session_state: # NEW: Admin tracking
            st.session_state['admin_logged_in'] = False
        if 'current_customer' not in st.session_state:
            st.session_state['current_customer'] = None
        if 'account_mode' not in st.session_state:
            st.session_state['account_mode'] = "login"

        with col_mid:
            # Check if NO ONE is logged in
            if not st.session_state['customer_logged_in'] and not st.session_state['admin_logged_in']:
                if st.session_state['account_mode'] == "login":
                   # SURGICAL FIX: Negative top margin explicitly drags the Sign In box up
                    st.markdown("<h3 style='text-align: center; margin-top: -35px; margin-bottom: 0px; font-size: 24px;'>Login / Register</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; color: #5f6368; font-size: 12px; margin-top: 4px;'>to continue to your Prime TechHub Dashboard</p>", unsafe_allow_html=True)


                    with st.container(border=True):
                        # FIX 1: clear_on_submit=False prevents inputs from vanishing on error
                        with st.form("pro_login", clear_on_submit=False): 
                            email = st.text_input("Email / Username")
                            password = st.text_input("Password", type="password")
                            btn_login = st.form_submit_button("SIGN IN", use_container_width=True)
                            
                            if btn_login:
                                # FIX 2: Security Fork - Check Admin First
                                admin_user = verify_admin(email, password) 
                                if admin_user:
                                    st.session_state['admin_logged_in'] = True
                                    st.rerun()
                                else:
                                    # If not admin, check customer
                                    customer = verify_customer(email, password)
                                    if customer:
                                        st.session_state['customer_logged_in'] = True
                                        st.session_state['current_customer'] = customer
                                        st.rerun()
                                    else:
                                        st.error("Account not found. Please check your credentials.")

                    st.markdown("<p style='text-align: center; font-weight: bold; font-size: 14px; margin-top: -5px; margin-bottom: 15px; color: #70757a;'>OR</p>", unsafe_allow_html=True)
                    
                    google_html = """
                    <style>
                        .google-btn-custom {
                            background-color: white;
                            color: #5f6368;
                            border: 1px solid #dadce0;
                            border-radius: 4px;
                            padding: 8px 20px;
                            font-size: 14px;
                            font-weight: 600;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            width: 100%;
                            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                            margin-bottom: 15px;
                            transition: background-color 0.2s ease;
                        }
                        /* This is the line that creates the grey toast shadow when hovered */
                            .google-btn-custom:hover {
                            background-color: #f1f3f4 !important; 
                        }
                    </style>
                    <a href="https://github.com/Aysha-Nur/Prime-TechHub#authentication-notice" target="_blank" style="text-decoration: none; color: inherit; width: 100%;">
                        <div class="google-btn-custom">
                            <img src="https://img.icons8.com/color/48/000000/google-logo.png" style="width: 18px; margin-right: 10px;"/>
                            Sign in with Google
                        </div>
                    </a>
                    """
                    st.markdown(google_html, unsafe_allow_html=True)
                
                    st.button("New to Prime TechHub? Create an account", on_click=lambda: st.session_state.update({"account_mode": "signup"}), use_container_width=True)
                    # --- BOTTOM RIGHT WATERMARK ---
                    st.markdown("""
                        <div style="position: fixed; bottom: 15px; right: 25px; color: #b0b0b0; font-size: 22px; font-weight: 600; letter-spacing: 0.5px; z-index: 100;">
                            Prime TechHub Account
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    # SURGICAL FIX: Converted h1 to a strictly sized h3
                    st.markdown("<h3 style='text-align: center; margin-bottom: 0px; font-size: 28px;'>Create Account</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; color: #5f6368; font-size: 13px; margin-top: 5px;'>Join Prime TechHub for a smarter home experience</p>", unsafe_allow_html=True)


                    with st.container(border=True):
                        # FIX 1: clear_on_submit=False prevents inputs from vanishing
                        with st.form("pro_signup", clear_on_submit=False):
                            name = st.text_input("Full Name")
                            email = st.text_input("Email Address")
                            password = st.text_input("Password", type="password")
                            btn_reg = st.form_submit_button("CREATE ACCOUNT", use_container_width=True)
                            
                            if btn_reg:
                                if not name or not email or not password:
                                    st.error("Please fill all fields to continue.")
                                else:
                                    if register_customer(name, email, password):
                                        st.session_state['customer_logged_in'] = True
                                        st.session_state['current_customer'] = verify_customer(email, password)
                                        st.rerun()
                                    else:
                                        st.error("This email is already registered.")
                    
                    
                    st.button("Already have an account? Log in", on_click=lambda: st.session_state.update({"account_mode": "login"}), use_container_width=True)
            
            # Show Customer Dashboard
            elif st.session_state['customer_logged_in'] and st.session_state['current_customer']:
                customer = st.session_state['current_customer']
                st.markdown(f"<h1>Hello, {customer['name'].split()[0]}! 👋</h1>", unsafe_allow_html=True)
                
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    c1.metric("Account Status", "Verified")
                    c2.metric("Membership", "Standard")
                    
                    st.divider()
                    st.write(f"📧 **Registered Email:** {customer['email']}")
                    
                    # --- DYNAMIC ORDER HISTORY ---                    
                    st.write("📦 **Recent Orders:**")
                    customer_orders = get_customer_orders(customer['id'])
                    
                    if customer_orders:
                        import pandas as pd
                        df_orders = pd.DataFrame(customer_orders, columns=["Product", "Price", "Date"])
                        st.dataframe(df_orders, use_container_width=True, hide_index=True)
                    else:
                        st.info("No orders placed yet. Time to start shopping!")

                
                if st.button("Sign Out", type="primary", use_container_width=True):
                    st.session_state['customer_logged_in'] = False
                    st.session_state['current_customer'] = None
                    st.rerun()
                    
            # Show Admin Route Notification
            elif st.session_state['admin_logged_in']:
                st.success("✅ Signed in as System Administrator.")
                st.info("Please use the '⚙️ Admin Dashboard' tab in the side menu to manage Prime TechHub.")
                if st.button("Sign Out", type="primary", use_container_width=True):
                    st.session_state['admin_logged_in'] = False
                    st.rerun()

if __name__ == "__main__":
    main()