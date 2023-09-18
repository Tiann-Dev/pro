import sqlite3
import secrets,os,sys
from datetime import datetime, timedelta
import database  # Import modul database di sini
from rich import print
from rich.console import Console
from rich import color
from rich.panel import Panel
from colorama import Fore, Style, init
import main
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
        console.print("[bold green]Upgrade berhasil![/bold green]")
        console.print(f"Pengguna dengan API key {api_key} telah diupgrade menjadi premium dengan durasi {premium_duration} hari.")
        input("Tekan Enter untuk kembali ke menu utama...")
    else:
        console.print("[bold red]API key tidak valid.[/bold red]")
        input("Tekan Enter untuk kembali ke menu utama.")



def admin_menu(connection):
    while True:
        clear_screen()
        display_logo()
        console.print("[green]Menu Admin:[/green]")
        console.print("[yellow]===================================")
        console.print("[yellow]1. Upgrade Pengguna ke Premium")
        console.print("[yellow]2. Handle Akun Terkunci")
        console.print("[yellow]3. Kembali ke Menu Utama")
        console.print("[yellow]===================================")
        admin_choice = get_choice()

        if admin_choice == "1":
            api_key = input("Masukkan API Key untuk pengguna yang ingin diupgrade: ")
            premium_duration = int(input("Masukkan durasi premium (dalam hari): "))  # Meminta durasi dari admin
            upgrade_user_to_premium(connection, api_key, premium_duration)
        elif admin_choice == "2":
            username = input("Masukkan username akun yang ingin dihandle: ")
            admin_handle_locked_account(connection, username)
            input("Tekan Enter untuk kembali ke menu Admin...")
        elif admin_choice == "3":
            break
        else:
            print("Pilihan tidak valid.")

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