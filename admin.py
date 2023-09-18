import sqlite3
import secrets
from datetime import datetime, timedelta

# Fungsi untuk mengupgrade pengguna menjadi premium dengan durasi tertentu
def upgrade_user_to_premium(connection, api_key, premium_duration):
    cursor = connection.cursor()

    # Cek apakah pengguna dengan API key tertentu ada
    cursor.execute("SELECT username FROM users WHERE api_key = ?", (api_key,))
    result = cursor.fetchone()

    if result:
        username = result[0]

        # Lakukan upgrade ke premium
        expiration_date = (datetime.now() + timedelta(days=premium_duration)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE users SET is_premium = 1, premium_duration = ? WHERE api_key = ?", (premium_duration, api_key))
        connection.commit()
        print(f"Pengguna dengan API key {api_key} telah diupgrade menjadi premium dengan durasi {premium_duration} hari.")
    else:
        print("API key tidak valid.")


# Fungsi utama
def main():
    try:
        # Buka koneksi ke database SQLite
        connection = sqlite3.connect("tianndev.db")

        # Masukkan API key yang ingin Anda gunakan untuk mengupgrade pengguna
        api_key = input("Masukkan API Key untuk pengguna yang ingin diupgrade: ")
        
        # Masukkan berapa lama masa aktif premiumnya (dalam hari)
        premium_duration = int(input("Masukkan durasi masa aktif premium (dalam hari): "))

        # Panggil fungsi untuk mengupgrade pengguna menjadi premium
        upgrade_user_to_premium(connection, api_key, premium_duration)

    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        # Tutup koneksi database
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
