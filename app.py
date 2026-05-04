import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Prime TechHub", layout="wide")

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

def process_checkout(cart_items):
    """Deducts purchased items from stock AND logs the sale in the orders table."""
    conn = sqlite3.connect('techhub.db')
    cursor = conn.cursor()
    
    try:
        for item in cart_items:
            # 1. Deduct the stock
            cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (item['id'],))
            # 2. Log the sale into the orders table
            cursor.execute("INSERT INTO orders (product_name, price) VALUES (?, ?)", (item['name'], item['price']))
            
        conn.commit()
        success = True
    except Exception as e:
        conn.rollback() 
        success = False
        
    conn.close()
    return success 

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
        
        # --- NEW: SEARCH & FILTER UI ---
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("🔍 Search products...", "")
        with col_filter:
            category_filter = st.selectbox("📂 Filter by Category", ["All", "Camera", "Lighting", "Smart Plug", "Hub/Controller", "Sensors", "Networking", "Audio"])

        products_df = get_products()
        
        if products_df.empty:
            st.warning("The inventory is currently empty. Please add items via the Admin Dashboard.")
        else:
            # --- NEW: APPLY SEARCH AND FILTER LOGIC ---
            if category_filter != "All":
                products_df = products_df[products_df['category'] == category_filter]
            
            if search_query:
                # Filters by name, ignoring case sensitivity
                products_df = products_df[products_df['name'].str.contains(search_query, case=False, na=False)]
            
            # --- NEW: HIDE OUT OF STOCK ITEMS ---
            products_df = products_df[products_df['stock'] > 0]

            if products_df.empty:
                st.info("No products match your search or items are out of stock.")
            else:
                if 'cart' not in st.session_state:
                    st.session_state['cart'] = []
                    
                for index, row in products_df.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.subheader(row['name'])
                        st.write(f"Category: {row['category']} | {row['description']}")
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
        
        if 'receipt' in st.session_state:
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
                c_name = st.text_input("Full Name")
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
                        if process_checkout(st.session_state['cart']):
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
        # Initialize session state variables
        if 'customer_logged_in' not in st.session_state:
            st.session_state['customer_logged_in'] = False
        if 'account_mode' not in st.session_state:
            st.session_state['account_mode'] = "login" # Start on login mode

        if not st.session_state['customer_logged_in']:
            # Center the login box like a real web portal
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.session_state['account_mode'] == "login":
                    st.header("Sign in")
                    st.write("Use your Prime TechHub Account")
                    
                    with st.form("unified_login", clear_on_submit=True):
                        email = st.text_input("Email")
                        password = st.text_input("Password", type="password")
                        submit = st.form_submit_button("Next")
                        
                        if submit:
                            customer = verify_customer(email, password)
                            if customer:
                                msg = st.empty()
                                msg.success("Logged in successfully!")
                                import time
                                time.sleep(1.2)
                                msg.empty()
                                st.session_state['customer_logged_in'] = True
                                st.session_state['current_customer'] = customer
                                st.rerun()
                            else:
                                st.error("Invalid email or password.")
                    
                    st.write("--- OR ---")
                    if st.button("🌐 Continue with Google", use_container_width=True):
                        st.info("Google Integration is in Sandbox mode. Please use email/password for this demo.")
                    
                    st.write("")
                    if st.button("Create account"):
                        st.session_state['account_mode'] = "signup"
                        st.rerun()

                else:
                    st.header("Create Account")
                    st.write("Join the Prime TechHub community")
                    
                    with st.form("unified_signup", clear_on_submit=True):
                        name = st.text_input("Full Name")
                        email = st.text_input("Email Address")
                        password = st.text_input("Password", type="password")
                        submit = st.form_submit_button("Register")
                        
                        if submit:
                            if not name or not email or not password:
                                st.error("All fields are required.")
                            else:
                                if register_customer(name, email, password):
                                    msg = st.empty()
                                    msg.success("Account created!")
                                    import time
                                    time.sleep(1.2)
                                    msg.empty()
                                    # Auto-login
                                    customer = verify_customer(email, password)
                                    st.session_state['customer_logged_in'] = True
                                    st.session_state['current_customer'] = customer
                                    st.rerun()
                                else:
                                    st.error("Email already registered.")
                    
                    st.write("")
                    if st.button("Already have an account? Sign in"):
                        st.session_state['account_mode'] = "login"
                        st.rerun()
        else:
            # Dashboard View
            customer = st.session_state['current_customer']
            st.subheader(f"Welcome, {customer['name']}")
            
            # Simple Dashboard UI
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**Profile Details**\n\nEmail: {customer['email']}")
            with c2:
                st.success(f"**Account Status**\n\nVerified Customer ✅")
            
            st.divider()
            if st.button("Sign out"):
                st.session_state['customer_logged_in'] = False
                del st.session_state['current_customer']
                st.rerun()

if __name__ == "__main__":
    main()