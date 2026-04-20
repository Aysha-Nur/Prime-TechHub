import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Prime TechHub", layout="wide")

# --- DATABASE HELPER FUNCTIONS ---
def get_products():
    """Reads all products from the database."""
    conn = sqlite3.connect('techhub.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return df

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
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", ["Storefront", "Admin Dashboard", "Cart"])

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
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                if verify_login(username, password):
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            st.success("Logged in successfully.")
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                st.rerun()
            
            # Create two tabs for the Admin
            tab1, tab2 = st.tabs(["Add New Product", "Sales Ledger"])
            
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
                    
                    # Calculate and display total revenue
                    total_revenue = orders_df['price'].sum()
                    st.metric(label="Total Revenue (PKR)", value=f"{total_revenue:,.2f}")

    # 3. CART PAGE
    elif page == "Cart":
        st.title("Shopping Cart")
        
        if 'cart' not in st.session_state or len(st.session_state['cart']) == 0:
            st.info("Your cart is currently empty.")
        else:
            total_price = 0
            for item in st.session_state['cart']:
                st.write(f"- {item['name']} : {item['price']} PKR")
                total_price += item['price']
                
            st.divider()
            st.subheader(f"Total: {total_price} PKR")
            
            if st.button("Proceed to Checkout"):
                if process_checkout(st.session_state['cart']):
                    st.success("Payment successful! Stock has been deducted.")
                    st.session_state['cart'] = [] # Empty the cart after purchase
                    st.rerun() # Refresh the screen
                else:
                    st.error("Checkout failed. Database error.")

if __name__ == "__main__":
    main()