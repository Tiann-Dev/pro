from colorama import Fore, init
import os

# Inisialisasi Colorama
init(autoreset=True)

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def display_logo():
    logo = r"""
  ____  __   __ ____    _    _   _ 
 / ___| \ \ / /|  _ \  / \  | \ | |
| |  _   \ V / | | | |/ _ \ |  \| |
| |_| |   | |  | |_| / ___ \| |\  |
 \____|   |_|  |____/_/   \_\_| \_|
                                   
    """
    print(Fore.BLUE + logo)

def display_menu():
    clear_screen()
    display_logo()
    print(Fore.GREEN + "Menu:")
    print(Fore.YELLOW + "1. Login")
    print(Fore.YELLOW + "2. Daftar")
    print(Fore.YELLOW + "3. Keluar")

def get_choice():
    return input(Fore.CYAN + "Pilihan Anda: ")

def input_username():
    return input(Fore.CYAN + "Username: ")

def input_password():
    return input(Fore.CYAN + "Password: ")

def display_message(message):
    print(Fore.MAGENTA + message)
