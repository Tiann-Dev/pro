import sqlite3
from datetime import datetime, timedelta
import secrets
import string

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("tianndev.db")
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(connection):
    cursor = connection.cursor()

    # Create the 'users' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            email TEXT,
            is_premium INTEGER DEFAULT 0,
            expiration_date DATETIME,
            is_admin INTEGER DEFAULT 0,
            is_locked INTEGER DEFAULT 0,
            is_online INTEGER DEFAULT 0,
            api_key TEXT,
            premium_duration TEXT DEFAULT '0'
        )
    ''')

    # Create the 'sessions' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT NOT NULL UNIQUE,
            expiration_time DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create the 'api_keys' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            api_key TEXT NOT NULL UNIQUE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_username TEXT,
            receiver_username TEXT,
            message TEXT,
            message_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        activity TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS BugReports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        description TEXT,
        report_date DATETIME,
        status TEXT
    )
""")

    connection.commit()


def log_user_activity(user_id, activity):
    connection = sqlite3.connect("tianndev.db")
    cursor = connection.cursor()

    # Menyisipkan log aktivitas
    cursor.execute("INSERT INTO activity_log (user_id, activity) VALUES (?, ?)", (user_id, activity))

    # Commit perubahan dan menutup koneksi
    connection.commit()
    connection.close()


def get_chat_messages(connection, sender_username, receiver_username):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT sender_username, receiver_username, message, timestamp
        FROM chat
        WHERE (sender_username = ? AND receiver_username = ?)
           OR (sender_username = ? AND receiver_username = ?)
        ORDER BY timestamp
    """, (sender_username, receiver_username, receiver_username, sender_username))
    messages = cursor.fetchall()
    return messages

def login(conn, username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    return user

def is_username_unique(connection, username):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
    return cursor.fetchone()[0] == 0

def generate_api_key(username):
    api_key_prefix = f"{username}_"
    remaining_length = 16 - len(api_key_prefix)
    characters = string.ascii_letters + string.digits
    api_key_suffix = ''.join(secrets.choice(characters) for _ in range(remaining_length))
    api_key = api_key_prefix + api_key_suffix
    return api_key

# Function to store an API key in the database
def store_api_key(api_key):
    connection = sqlite3.connect("tianndev.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO api_keys (api_key) VALUES (?)", (api_key,))
    connection.commit()
    connection.close()

def register(connection, username, password, is_premium=False, premium_duration=None):
    cursor = connection.cursor()

    # Periksa panjang nama pengguna dan kata sandi
    if len(username) < 1:
        return "Nama pengguna terlalu pendek (minimal 4 karakter)."
    if len(password) < 1:
        return "Kata sandi terlalu pendek (minimal 6 karakter)."

    # Periksa apakah nama pengguna sudah digunakan
    if not is_username_unique(connection, username):
        return "Nama pengguna sudah ada, silakan pilih yang lain."

    # Hasilkan API key secara otomatis
    api_key = generate_api_key(username)   # Menghasilkan API key sepanjang 32 karakter

    # Tanggal kedaluwarsa untuk akun premium
    expiration_date = None
    if is_premium and premium_duration is not None:
        expiration_date = (datetime.now() + timedelta(days=premium_duration)).strftime("%Y-%m-%d %H:%M:%S")

    # Periksa apakah nama pengguna adalah "tian" dan tetapkan status admin jika benar
    if username.lower() == "tian":
        is_admin = 1
    else:
        is_admin = 0

    try:
        # Sisipkan data pengguna ke database, termasuk API key dan status admin
        cursor.execute("INSERT INTO users (username, password, registration_date, is_premium, expiration_date, api_key, is_admin) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (username, password, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), is_premium, expiration_date, api_key, is_admin))
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return "Terjadi kesalahan saat mendaftar."

def update_password(conn, username, new_password):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(e)
        return False

def update_email(connection, username, new_email):
    cursor = connection.cursor()

    cursor.execute("UPDATE users SET email = ? WHERE username = ?", (new_email, username))
    connection.commit()
    return True

def get_user_id(connection, username):
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    if user_id:
        return user_id[0]
    else:
        return None

def get_user_info(connection, username):
    cursor = connection.cursor()
    cursor.execute("SELECT id, username, password, registration_date, email, is_premium, premium_duration, api_key, is_online FROM users WHERE username = ?", (username,))
    user_info = cursor.fetchone()
    return user_info



def create_session(conn, user_id, session_token, expiration_time):
    try:
        cursor = conn.cursor()
        
        # Begin a transaction
        cursor.execute("BEGIN")

        cursor.execute("INSERT INTO sessions (user_id, session_token, expiration_time) VALUES (?, ?, ?)",
                       (user_id, session_token, expiration_time.strftime("%Y-%m-%d %H:%M:%S")))

        # Commit the transaction to release the lock
        conn.commit()

    except sqlite3.Error as e:
        # Roll back the transaction on error
        conn.rollback()
        print("SQLite error:", e)
    finally:
        cursor.close()

def delete_session(conn, session_token):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
    conn.commit()

def lock_account(connection, username):
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET is_locked = 1 WHERE username = ?", (username,))
    connection.commit()

def unlock_account(connection, username):
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET is_locked = 0 WHERE username = ?", (username,))
    connection.commit()

def is_account_locked(connection, username):
    cursor = connection.cursor()
    cursor.execute("SELECT is_locked FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result and result[0] == 1:
        return True
    else:
        return False

def validate_password(connection, username, password):
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    stored_password = cursor.fetchone()
    if stored_password is not None:
        stored_password = stored_password[0]
        return stored_password == password
    else:
        return False


def get_registration_date(connection, username):
    cursor = connection.cursor()
    cursor.execute("SELECT registration_date FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def upgrade_user_to_premium(connection, username, premium_duration):
    cursor = connection.cursor()
    expiration_date = (datetime.now() + timedelta(days=premium_duration)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE users SET is_premium = 1, expiration_date = ? WHERE username = ?", (expiration_date, username))
    connection.commit()



def set_user_online_status(connection, username, is_online):
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET is_online = ? WHERE username = ?", (is_online, username))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print("Error setting user online status:", e)
        return False


def get_online_users(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users WHERE is_online = 1")
    online_users = cursor.fetchall()
    return [user[0] for user in online_users]


def send_chat_message(connection, sender_username, receiver_username, message):
    cursor = connection.cursor()
    sender_id = get_user_id(connection, sender_username)
    receiver_id = get_user_id(connection, receiver_username)
    
    if sender_id and receiver_id:
        cursor.execute("INSERT INTO chat_messages (sender_id, receiver_id, message, timestamp) VALUES (?, ?, ?, ?)",
                       (sender_id, receiver_id, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        connection.commit()
        return True
    else:
        return False

def get_received_messages(connection, receiver_username):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT sender_username, message, timestamp
        FROM chat_messages
        WHERE receiver_username = ?
        ORDER BY timestamp ASC
    """, (receiver_username,))
    received_messages = cursor.fetchall()
    return received_messages

def get_username_by_id(connection, user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def get_chat_messages(connection, sender_username, receiver_username):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT sender_username, receiver_username, message, timestamp
        FROM chat_messages
        WHERE (sender_username = ? AND receiver_username = ?)
           OR (sender_username = ? AND receiver_username = ?)
        ORDER BY timestamp
    """, (sender_username, receiver_username, receiver_username, sender_username))
    messages = cursor.fetchall()
    return messages

# ...

def send_chat_message(connection, sender_username, receiver_username, message):
    cursor = connection.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO chat_messages (sender_username, receiver_username, message, timestamp) VALUES (?, ?, ?, ?)",
                   (sender_username, receiver_username, message, timestamp))
    connection.commit()


def get_received_messages(connection, receiver_username):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT sender_username, message_text, timestamp
        FROM chat_messages
        WHERE receiver_username = ?
        ORDER BY timestamp ASC
    """, (receiver_username,))
    received_messages = cursor.fetchall()
    return received_messages

def create_admin_account(connection, username, password):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username, password, registration_date, is_premium, api_key, premium_duration) VALUES (?, ?, datetime('now'), 1, 'T_Admin', 30)", (username, password))
    connection.commit()

def update_email(connection, username, new_email):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE users SET email = ? WHERE username = ?", (new_email, username))
        connection.commit()
        return True
    except sqlite3.Error as e:
        print("Error updating email:", e)
        return False
