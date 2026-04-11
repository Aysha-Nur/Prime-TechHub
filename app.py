import streamlit as st

# Configure the main page
st.set_page_config(page_title="Prime TechHub", layout="wide")

def main():
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", ["Storefront", "Admin Dashboard", "Cart"])

    # Main content area routing
    if page == "Storefront":
        st.title("Prime TechHub: Smart Home Devices")
        st.write("The product catalog will render here.")
        
    elif page == "Admin Dashboard":
        st.title("Inventory Management")
        st.warning("Secure Area: Login required.")
        
    elif page == "Cart":
        st.title("Shopping Cart")
        st.info("Your cart is currently empty.")

if __name__ == "__main__":
    main()