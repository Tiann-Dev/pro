
from rich import print
from rich.console import Console
from rich import color
from rich.panel import Panel
from colorama import Fore, Style, init
import secrets
import admin


import sqlite3
import os
import random
import string
import time
from datetime import datetime, timedelta
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

# Initialize colorama
init(autoreset=True)
console = Console()

def create_connection(database_file):
    return sqlite3.connect(database_file)

def generate_api_key():
    # Generate a random API key
    api_key_length = 32
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(api_key_length))

def store_api_key(user_id, api_key):
    # Store the API key in the database
    cursor = connection.cursor()
    cursor.execute("INSERT INTO api_keys (user_id, api_key) VALUES (?, ?)", (user_id, api_key))
    connection.commit()

def is_administrator(connection, username):
    # Check if the user is an administrator (You need to implement this)
    cursor = connection.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result and result[0] == 1

def admin_menu(connection):
    if username == "tian":
        while True:
            clear_screen()
            display_logo()
            console.print("[green]Menu Admin:[/green]")
            console.print("[yellow]===================================")
            console.print("[yellow]1. Upgrade Pengguna ke Premium")
            console.print("[yellow]2. Kembali ke Menu Utama")
            console.print("[yellow]===================================")
            admin_choice = get_choice()

            if admin_choice == "1":
                api_key = input("Masukkan API Key untuk pengguna yang ingin diupgrade: ")
                premium_duration = int(input("Masukkan durasi premium (dalam hari): "))
                admin.upgrade_user_to_premium(connection, api_key, premium_duration)
                input("Tekan Enter untuk kembali ke menu Admin...")
            elif admin_choice == "2":
                main_menu(connection, username, session_token)



def is_user_exists(connection, username):
    # Check if the user exists in the database
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result and result[0] > 0

