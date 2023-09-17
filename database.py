import sqlite3
from datetime import datetime, timedelta


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("tianndev.db")
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            registration_date TEXT NOT NULL,
            is_premium INTEGER DEFAULT 0,
            expiration_date TEXT,
            is_locked INTEGER DEFAULT 0,
            email TEXT,
            is_online INTEGER DEFAULT 0  -- Tambahkan kolom is_online
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            expiration_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_username ON users (username)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_session_token ON sessions (session_token)
    """)

    connection.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            sender_username TEXT NOT NULL,
            receiver_username TEXT NOT NULL,
            message TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    """)

    connection.commit()


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

def register(connection, username, password):
    cursor = connection.cursor()

    if len(username) < 1:
        return "Nama pengguna terlalu pendek (minimal 4 karakter)."
    if len(password) < 1:
        return "Kata sandi terlalu pendek (minimal 6 karakter)."
    if not is_username_unique(connection, username):
        return "Nama pengguna sudah ada, silakan pilih yang lain."

    try:
        expiration_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users (username, password, registration_date, is_premium, expiration_date) VALUES (?, ?, ?, ?, ?)",
                       (username, password, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, expiration_date))
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
    cursor.execute("SELECT id, username, password, registration_date, email, is_premium FROM users WHERE username = ?", (username,))
    user_info = cursor.fetchone()
    return user_info


def create_session(conn, user_id, session_token, expiration_time):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (user_id, session_token, expiration_time) VALUES (?, ?, ?)",
                   (user_id, session_token, expiration_time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

def delete_session(conn, session_token):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
    conn.commit()

def lock_account(connection, username):
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET is_locked = 1 WHERE username = ?", (username,))
    connection.commit()

def is_account_locked(connection, username):
    cursor = connection.cursor()
    cursor.execute("SELECT is_locked FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if result is not None:
        locked = result[0]
        print(f"Account locked status for {username}: {locked}")
        return locked == 1
    else:
        print(f"No account found with username: {username}")
        return False



def unlock_account(connection, username):
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET is_locked = 0 WHERE username = ?", (username,))
    connection.commit()

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

def upgrade_to_premium(connection, username):
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET is_premium = 1 WHERE username = ?", (username,))
    connection.commit()

def downgrade_to_free(connection, username):
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET is_premium = 0 WHERE username = ?", (username,))
    connection.commit()

# database.py

# ...

def set_user_online_status(connection, username, is_online):
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET is_online = ? WHERE username = ?", (is_online, username))
    connection.commit()

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
