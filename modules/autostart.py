import os
import winreg as reg

def run(**args):
    try:
        file_path = os.path.realpath(__file__)
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE) as reg_key:
            reg.SetValueEx(reg_key, "MyApp", 0, reg.REG_SZ, file_path)
        print("Added to startup.")
    except Exception as e:
        print(f"Failed to add to startup: {e}")

if __name__ == "__main__":
    run()
