from rich import print
from rich.console import Console
from rich.progress import Progress
from rich import color
from colorama import Fore, init

import os
import random
import string
import time
from PIL import Image
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
    set_user_online_status,  # Tambahkan ini
    get_online_users,  # Tambahkan ini
    send_chat_message,  # Tambahkan ini
    get_received_messages,  #
    get_username_by_id,
    is_username_unique,
    create_tables

    )

# Buat koneksi ke database
connection = create_connection()

# Buat tabel-tabel
create_tables(connection)

# Tutup koneksi
connection.close()


console = Console()

def request_premium(connection, username):
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET is_premium = 2 WHERE username = ?", (username,))
    connection.commit()

def chat_menu(connection, username):
    while True:
        print("1. Kirim Pesan")
        print("2. Baca Pesan")
        print("3. Kembali ke Menu Utama")
        choice = get_choice()

        if choice == "1":
            receiver_username = input("Username Penerima: ")
            message = input("Pesan: ")
            send_chat_message(connection, username, receiver_username, message)
            print("Pesan telah dikirim.")

        elif choice == "2":
            receiver_username = input("Username Penerima: ")
            messages = get_chat_messages(connection, username, receiver_username)
            if not messages:
                print("Tidak ada pesan.")
            for message in messages:
                sender, receiver, text, timestamp = message
                print(f"[{timestamp}] {sender}: {text}")

        elif choice == "3":
            break


def logout(connection, session_token):
    # Hapus sesi berdasarkan token
    delete_session(connection, session_token)
    return None  # Kembalikan None sebagai tanda logout berhasils

def is_session_valid(connection, session_token):
    cursor = connection.cursor()
    current_time = datetime.now()

    cursor.execute("SELECT expiration_time FROM sessions WHERE session_token = ?", (session_token,))
    expiration_time = cursor.fetchone()

    if expiration_time and current_time < expiration_time[0]:
        return True
    else:
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
    return input(Fore.YELLOW + "Pilihan Anda: ")

def display_menu():
    clear_screen()
    display_logo()
    console.print("[green]Menu:")
    console.print("[yellow]1. Login")
    console.print("[yellow]2. Daftar")
    console.print("[yellow]3. Keluar")

def view_profile(connection, user_id, username):
    user_info = get_user_info(connection, username)
    if user_info:
        stored_user_id, stored_username, stored_password, stored_registration_date, stored_email, is_premium = user_info
        clear_screen()
        display_logo()
        print(Fore.GREEN+"Profil Pengguna:")
        print(Fore.YELLOW + f"Nomor Seri: {stored_user_id}")
        print(Fore.YELLOW + f"Username: {stored_username}")
        print(Fore.YELLOW + f"Password: {stored_password}")
        print(Fore.YELLOW + f"Tanggal Pendaftaran: {stored_registration_date}")
        print(Fore.YELLOW + f"Status Premium: {'Premium' if is_premium else 'Gratis'}")
    else:
        display_message("Pengguna tidak ditemukan.")
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


def main_menu(connection, user_id, username):
    while True:
        clear_screen()
        display_logo()
        print(Fore.GREEN + "Menu Utama:")
        print(Fore.YELLOW + "1. Lihat Profil")
        print(Fore.YELLOW + "2. Ubah Kata Sandi")
        print(Fore.YELLOW + "3. Chat")
        print(Fore.YELLOW + "4. Keluar")
        choice = get_choice()

        # Di dalam fungsi main_menu
        if choice == "1":
            view_profile(connection, user_id, username)  # Hanya memerlukan 3 argumen

        elif choice == "2":
            change_password(connection, username)
            delete_session(connection, session_token)
            input("Tekan Enter untuk kembali ke menu utama...")
            break
        elif choice == "3":
            inbox_menu(connection, username) 
        elif choice == "4":
            username = logout(connection, session_token)
            if username is None:
                display_message("Logout berhasil!")
                input("Tekan Enter untuk kembali ke menu utama...")
                break
            display_message("Pilihan tidak valid. Coba lagi.")


if __name__ == "__main__":
    connection = create_connection()
    create_tables(connection)
    username = None
    session_token = None
    login_attempts = 0

# ...

def handle_login(connection):
    login_attempts = 0
    user_id = None
    username = None

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
                    input("Tekan Enter untuk lanjut...")
                    main_menu(connection, user_id, username)
                    break
                else:
                    login_attempts += 1
                    console.print("[red]Login gagal. Username atau password salah.")
                    input("Tekan Enter untuk kembali ke menu utama...")
                    username = None
            else:
                console.print("[red]Session Anda Habis! Silahkan Login Ulang!")
                input("Tekan Enter untuk kembali ke menu...")
                username = None
                def set_user_online_status(connection, username, online_status):
                    cursor = connection.cursor()
                    cursor.execute("UPDATE users SET is_online = ? WHERE username = ?", (online_status, username))
                    connection.commit()

        elif choice == "2":
            if username is None:
                username = input_username()
                password = input_password()

                registration_result = register(connection, username, password)


                if registration_result is True:
                    console.print("[green]Pendaftaran berhasil!")
                    username = None
                else:
                    console.print(f"[red]{registration_result}")
                input("Tekan Enter untuk kembali ke menu utama...")
                username = None
            else:
                console.print("[red]Session Anda Habis! Silahkan Login Ulang!")
                input("Tekan Enter untuk kembali ke menu...")
                username = None
        elif choice == "3":
            break