def is_user_premium(connection, username):
    # Check if the user is already premium
    cursor = connection.cursor()
    cursor.execute("SELECT is_premium FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result and result[0] == 1

def admin_upgrade_to_premium(connection, admin_username, target_username):
    # Check if the admin user is indeed an administrator
    if not is_administrator(connection, admin_username):
        console.print("[bold red]Anda tidak memiliki hak administrator.[/bold red]")
        input("Tekan Enter untuk kembali ke menu utama...")
        return

    # Check if the target user exists
    if not is_user_exists(connection, target_username):
        console.print("[bold red]Pengguna dengan nama ini tidak ditemukan.[/bold red]")
        input("Tekan Enter untuk kembali ke menu utama...")
        return

    # Check if the target user is already premium
    if is_user_premium(connection, target_username):
        console.print("[bold red]Pengguna ini sudah merupakan pengguna premium.[/bold red]")
        input("Tekan Enter untuk kembali ke menu utama...")
        return

    # Generate a new API key
    api_key = generate_api_key()

    # Upgrade the target user to premium and store the API key
    user_id = get_user_id(connection, target_username)  # Implement get_user_id function
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET is_premium = 1 WHERE id = ?", (user_id,))
    connection.commit()
    store_api_key(user_id, api_key)

    console.print("[bold green]Upgrade berhasil![/bold green]")
    console.print(f"[yellow]API Key baru untuk pengguna {target_username}:[/yellow] {api_key}")
    input("Tekan Enter untuk kembali ke menu utama...")

def logout(connection, session_token):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
    connection.commit()
    
    # Set user status as offline
    set_user_online_status(connection, username, False)  
    return None, None

# Fungsi untuk memeriksa apakah sesi masih berlaku
def is_session_valid(connection, session_token):
    cursor = connection.cursor()

    # Periksa apakah sesi ada di database
    cursor.execute("SELECT expiration_time FROM sessions WHERE session_token = ?", (session_token,))
    expiration_date_str = cursor.fetchone()

    if expiration_date_str:
        expiration_date = datetime.strptime(expiration_date_str[0], "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()

        # Periksa apakah sesi masih berlaku
        if current_time < expiration_date:
            return True

    return False


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


def input_username():
    return input(Fore.YELLOW + "Username: ")


def input_password():
    return input(Fore.YELLOW + "Password: ")

def get_choice():
    choice = input(Fore.YELLOW + "Pilihan Anda: ")
    return choice.strip()  # Remove leading/trailing whitespace


def display_menu():
    clear_screen()
    display_logo()
    console.print("[green]Menu:")
    console.print("[yellow]1. Login")
    console.print("[yellow]2. Daftar")
    console.print("[yellow]3. Keluar")

def view_profile(connection, username, session_token):
    user_info = get_user_info(connection, username)
    if user_info:
        stored_user_id, stored_username, stored_password, stored_registration_date, stored_email, is_premium, premium_duration, api_key, is_online = user_info

        clear_screen()
        display_logo()
        print("[bold green]Profil Pengguna:[/bold green]")
        print(f"[yellow]Nomor Seri:[/yellow] {stored_user_id}")
        print(f"[yellow]Username:[/yellow] {stored_username}")
        print(f"[yellow]Password:[/yellow] {stored_password}")
        print(f"[yellow]Tanggal Pendaftaran:[/yellow] {stored_registration_date}")
        print(f"[yellow]Email:[/yellow] {stored_email if stored_email else 'None'}")
        print(f"[yellow]Status Premium:[/yellow] {'Premium' if is_premium else 'Gratis'}")
        print(f"[yellow]Status Online:[/yellow] {'Online' if is_online else 'Offline'}")
        print(f"[yellow]Durasi Premium:[/yellow] {premium_duration} hari")
        print(f"[yellow]API Key:[/yellow] {api_key if api_key else 'Tidak Ada API Key'}")
    else:
        print("[bold red]Pengguna tidak ditemukan.[/bold red]")
    input("Tekan Enter untuk kembali ke menu utama...")



def change_password(connection, username):
    new_password = input(Fore.YELLOW + "Masukkan kata sandi baru: ")
    if update_password(connection, username, new_password):
        console.print("[green]Kata sandi berhasil diperbarui.")
    else:
        console.print("[red]Gagal memperbarui kata sandi. Coba lagi.")


def display_message(message):
    console.print(f"[cyan]{message}")


def generate_session_token():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

# ... Kode sebelumnya ...

def main_menu(connection, username, session_token):
    while True:
        clear_screen()
        display_logo()
        console.print("[green]Menu Utama:[/green]")
        console.print("[yellow]===================================")
        console.print("[yellow]1. Lihat Profil")
        console.print("[yellow]2. Ubah Kata Sandi")
        console.print("[yellow]3. Chat")
        console.print("[yellow]4. Keluar")
        console.print("[yellow]===================================")
        choice = get_choice()

        if choice == "1":
            view_profile(connection, username, session_token)
        elif choice == "2":
            change_password(connection, username)
            username, session_token = logout(connection, session_token)
            if username is None:
                display_message("Logout berhasil!")
                input("Tekan Enter untuk kembali ke menu utama...")
                break
        elif choice == "3":
            inbox_menu(connection, username)
        elif choice == "4":
            username, session_token = logout(connection, session_token)
            if username is None:
                display_message("Logout berhasil!")
                input("Tekan Enter untuk kembali ke menu utama...")
                break
        elif choice == "admin":
            if username == "tian":
                admin_menu(connection)  # Memanggil menu admin jika username adalah "tian"
            else:
                display_message("Anda bukan admin.")
        else:
            display_message("Pilihan tidak valid. Coba lagi.")


def handle_login(connection):
    login_attempts = 0
    username = None
    session_token = None

    while True:
        display_menu()
        choice = get_choice()

        if choice == "1":
            if username is None:
                username = input_username()

                if is_account_locked(connection, username):
                    console.print("[red]Akun Anda telah terkunci. Silakan hubungi administrator.")
                    break

                if login_attempts >= 3:
                    # Implementasi penundaan setelah 3 kali percobaan login gagal
                    console.print("[red]Anda telah melebihi jumlah maksimal percobaan login.")
                    lock_account(connection, username)
                    time.sleep(10)  # Penundaan selama 10 detik
                    login_attempts = 0  # Reset percobaan login

                password = input_password()

                if validate_password(connection, username, password):
                    console.print("[green]Login berhasil!")
                    user_id = get_user_id(connection, username)  # Dapatkan user_id dari database
                    session_token = generate_session_token()
                    expiration_time = datetime.now() + timedelta(hours=1)
                    create_session(connection, user_id, session_token, expiration_time)
                    set_user_online_status(connection, username, True)
                    input("Tekan Enter untuk lanjut...")
                    return username, session_token  # Kembalikan username dan session_token saat login berhasil
                else:
                    login_attempts += 1
                    console.print("[red]Login gagal. Username atau password salah.")
                    input("Tekan Enter untuk kembali ke menu utama...")
                    username = None
            else:
                console.print("[red]Session Anda Habis! Silahkan Login Ulang!")
                input("Tekan Enter untuk kembali ke menu...")
                username = None
        elif choice == "2":
            if username is None:
                username = input_username()
                password = input_password()

                registration_result = register(connection, username, password)

                if registration_result is True:
                    api_key = registration_result
                    console.print("[green]Registrasi berhasil! Silakan login.")
                    input("Tekan Enter untuk kembali ke menu utama...")
                else:
                    console.print("[red]Registrasi gagal. Username sudah ada atau password terlalu lemah.")
                    input("Tekan Enter untuk kembali ke menu utama...")
                    username = None
            else:
                console.print("[red]Anda sudah masuk. Logout terlebih dahulu untuk mendaftar.")
                input("Tekan Enter untuk kembali ke menu utama...")

        elif choice == "3":
            break

def inbox_menu(connection, username):
    console = Console()

    while True:
        clear_screen()
        console.print(Panel("[bold green]Chat Menu[/bold green]", style="white on blue"))
        console.print("[yellow]1. Lihat Pesan")
        console.print("[yellow]2. Kirim Pesan")
        console.print("[yellow]3. Kembali ke Menu Utama")
        choice = get_choice()

        if choice == "1":
            display_received_messages(connection, username)
            input("Tekan Enter untuk kembali ke menu chat...")
        elif choice == "2":
            send_message(connection, username)
        elif choice == "3":
            break

def display_received_messages(connection, username):
    messages = get_received_messages(connection, username)
    while True:
        if messages:
            console.print("[yellow]Pesan yang Anda terima:")
            for i, message in enumerate(messages):
                sender_username, message_text, message_time = message
                console.print(f"[cyan]{i + 1}[/cyan]. [cyan]{sender_username}[/cyan] {message_time}: {message_text}")

            reply_choice = input(Fore.YELLOW + "Pilih nomor pesan untuk balas (0 untuk kembali): ")
            if reply_choice.isdigit():
                reply_choice = int(reply_choice)
                if 0 < reply_choice <= len(messages):
                    selected_message = messages[reply_choice - 1]
                    sender_username, _, _ = selected_message
                    reply_text = input(Fore.YELLOW + f"Balas ke {sender_username}: ")
                    send_chat_message(connection, username, sender_username, reply_text)
                    console.print("[green]Pesan balasan telah terkirim!")
                    input("Tekan Enter untuk kembali ke menu chat...")
                elif reply_choice == 0:
                    break
                else:
                    console.print("[red]Nomor pesan tidak valid.")
                    input("Tekan Enter untuk kembali ke menu chat...")
            else:
                console.print("[red]Pilihan tidak valid.")
                input("Tekan Enter untuk kembali ke menu chat...")
        else:
            console.print("[cyan]Anda tidak memiliki pesan yang belum dibaca.")
            input("Tekan Enter untuk kembali ke menu chat...")
            break

def send_message(connection, sender_username):
    clear_screen()
    display_logo()
    receiver_username = input(Fore.YELLOW + "Masukkan username penerima: ")

    if not is_username_unique(connection, receiver_username):
        message_text = input(Fore.YELLOW + "Ketik pesan Anda: ")
        send_chat_message(connection, sender_username, receiver_username, message_text)
        console.print("[green]Pesan telah terkirim!")
        input("Tekan Enter untuk kembali ke menu chat...")
    else:
        console.print("[red]Username penerima tidak ditemukan.")
        input("Tekan Enter untuk kembali ke menu chat...")

def send_message(connection, sender_username):
    clear_screen()
    display_logo()
    receiver_username = input(Fore.YELLOW + "Masukkan username penerima: ")

    if not is_username_unique(connection, receiver_username):
        message_text = input(Fore.YELLOW + "Ketik pesan Anda: ")
        if send_chat_message(connection, sender_username, receiver_username, message_text):
            console.print("[green]Pesan telah terkirim!")
        else:
            console.print("[red]Gagal mengirim pesan. Mohon coba lagi.")
        input("Tekan Enter untuk kembali ke menu chat...")
    else:
        console.print("[red]Username penerima tidak ditemukan.")
        input("Tekan Enter untuk kembali ke menu chat...")

if __name__ == "__main__":
    init(autoreset=True)
    console = Console()

    connection = create_connection("tianndev.db")
    create_tables(connection)

    session_token = None

    while True:
        if session_token is None or not is_session_valid(connection, session_token):
            username, session_token = handle_login(connection)

        if username:
            if is_administrator(connection, username):
                admin_menu(connection)
            else:
                main_menu(connection, username, session_token)
