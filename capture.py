import cv2
import numpy as np
import pyautogui
import win32gui
import win32ui
import win32con
import time

def capture_fullscreen(save_path):
    """Captures the entire screen and saves it to the specified path."""
    screen = np.array(pyautogui.screenshot())
    cv2.imwrite(save_path, screen)
    return screen

def capture_active_window():
    """Captures the active window and returns a NumPy array."""
    window = pyautogui.getActiveWindow()
    if window:
        x, y, width, height = window.left, window.top, window.width, window.height
        screen = np.array(pyautogui.screenshot(region=(x, y, width, height)))
        return screen
    return None

def capture_region(x1, y1, x2, y2):
    """Captures a specified region of the screen."""
    screen = np.array(pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1)))
    return screen

def capture_active_monitor():
    """Captures the primary monitor."""
    primary_monitor = pyautogui.primaryMonitor
    screen = np.array(pyautogui.screenshot(region=(primary_monitor.left, primary_monitor.top, primary_monitor.width, primary_monitor.height)))
    return screen

def capture_all_monitors():
    """Captures all monitors and combines them into a single image."""
    all_screens = []
    monitors = pyautogui.getMonitors()
    for monitor in monitors:
        screen = np.array(pyautogui.screenshot(region=(monitor.left, monitor.top, monitor.width, monitor.height)))
        all_screens.append(screen)

    # Combine screens into a single image
    combined_width = sum(monitor.width for monitor in monitors)
    combined_height = max(monitor.height for monitor in monitors)
    combined_screen = np.zeros((combined_height, combined_width, 3), dtype=np.uint8)

    offset = 0
    for screen in all_screens:
        screen_height, screen_width, _ = screen.shape
        combined_screen[:screen_height, offset:offset + screen_width] = screen
        offset += screen_width

    return combined_screen

def capture_window_menu():
    """Captures the active window's menu."""
    hwnd = win32gui.GetForegroundWindow()
    rect = win32gui.GetWindowRect(hwnd)
  
    # Create a device context
    hdc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hdc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # Create a bitmap
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfc_dc, rect[2] - rect[0], rect[3] - rect[1])
    save_dc.SelectObject(bmp)

    # BitBlt to capture the window
    win32gui.BitBlt(save_dc, 0, 0, rect[2] - rect[0], rect[3] - rect[1], hdc, 0, 0, win32con.SRCCOPY)

    # Convert bitmap to numpy array
    signed_ints_array = bmp.GetBitmapBits(True)
    img = np.frombuffer(signed_ints_array, dtype='uint8')
    img = img.reshape((rect[3] - rect[1], rect[2] - rect[0], 4))
    img = img[..., :3]  # Drop alpha channel

    # Convert to OpenCV format
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    mfc_dc.DeleteDC()
    save_dc.DeleteDC()
    bmp.DeleteObject()

    return img

def capture_scrolling_content(scroll_amount, delay=0.1, overlap=0.2):
    """Captures scrolling content by simulating scrolling and taking multiple screenshots."""
    initial_pos = pyautogui.position()
    images = []

    for i in range(scroll_amount // 100 + 1):
        screen = np.array(pyautogui.screenshot())
        images.append(screen)
        pyautogui.scroll(-100)  # Scroll down
        time.sleep(delay)

    # Combine images into a single image
    combined_height = sum(img.shape[0] for img in images)
    combined_width = images[0].shape[1]
    combined_screen = np.zeros((combined_height, combined_width, 3), dtype=np.uint8)

    y_offset = 0
    for img in images:
        img_height, img_width, _ = img.shape
        combined_screen[y_offset:y_offset + img_height, :img_width] = img
        y_offset += img_height

    return combined_screen