def get_received_messages(connection, receiver_username):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT sender_id, message, timestamp FROM chat_messages WHERE receiver_id = (SELECT id FROM users WHERE username = ?) ORDER BY timestamp",
        (receiver_username,))
    messages = cursor.fetchall()
    return messages

def chat_menu(connection, username):
    while True:
        clear_screen()
        display_logo()
        print(Fore.GREEN + "Menu Chat:")
        print(Fore.YELLOW + "1. Kirim Pesan")
        print(Fore.YELLOW + "2. Pesan Masuk")
        print(Fore.YELLOW + "3. Kembali")
        choice = get_choice()

        if choice == "1":
            receiver_username = input(Fore.YELLOW + "Masukkan username penerima: ")
            message = input(Fore.YELLOW + "Masukkan pesan: ")
            send_chat_message(connection, username, receiver_username, message)

        elif choice == "2":
            received_messages = get_received_messages(connection, username)
            clear_screen()
            display_logo()
            print(Fore.GREEN + "Pesan Masuk:")
            for sender_id, message, timestamp in received_messages:
                sender_username = get_username_by_id(connection, sender_id)
                print(Fore.YELLOW + f"Dari: {sender_username}")
                print(Fore.YELLOW + f"Pesan: {message}")
                print(Fore.YELLOW + f"Waktu: {timestamp}")
                print()

        elif choice == "3":
            break

# Fungsi untuk menampilkan daftar pesan masuk
def display_inbox(connection, username):
    cursor = connection.cursor()
    cursor.execute("SELECT id, sender_id, message, timestamp FROM chat_messages WHERE receiver_username = ? ORDER BY timestamp DESC", (username,))
    messages = cursor.fetchall()

    if not messages:
        print("Tidak ada pesan masuk.")
        return

    print("Daftar Pesan Masuk:")
    for idx, message in enumerate(messages, start=1):
        message_id, sender_id, message_text, timestamp = message
        sender_username = get_username_by_id(connection, sender_id)
        print(f"{idx}. Dari: {sender_username}, Tanggal: {timestamp}")
    
    while True:
        try:
            choice = int(input("Pilih nomor pesan yang ingin Anda baca (0 untuk kembali): "))
            if choice == 0:
                break
            elif 1 <= choice <= len(messages):
                selected_message = messages[choice - 1]
                message_id, sender_id, message_text, timestamp = selected_message
                sender_username = get_username_by_id(connection, sender_id)
                print(f"Pesan dari {sender_username} pada {timestamp}:")
                print(message_text)
            else:
                print("Nomor pesan tidak valid. Coba lagi.")
        except ValueError:
            print("Input tidak valid. Harap masukkan nomor pesan.")

# Fungsi untuk menu pesan masuk

def send_message(connection, sender_id, receiver_username, message):
    cursor = connection.cursor()
    receiver_id = get_user_id(connection, receiver_username)  # Mendapatkan receiver_id berdasarkan receiver_username

    if receiver_id is not None:
        # Definisikan sender_username dan receiver_username
        sender_username = "nama_pengirim"  # Gantilah dengan username pengirim
        receiver_username = "nama_penerima"  # Gantilah dengan username penerima

        # Kemudian jalankan query
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO chat_messages (sender_id, receiver_id, sender_username, receiver_username, message, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                    (sender_id, receiver_id, sender_username, receiver_username, message, timestamp))

        print("Pesan terkirim.")
    else:
        print(f"Penerima dengan username {receiver_username} tidak ditemukan.")



def chat_with_user(connection, sender_username):
    receiver_username = input("Masukkan username penerima: ")
    if not is_username_unique(connection, receiver_username):
        while True:
            message = input("Ketik pesan Anda (ketik 'selesai' untuk keluar): ")
            if message.lower() == 'selesai':
                break
            send_message(connection, sender_username, receiver_username, message)
    else:
        print("Penerima dengan username tersebut tidak ditemukan.")

def inbox_menu(connection, username):
    while True:
        print("Menu Pesan Masuk:")
        print("1. Tampilkan Pesan Masuk")
        print("2. Kirim Pesan")
        print("3. Keluar")
        choice = input("Pilihan Anda: ")
        if choice == "1":
            display_inbox(connection, username)
        elif choice == "2":
            chat_with_user(connection, username)  # Menggunakan fungsi chat_with_user untuk mengirim pesan
        elif choice == "3":
            break
        else:
            print("Pilihan tidak valid. Coba lagi.")


if __name__ == "__main__":
    connection = create_connection()
    create_tables(connection)
    username = None
    session_token = None
    login_attempts = 0

    while True:
        handle_login(connection)
    
    connection.close()

