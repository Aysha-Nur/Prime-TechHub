import sqlite3

def init_db():
    # Connect to SQLite (creates the file if it doesn't exist)
    conn = sqlite3.connect('techhub.db')
    cursor = conn.cursor()

    # Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Create Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            description TEXT
        )
    ''')
    
    # Create Orders Table for Sales Logging
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER, 
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id) 
        )
    ''')
    
    # Insert a default Admin user if the table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Note: Plaintext password is fine for local viva defense
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")

    # --- NEW: Auto-Populate Professional Inventory ---
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
        
        # Insert them all into the database including descriptions
        for prod in professional_products:
            cursor.execute("INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)", 
                           (prod[0], prod[1], prod[2], prod[3], prod[4]))
        print("Professional inventory loaded successfully!")

    conn.commit()
    conn.close()
    print("Database built successfully.")


def get_customer_orders(customer_id):
    """Fetches the order history for a specific logged-in customer."""
    import sqlite3
    conn = sqlite3.connect('techhub.db')
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, price, sale_date FROM orders WHERE customer_id=?", (customer_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders

def process_checkout(cart_items, customer_id):
    """Processes the cart, logs the order with the customer ID, and deducts stock."""
    import sqlite3
    conn = sqlite3.connect('techhub.db')
    cursor = conn.cursor()
    success = False
    try:
        for item in cart_items:
            # 1. Insert the order with the specific customer_id
            cursor.execute("INSERT INTO orders (customer_id, product_name, price) VALUES (?, ?, ?)", 
                           (customer_id, item['name'], item['price']))
            # 2. Deduct 1 from the product stock
            cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (item['id'],))
        
        conn.commit()
        success = True
    except Exception as e:
        print(f"Checkout Error: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    return success

if __name__ == '__main__':
    init_db()