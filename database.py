import sqlite3
import pandas as pd
import streamlit as st   
def init_db():

    conn = sqlite3.connect('data/techhub.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)''')

    
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL, price REAL NOT NULL, stock INTEGER NOT NULL, description TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER, product_name TEXT NOT NULL, price REAL NOT NULL, sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id))''')
    
        
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:

        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")


    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        professional_products = [
            ("Aura Smart Bulb (RGB)", "Lighting", 3500.00, 50, "16 million colors, voice-activated."),
            ("Acoustic Echo Smart Speaker", "Audio", 12000.00, 30, "High-fidelity audio with built-in voice assistant."),
            ("AquaLeak Smart Sensor", "Sensors", 2500.00, 100, "Instant phone alerts for water leaks."),
            ("BioMetric Smart Lock Pro", "Security", 45000.00, 15, "Fingerprint, passcode, and app unlocking."),
            ("Camera - PrimeVision 4K", "Camera", 18500.00, 25, "Ultra HD indoor/outdoor security camera with night vision."),
            ("Doorbell Cam Pro", "Camera", 22000.00, 20, "Two-way audio, motion detection, and HD video."),
            ("EnergySync Power Strip", "Smart Plug", 6500.00, 40, "Independently control 4 outlets via Wi-Fi."),
            ("Hub - Nexus Home Controller", "Hub/Controller", 28000.00, 10, "The brain of your smart home. Zigbee and Z-Wave compatible."),
            ("Lumina LED Strip 5m", "Lighting", 4200.00, 60, "Syncs with music and TV colors."),
            ("MotionDetect Pro", "Sensors", 3000.00, 80, "Triggers lights and alarms instantly on movement."),
            ("MeshNet Wi-Fi 6 Router", "Networking", 35000.00, 12, "Eliminate dead zones with Gigabit speeds."),
            ("SoundBar Connect", "Audio", 25000.00, 15, "Cinematic smart audio for your living room."),
            ("ThermoSmart Thermostat", "Sensors", 32000.00, 18, "Learns your habits to save energy and optimize temperature."),
            ("VoltGuard Wi-Fi Plug", "Smart Plug", 2000.00, 100, "Turn any standard appliance into a smart device."),
            ("Window/Door Contact Sensor", "Sensors", 1800.00, 120, "Alerts you if a window or door is left open.")
        ]
              
        for prod in professional_products:

            cursor.execute("INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)", (prod[0], prod[1], prod[2], prod[3], prod[4]))
        print("Professional inventory loaded successfully!")

    conn.commit()
    conn.close()
    print("Database built successfully.")

def verify_admin(username, password):
    conn = sqlite3.connect('data/techhub.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username=? AND password=? AND role='admin'", (username, password))
    admin = cursor.fetchone()
    conn.close()
    if admin: return {"id": admin[0], "username": admin[1], "role": admin[2]}
    return None

def register_customer(name, email, password):
    conn = sqlite3.connect('data/techhub.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO customers (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally: conn.close()
    return success

def verify_customer(email, password):
    conn = sqlite3.connect('data/techhub.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM customers WHERE email=? AND password=?", (email, password))
    customer = cursor.fetchone()
    conn.close()
    if customer: return {"id": customer[0], "name": customer[1], "email": customer[2]}
    return None

@st.cache_data(ttl=60, show_spinner=False)
def get_products():
    conn = sqlite3.connect('data/techhub.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return df


def get_customer_orders(customer_id):

    conn = sqlite3.connect('data/techhub.db')
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, price, sale_date FROM orders WHERE customer_id=?", (customer_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders

def process_checkout(cart_items, customer_id):

    conn = sqlite3.connect('data/techhub.db')
    cursor = conn.cursor()
    success = False
    try:
        for item in cart_items:
            cursor.execute("INSERT INTO orders (customer_id, product_name, price) VALUES (?, ?, ?)", (customer_id, item['name'], item['price']))
            cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (item['id'],))

        conn.commit()
        success = True
    except Exception as e:
        print(f"Checkout Error: {e}")
        conn.rollback()
    finally: conn.close()
    return success

def update_customer_password(customer_id, current_password, new_password):
    """
    Verifies current password then updates to new one.
    Returns: 'success' | 'wrong_password' | 'error'
    """
    conn   = sqlite3.connect('data/techhub.db')
    cursor = conn.cursor()
    try:
        # Verify current password belongs to this customer
        cursor.execute(
            "SELECT id FROM customers WHERE id = ? AND password = ?",
            (customer_id, current_password)
        )
        if not cursor.fetchone():
            return 'wrong_password'

        # Update to new password
        cursor.execute(
            "UPDATE customers SET password = ? WHERE id = ?",
            (new_password, customer_id)
        )
        conn.commit()
        return 'success'
    except Exception as e:
        print(f"Password update error: {e}")
        conn.rollback()
        return 'error'
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()