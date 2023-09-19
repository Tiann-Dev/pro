import sqlite3
import secrets,os,sys
import main
import string,random

from datetime import datetime, timedelta
import database  # Import modul database di sini
from rich import print
from rich.console import Console
from rich import color
from rich.panel import Panel
from colorama import Fore, Style, init
from database import (
    create_connection,
    create_tables,
    login,
    register,
    update_password,
    get_user_id,
    create_session,
    delete_session,
    lock_account,
    is_account_locked,
    unlock_account,
    validate_password,
    get_registration_date,
    get_user_info,
    set_user_online_status,  
    get_online_users,  
    send_chat_message,  
    get_received_messages,  
    get_username_by_id,
    is_username_unique,
    store_api_key,
    create_admin_account,
    upgrade_user_to_premium
)

init(autoreset=True)
console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def display_logo():
    console.print(
        """
   _____ _             ____                 _ 
  / ____| |           / __ \               | |
 | |    | |__   __ _| |  | |_   _  ___  __| |
 | |    | '_ \ / _` | |  | | | | |/ _ \/ _` |
 | |____| | | | (_| | |__| | |_| |  __/ (_| |
  \_____|_| |_|\__,_|\____/ \__, |\___|\__,_|
                            __/ |           
                           |___/            
""",
        style="cyan",
    )

def is_administrator(connection, username):
    cursor = connection.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        return result[0] == 1
    return False

def generate_api_key():
    return secrets.token_urlsafe(16)

def get_choice():
    choice = input(Fore.YELLOW + "Pilihan Anda: ")
    return choice.strip()  # Remove leading/trailing whitespace

def admin_handle_locked_account(connection, username):
    if database.is_account_locked(connection, username):
        print(f"Akun {username} terkunci.")
        print("1. Buka Kunci Akun")
        print("2. Kembali")
        choice = input("Pilih tindakan: ")

        if choice == "1":
            database.unlock_account(connection, username)
            print(f"Akun {username} telah dibuka kunci.")
        elif choice == "2":
            pass  # Kembali ke menu admin
        else:
            print("Pilihan tidak valid.")
    else:
        print(f"Akun {username} tidak terkunci.")

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
        cursor.execute("UPDATE users SET is_premium = 1, premium_duration = ?, expiration_date = ? WHERE api_key = ?", (premium_duration, expiration_date, api_key))
        connection.commit()
        print(f"Pengguna dengan API key {api_key} telah diupgrade menjadi premium dengan durasi {premium_duration} hari.")
    else:
        print("API key tidak valid.")

# Fungsi untuk mengupgrade pengguna menjadi premium dengan durasi tertentu
from datetime import datetime, timedelta

def upgrade_user_to_premium(connection, api_key, premium_duration_in_days):
    cursor = connection.cursor()

    # Cek apakah pengguna dengan API key tertentu ada
    cursor.execute("SELECT id, username FROM users WHERE api_key = ?", (api_key,))
    result = cursor.fetchone()

    if result:
        user_id, username = result

        # Hitung tanggal kedaluwarsa berdasarkan durasi dalam hari
        current_time = datetime.now()
        expiration_date = current_time + timedelta(days=premium_duration_in_days)

        # Format tanggal kedaluwarsa dalam format "YYYY-MM-DD HH:MM:SS"
        formatted_expiration_date = expiration_date.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE users SET is_premium = 1, premium_duration = ?, expiration_date = ? WHERE id = ?", (premium_duration_in_days, formatted_expiration_date, user_id))
        connection.commit()
        print("[bold green]Upgrade berhasil![/bold green]")
        print(f"Pengguna dengan API key {api_key} (username: {username}) telah diupgrade menjadi premium dengan durasi {premium_duration_in_days} hari.")
        input("Tekan Enter untuk kembali ke menu utama...")
    else:
        print("[bold red]API key tidak valid.[/bold red]")
        input("Tekan Enter untuk kembali ke menu utama.")


def get_valid_integer_input(prompt):
    while True:
        user_input = input(prompt)
        if not user_input.isdigit():
            print("Input tidak valid. Harap masukkan angka bulat yang benar.")
        else:
            try:
                integer_value = int(user_input)
                if integer_value <= 0:
                    print("Angka harus lebih besar dari 0.")
                else:
                    return integer_value  # Mengembalikan nilai jika valid
            except ValueError:
                print("Terjadi kesalahan saat mengonversi input menjadi angka bulat.")

