from rich import print
from rich.console import Console
from rich import color
from rich.table import Table
from rich.panel import Panel
from colorama import Fore, Style, init
import secrets
import emoji
import subprocess
import importlib
from rich.text import Text

import sqlite3
import os,re
import random
import string
import time,sys
import admin
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
    upgrade_user_to_premium,
    update_email

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
⠀⣠⣶⣿⣿⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠹⢿⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⡏⢀⣀⡀⠀⠀⠀⠀⠀
⠀⠀⣠⣤⣦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⣟⣋⣼⣽⣾⣽⣦⡀⠀⠀⠀
⢀⣼⣿⣷⣾⡽⡄⠀⠀⠀⠀⠀⠀⠀⣴⣶⣶⣿⣿⣿⡿⢿⣟⣽⣾⣿⣿⣦⠀⠀
⣸⣿⣿⣾⣿⣿⣮⣤⣤⣤⣤⡀⠀⠀⠻⣿⡯⠽⠿⠛⠛⠉⠉⢿⣿⣿⣿⣿⣷⡀
⣿⣿⢻⣿⣿⣿⣛⡿⠿⠟⠛⠁⣀⣠⣤⣤⣶⣶⣶⣶⣷⣶⠀⠀⠻⣿⣿⣿⣿⣇
⢻⣿⡆⢿⣿⣿⣿⣿⣤⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠟⠀⣠⣶⣿⣿⣿⣿⡟
⠈⠛⠃⠈⢿⣿⣿⣿⣿⣿⣿⠿⠟⠛⠋⠉⠁⠀⠀⠀⠀⣠⣾⣿⣿⣿⠟⠋⠁⠀
⠀⠀⠀⠀⠀⠙⢿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⠟⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣼⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠻⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """
    )

def input_username():
    return input("👤 Username: ")

def input_password():
    return input("🔒 Password: ")

def get_choice():
    return input("👆 Pilihan Anda: ").strip()


console = Console()

def display_menu():
    console.clear()
    print('''    |￣￣￣￣￣￣￣￣￣￣￣￣￣￣|
        Selamat Datang di Forum
    |＿＿＿＿＿＿＿＿＿＿＿＿＿＿|
                        \ (•◡•) /
                        \       /''')

    table = Table(show_header=False)
    table.add_column("[yellow]Pilihan", justify="center", width=50)
    table.add_row("[cyan1]1. [bold]:closed_lock_with_key: Login[/bold]")
    table.add_row("[cyan2]2. [bold]:busts_in_silhouette: Daftar[/bold]")
    table.add_row("[red3]3. [bold]:x: Keluar[/bold]")
    console.print(table)


def view_profile(connection, username, session_token):
    user_info = get_user_info(connection, username)
    if user_info:
        stored_user_id, stored_username, stored_password, stored_registration_date, stored_email, is_premium, premium_duration, api_key, is_online = user_info

        clear_screen()
        display_logo()
        console.print("[bold green]Profil Pengguna[/bold green] 📌")
        console.print(f"🆔 [yellow]Nomor Seri:[/yellow] {stored_user_id}")
        console.print(f"👤 [yellow]Username:[/yellow] {stored_username}")
        console.print(f"🔒 [yellow]Password:[/yellow] {'*' * len(stored_password)}")
        formatted_registration_date = datetime.strptime(stored_registration_date, "%Y-%m-%d %H:%M:%S").strftime("%d %B %Y")
        console.print(f"📅 [yellow]Tanggal Pendaftaran:[/yellow] {formatted_registration_date}")
        console.print(f"📧 [yellow]Email:[/yellow] {stored_email if stored_email else 'None'}")
        console.print(f"🌟 [yellow]Status Premium:[/yellow] {'✅ Premium' if is_premium else '❌ Gratis'}")
        console.print(f"💻 [yellow]Status Online:[/yellow] {'✅ Online' if is_online else '❌ Offline'}")
        console.print(f"⏳ [yellow]Durasi Premium:[/yellow] {premium_duration} hari")
        console.print(f"🔑 [yellow]API Key:[/yellow] {api_key if api_key else 'Tidak Ada API Key'}")
    else:
        console.print("[bold red]Pengguna tidak ditemukan.[/bold red]")
    input("\nTekan Enter untuk kembali ke menu utama...")



def change_password(connection, username):
    while True:
        display_logo()
        console.print("[green]Ubah Kata Sandi:[/green]")
        console.print("[yellow]===================================")

        # Meminta kata sandi lama dan kata sandi baru dari pengguna
        old_password = input("Masukkan kata sandi lama: ")
        new_password = input("Masukkan kata sandi baru: ")

        # Memeriksa kata sandi lama yang sesuai
        if validate_password(connection, username, old_password):
            # Mengupdate kata sandi baru di database
            if update_password(connection, username, new_password):
                console.print("[green]Kata sandi berhasil diubah![/green]")
                input("Tekan Enter untuk kembali ke menu utama...")
                break
            else:
                display_message("Terjadi kesalahan saat mengubah kata sandi. Coba lagi.")
        else:
            display_message("Kata sandi lama tidak cocok. Coba lagi.")

def display_message(message):
    console.print(f"[cyan]{message}")

def is_valid_email(email):
    # Periksa keberadaan karakter "@" dalam email
    if "@" not in email:
        return False

    # Gunakan ekspresi reguler untuk memeriksa apakah email memiliki format yang benar
    pattern = r'^\S+@\S+\.\S+$'
    return re.match(pattern, email)

# Fungsi untuk mengubah email pengguna
def change_email(connection, username):
    clear_screen()
    display_logo()
    console.print("[yellow]===================================")
    console.print("[yellow]Ubah Alamat Email")
    console.print("[yellow]===================================")

    # Mintalah pengguna untuk memasukkan email baru
    new_email = input("Masukkan email baru: ")

    # Validasi email yang dimasukkan oleh pengguna
    if not is_valid_email(new_email):
        display_message("Email yang dimasukkan tidak valid. Coba lagi.")
        input("Tekan Enter untuk melanjutkan...")
        return

    try:
        # Perbarui alamat email dalam database
        update_email(connection, username, new_email)
        display_message("Alamat email berhasil diperbarui.")
        input("Tekan Enter untuk kembali ke menu pengaturan...")
    except Exception as e:
        display_message(f"Terjadi kesalahan: {str(e)}")
        input("Tekan Enter untuk kembali ke menu pengaturan...")

def generate_session_token():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))


def display_statistics(connection):
    cursor = connection.cursor()
    
    # Hitung total pengguna
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Hitung total pesan dalam sistem
    cursor.execute("SELECT COUNT(*) FROM chat_messages")
    total_messages = cursor.fetchone()[0]

    # Hitung total pengguna online
    cursor.execute("SELECT username FROM users WHERE is_online = 1")
    online_users = [row[0] for row in cursor.fetchall()]

    clear_screen()
    display_logo()
    console.print("📊 [green]Statistik Aplikasi[/green] 📈")
    console.print("📋 [yellow]===================================")
    console.print(f"👥 [yellow]Total Pengguna: {total_users}")
    console.print(f"💌 [yellow]Total Pesan: {total_messages}")
    console.print(f"💻 [yellow]Total Pengguna Online: {len(online_users)}")
    console.print("📊 [green]Statistik[/green] 📈")
    console.print("📋 [yellow]===================================")
    console.print("👥 [yellow]Pengguna Online[/yellow]")
    for user in online_users:
        console.print(f"🔵 [yellow]- {user}")
    console.print("📋 [yellow]===================================")
    input("Tekan Enter untuk kembali ke menu utama...")


def settings_menu(connection, username):
    while True:
        clear_screen()
        display_logo()
        console.print("[green]Pengaturan:[/green]")
        console.print("[yellow]===================================")
        console.print("[yellow]1. Ubah Email ✉️")
        console.print("[yellow]2. Ubah Kata Sandi 🔐")
        console.print("[yellow]3. Atur Notifikasi 🔔")
        console.print("[yellow]4. Kembali ke Menu Utama ↩️")
        console.print("[yellow]===================================")
        choice = get_choice()

        if choice == "1":
            change_email(connection, username)
        elif choice == "2":
            change_password(connection, username)  # Panggil fungsi "change_password" untuk mengubah kata sandi
        elif choice == "3":
            configure_notifications()
        elif choice == "4":
            break
        else:
            display_message("Pilihan tidak valid. Coba lagi.")


def display_about_us():
    clear_screen()
    display_logo()
    console.print("[bold cyan]Tentang Kami[/bold cyan]")
    console.print("[yellow]===================================")
    console.print("👋 Selamat datang di Aplikasi Kami!")
    console.print("🚀 Versi Aplikasi: 1.0")
    console.print("✉️ Hubungi Kami: haha@gacorkang.my.id")
    console.print("ℹ️ Aplikasi ini dibuat untuk tujuan demonstrasi dan pembelajaran.")
    console.print("🌐 Kunjungi situs web kami: https://gacorkang.my.id")
    console.print("[yellow]===================================")
    input("Tekan Enter untuk kembali ke Menu Tambahan...")



def main_menu(connection, username, session_token):
    while True:
        clear_screen()
        display_logo()
        console.print("[bold green]Menu Utama[/bold green]")
        console.print("[yellow]===================================")
        console.print("[yellow]1. Lihat Profil [/yellow](👤)")
        console.print("[yellow]2. Chat [/yellow](💬)")
        console.print("[yellow]3. Statistik [/yellow](📊)")
        console.print("[yellow]4. Pengaturan [/yellow](⚙️)")
        console.print("[yellow]5. Tentang Kami [/yellow](ℹ️)")
        console.print("[yellow]6. Keluar [/yellow](🚪)")
        console.print("[yellow]===================================")
        choice = get_choice()


        if choice == "1":
            view_profile(connection, username, session_token)
        elif choice == "2":
            chat_menu(connection, username)
        elif choice == "3":
            display_statistics(connection)
        elif choice == "4":
            settings_menu(connection, username)  # Panggil submenu pengaturan
        elif choice == "5":
            display_about_us()
        elif choice == "6":
            username, session_token = logout(connection, session_token)
            if username is None:
                display_message("Logout berhasil!")
                input("Tekan Enter untuk kembali ke menu utama...")
                break
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
                    input("Tekan Enter untuk kembali ke menu utama...")

                    username = None

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
                    if login_attempts >= 3:
                        console.print("[red]Anda telah melebihi jumlah maksimal percobaan login.")
                        lock_account(connection, username)
                        time.sleep(10)  # Penundaan selama 10 detik
                        login_attempts = 0  # Reset percobaan login
                    else:
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


def chat_menu(connection, username):
    while True:
        clear_screen()
        display_logo()
        console.print("[bold cyan]🗨️ Menu Obrolan 🗨️[/bold cyan]")
        console.print("[yellow]===================================")
        console.print("[cyan]1. 📩 Mulai Obrolan[/cyan]")
        console.print("[cyan]2. 📥 Lihat Pesan[/cyan]")
        console.print("[cyan]3. ✉️ Kirim Pesan[/cyan]")
        console.print("[red]4. 🚪 Keluar[/red]")
        console.print("[yellow]===================================")
        choice = get_choice()

        if choice == "1":
            start_chat(connection, username)
        elif choice == "2":
            view_messages(connection, username)
        elif choice == "3":
            send_message(connection, username)
        elif choice == "4":
            break
        else:
            display_message("Pilihan tidak valid. Coba lagi.")


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

def send_chat_message(connection, sender_username, receiver_username, message):
    cursor = connection.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("INSERT INTO chat_messages (sender_username, receiver_username, message_text, timestamp) VALUES (?, ?, ?, ?)",
                       (sender_username, receiver_username, message, timestamp))
        connection.commit()
        return True
    except Exception as e:
        print("Error:", e)
        return False

def check_required_modules():
    required_modules = [
        "rich", "colorama", "secrets", "emoji", "sqlite3", "os", "re", "random","string", "time", "datetime","rich","rich.table","rich.panel","secrets", "emoji", "rich.text"
    ]

    missing_modules = []

    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_modules.append(module_name)

    return missing_modules

def install_missing_modules(missing_modules):
    if missing_modules:
        for module_name in missing_modules:
            try:
                subprocess.run(["python","-m", "pip", "install", module_name], check=True)
                print(f"Modul {module_name} telah diinstal.")
            except subprocess.CalledProcessError:
                print(f"Gagal menginstal modul {module_name}.")


def run_program():
    # Program utama Anda di sini
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
                admin.admin_menu(connection)
            else:
                main_menu(connection, username, session_token)

def main():
    missing_modules = check_required_modules()

    if missing_modules:
        print("Modul-modul berikut belum terinstal:")
        for module in missing_modules:
            print(module)
        print("Menginstal modul-modul yang dibutuhkan...")
        install_missing_modules(missing_modules)
    else:
        run_program()

if __name__ == "__main__":
    main()
