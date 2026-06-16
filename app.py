import streamlit as st
import sqlite3
import pandas as pd

from database import get_customer_orders, process_checkout

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
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", ["Storefront", "Cart", "My Account", "Admin Dashboard"])

 # 1. STOREFRONT PAGE
    if page == "Storefront":
        st.title("Prime TechHub: Smart Home Devices")
        
        # --- SEARCH & FILTER UI ---
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("🔍 Search products...", placeholder="Type a device name, brand, or keyword...")
        with col_filter:
            category_filter = st.selectbox(
                "📁 Filter by Category", 
                ["All", "Camera", "Lighting", "Smart Plug", "Hub/Controller", "Sensors", "Networking", "Audio"], 
                index=None, 
                placeholder="Search or select a category..."
            )

        # Fetch products from backend database
        products_df = get_products()
        
        if products_df.empty:
            st.warning("The inventory is currently empty. Please add items via the Admin Dashboard.")
        else:
            # Track if a search filter is actively being used
            is_searching = False

            # --- FIX 1: APPLY CATEGORY FILTER ---
            if category_filter is not None and category_filter != "All":
                products_df = products_df[products_df['category'] == category_filter]
                is_searching = True
            
            # --- FIX 2: ADVANCED FUZZY SEARCH (Ignores Case & Hyphens/Dashes) ---
            # Clean up the user query string by stripping whitespace and dashes
            clean_query = search_query.strip().lower().replace("-", "").replace(" ", "")
            
            if clean_query:
                is_searching = True
                # Create a temporary search column that also strips dashes and spaces from product names
                products_df['clean_name'] = products_df['name'].str.lower().str.replace("-", "", regex=False).str.replace(" ", "", regex=False)
                # Match the sanitized strings together
                products_df = products_df[products_df['clean_name'].str.contains(clean_query, na=False)]
            
            # --- HIDE OUT OF STOCK ITEMS ---
            products_df = products_df[products_df['stock'] > 0]

            # --- DYNAMIC NOT FOUND MESSAGE ---
            # The message ONLY displays if the dataset is empty AND the user actually typed a search query
            if products_df.empty and is_searching:
                st.warning("We're sorry, no such products found. Please try different keywords or browse our categories.")
            elif products_df.empty and not is_searching:
                st.info("No active devices available in the inventory right now.")
            else:
                if 'cart' not in st.session_state:
                    st.session_state['cart'] = []
                    
                # --- RENDER PRODUCTS ---
                for index, row in products_df.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.subheader(row['name'])
                        st.write(f"Category: {row['category']}")
                    with col2:
                        st.write(f"**Price:** {row['price']} PKR")
                        st.write(f"**Stock:** {row['stock']} units")
                    with col3:
                        if st.button("Add to Cart", key=f"add_{row['id']}"):
                            st.session_state['cart'].append({
                                "id": row['id'], 
                                "name": row['name'], 
                                "price": row['price']
                            })
                            st.toast(f"Added {row['name']} to cart!")
                    st.divider()

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
                        
    # 3. CART PAGE
    elif page == "Cart":
        st.title("🛒 Secure Checkout")
        
        # --- NEW: ENFORCE CUSTOMER LOGIN ---
        if not st.session_state.get('customer_logged_in') or st.session_state.get('current_customer') is None:
            st.warning("🔒 Please sign in to your Prime TechHub account to view your cart and checkout.")
            st.info("Navigate to the 'My Account' tab in the sidebar to log in or register.")
            
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

                            
    # 4. MY ACCOUNT PAGE
    elif page == "My Account":
        # Centering the UI
        _, col_mid, _ = st.columns([1, 2, 1])

        # --- Safely initialize ALL session states so the KeyError never happens ---
        if 'customer_logged_in' not in st.session_state:
            st.session_state['customer_logged_in'] = False
        if 'current_customer' not in st.session_state:
            st.session_state['current_customer'] = None
        if 'account_mode' not in st.session_state:
            st.session_state['account_mode'] = "login"

        with col_mid:
            # Check if logged in AND the customer data actually exists
            if not st.session_state['customer_logged_in'] or st.session_state['current_customer'] is None:
                if st.session_state['account_mode'] == "login":
                    st.markdown("<h1 style='text-align: center;'>Sign in</h1>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; color: #5f6368; font-size: 14px;'>to continue to your Prime TechHub Dashboard</p>", unsafe_allow_html=True)
                    st.write("")

                    with st.container(border=True):
                        with st.form("pro_login", clear_on_submit=True):
                            email = st.text_input("Email Address")
                            password = st.text_input("Password", type="password")
                            btn_login = st.form_submit_button("SIGN IN", use_container_width=True)
                            
                            if btn_login:
                                customer = verify_customer(email, password)
                                if customer:
                                    st.session_state['customer_logged_in'] = True
                                    st.session_state['current_customer'] = customer
                                    st.rerun()
                                else:
                                    st.error("Account not found. Please check your details.")

                        st.markdown("<p style='text-align: center; font-weight: bold; font-size: 14px; margin-top: -5px; margin-bottom: 15px; color: #70757a;'>OR</p>", unsafe_allow_html=True)
                        
                        google_html = """
                        <a href="https://github.com/Aysha-Nur/Prime-TechHub#authentication-notice" target="_blank" style="text-decoration: none; color: inherit; width: 100%;">
                            <div style="background-color: white; color: #5f6368; border: 1px solid #dadce0; border-radius: 4px; padding: 8px 20px; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.05); margin-bottom: 15px;">
                                <img src="https://img.icons8.com/color/48/000000/google-logo.png" style="width: 18px; margin-right: 10px;"/>
                                Sign in with Google
                            </div>
                        </a>
                        """
                        st.markdown(google_html, unsafe_allow_html=True)
                    
                    # --- Added guaranteed spacing below the container ---
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.button("New to Prime TechHub? Create an account", on_click=lambda: st.session_state.update({"account_mode": "signup"}), use_container_width=True)

                else:
                    st.markdown("<h1 style='text-align: center;'>Create Account</h1>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; color: #5f6368; font-size: 14px;'>Join Prime TechHub for a smarter home experience</p>", unsafe_allow_html=True)
                    st.write("")

                    with st.container(border=True):
                        with st.form("pro_signup", clear_on_submit=True):
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
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.button("Already have an account? Log in", on_click=lambda: st.session_state.update({"account_mode": "login"}), use_container_width=True)
            
            else:
                # --- PROFESSIONAL LOGGED-IN DASHBOARD VIEW ---
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
                
                st.write("")
                if st.button("Sign Out", type="primary", use_container_width=True):
                    st.session_state['customer_logged_in'] = False
                    st.session_state['current_customer'] = None
                    st.rerun()

if __name__ == "__main__":
    main()