def admin_menu(connection):
    while True:
        clear_screen()
        display_logo()
        console.print("Menu Admin:")
        console.print("=" * 20)
        console.print("1. Upgrade Pengguna ke Premium")
        console.print("2. Kunci Akun Pengguna")
        console.print("3. Daftar Pengguna Aktif")  # Menambahkan pilihan "Daftar Pengguna Aktif"
        console.print("4. Daftar Pengguna Dikunci")  # Menambahkan pilihan "Daftar Pengguna Dikunci"
        console.print("5. Buka Kunci Akun Pengguna")
        console.print("6. Log Aktivitas Pengguna") 
        console.print("7. Reset Password Pengguna")
        console.print("8. Kembali ke Menu Utama")
        console.print("=" * 20)

        choice = input("Pilihan Anda: ")

        if choice == "1":
            # Panggil fungsi untuk mengupgrade pengguna ke premium
            api_key = input("Masukkan API Key pengguna yang akan di-upgrade: ")
            premium_duration_in_days = int(input("Masukkan durasi premium dalam hari: "))
            upgrade_user_to_premium(connection, api_key, premium_duration_in_days)
        elif choice == "2":
            # Panggil fungsi untuk mengkunci akun pengguna
            lock_user_account(connection)
        elif choice == "3":
            # Panggil fungsi untuk menampilkan daftar pengguna aktif
            view_user_list(connection)
        elif choice == "4":
            # Panggil fungsi untuk menampilkan daftar pengguna dikunci
            view_locked_users(connection)
        elif choice == "5":
            # Panggil fungsi untuk membuka kunci akun pengguna
            unlock_user_account(connection)
        elif choice == "6":
            view_all_user_activity_logs(connection)
            break
        elif choice == "7":
            # Panggil fungsi untuk reset kata sandi pengguna
            username = input("Masukkan username pengguna yang akan direset kata sandinya: ")
            reset_user_password(connection, username)
        elif choice == "8":
            break
        else:
            console.print("[bold red]Error: Pilihan tidak valid. Silakan pilih lagi.[/bold red]")
            input("Tekan Enter untuk melanjutkan...")

def view_user_list(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT username, id, is_premium, is_online FROM users")
    users = cursor.fetchall()

    clear_screen()
    display_logo()
    console.print("Daftar Pengguna:")
    console.print("=" * 60)

    active_users = []
    inactive_users = []

    for user in users:
        username, id, is_premium, is_active = user
        premium_status = "Premium" if is_premium else "Gratis"
        status = "Aktif" if is_active else "Nonaktif"
        user_info = f"🆔 {id}, 👤 {username}, 🌟 {premium_status}, 🟢 {status}"

        if is_active:
            active_users.append(user_info)
        else:
            inactive_users.append(user_info)

    if active_users:
        console.print("🟢 [bold green]Aktif[/bold green]")
        for user_info in active_users:
            console.print(user_info)
        console.print("=" * 60)

    if inactive_users:
        console.print("🔴 [bold red]Nonaktif[/bold red]")
        for user_info in inactive_users:
            console.print(user_info)
        console.print("=" * 60)

    input("Tekan Enter untuk kembali ke Menu Admin...")


def deactivate_user_account(connection):
    clear_screen()
    display_logo()
    console.print("Tutup Akun Pengguna")
    console.print("=" * 20)

    # Menampilkan daftar pengguna aktif
    view_user_list(connection)

    # Meminta input dari admin untuk memilih pengguna yang akan dinonaktifkan
    user_id_to_deactivate = input("Masukkan ID pengguna yang akan dinonaktifkan: ")

    # Periksa apakah ID pengguna valid
    if not user_id_to_deactivate.isdigit():
        console.print("[bold red]Error: Masukkan ID pengguna yang valid.[/bold red]")
        input("\nTekan Enter untuk kembali ke Menu Admin...")
        return

    user_id_to_deactivate = int(user_id_to_deactivate)

    # Periksa apakah ID pengguna ada dalam database
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id_to_deactivate,))
    result = cursor.fetchone()

    if not result:
        console.print("[bold red]Error: ID pengguna tidak ditemukan.[/bold red]")
        input("\nTekan Enter untuk kembali ke Menu Admin...")
        return

    # Nonaktifkan akun pengguna dengan mengubah status premium menjadi False
    cursor.execute("UPDATE users SET is_premium = 0 WHERE id = ?", (user_id_to_deactivate,))
    connection.commit()

    console.print("[bold green]Akun pengguna telah dinonaktifkan.[/bold green]")
    input("\nTekan Enter untuk kembali ke Menu Admin...")

# Fungsi untuk mengkunci akun pengguna
def lock_user_account(connection):
    clear_screen()
    display_logo()
    console.print("Kunci Akun Pengguna:")  # Mengganti "Tutup Akun Pengguna" menjadi "Kunci Akun Pengguna"
    console.print("=" * 20)
    username = input("Masukkan username pengguna yang akan dikunci akunnya: ")

    # Panggil fungsi untuk mengkunci akun pengguna dengan username tertentu
    result = lock_user(connection, username)  # Mengganti "deactivate_user" menjadi "lock_user"

    if result == True:
        console.print("[bold green]Akun pengguna telah dikunci.[/bold green]")
    else:
        console.print("[bold red]Error: Pengguna tidak ditemukan atau akun sudah dikunci.[/bold red]")

    input("Tekan Enter untuk kembali ke Menu Admin...")

# Fungsi untuk mengkunci akun pengguna dengan username tertentu
def lock_user(connection, username):
    cursor = connection.cursor()

    # Cek apakah pengguna dengan username tertentu ada
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()

    if user_id:
        # Kunci akun pengguna dengan mengubah status is_locked menjadi 1
        cursor.execute("UPDATE users SET is_locked = 1 WHERE username = ?", (username,))
        connection.commit()
        return True
    else:
        return False

def view_locked_users(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT username, id FROM users WHERE is_online = 0")
    locked_users = cursor.fetchall()

    clear_screen()
    display_logo()
    console.print("Daftar Pengguna Dikunci:")
    console.print("=" * 60)

    for user in locked_users:
        username, id = user
        user_info = f"🆔 {id}, 👤 {username}, 🔴 [bold red]Nonaktif[/bold red]"
        console.print(user_info)

    console.print("=" * 60)
    input("Tekan Enter untuk kembali ke Menu Admin...")

def unlock_user_account(connection):
    cursor = connection.cursor()

    try:
        user_id = int(input("Masukkan ID pengguna yang akan diaktifkan: "))

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if user:
            cursor.execute("UPDATE users SET is_online = 1 WHERE id = ?", (user_id,))
            connection.commit()
            console.print("Akun pengguna telah diaktifkan.")
        else:
            console.print("ID pengguna tidak ditemukan.")
    except ValueError:
        console.print("ID pengguna harus berupa angka.")

    input("Tekan Enter untuk kembali ke Menu Admin...")


def view_all_user_activity_logs(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, activity, timestamp FROM activity_log ORDER BY timestamp DESC")
    activity_logs = cursor.fetchall()

    clear_screen()
    display_logo()
    console.print("Log Aktivitas Pengguna:")
    console.print("=" * 27)
    
    if not activity_logs:
        console.print("Belum ada aktivitas pengguna.")
    else:
        for username, activity, timestamp in activity_logs:
            formatted_timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%d %B %Y, %H:%M:%S")
            console.print(f"👤 Pengguna: {username}")
            console.print(f"📅 Waktu: {formatted_timestamp}")
            console.print(f"📝 Aktivitas: {activity}")
            console.print("-" * 27)

    console.print("=" * 27)
    input("Tekan Enter untuk kembali ke Menu Admin...")

def reset_user_password(connection, username):
    cursor = connection.cursor()

    # Cek apakah pengguna dengan username tertentu ada
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    if result:
        # Generate kata sandi baru
        new_password = generate_random_password()

        # Update kata sandi pengguna dengan kata sandi baru
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hash_password(new_password), username))
        connection.commit()

        console.print("[bold green]Reset kata sandi berhasil![/bold green]")
        console.print(f"Kata sandi untuk pengguna {username} telah direset menjadi: {new_password}")
    else:
        console.print("[bold red]Pengguna tidak ditemukan.[/bold red]")

    input("Tekan Enter untuk kembali ke Menu Admin...")

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def hash_password(password):
    # Anda dapat menggunakan metode hash seperti hashlib untuk mengamankan kata sandi
    # Contoh sederhana: return hashlib.sha256(password.encode()).hexdigest()
    return password  # Gantilah dengan metode hash yang sesuai dengan kebutuhan Anda


# Fungsi utama
def main():
    try:
        # Buka koneksi ke database SQLite
        connection = sqlite3.connect("tianndev.db")

        # Masukkan API key yang ingin Anda gunakan untuk mengupgrade pengguna
        api_key = input("Masukkan API Key untuk pengguna yang ingin diupgrade: ")
        
        premium_duration = get_valid_integer_input("Masukkan durasi premium (dalam hari): ")
        print("Durasi premium yang dimasukkan adalah:", premium_duration)
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