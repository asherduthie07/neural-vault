from typing import Optional
from PySide6.QtCore import QRect

try:
    import win32gui
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False

def get_active_window_rect() -> Optional[QRect]:
    if not PYWIN32_AVAILABLE:
        return None
    
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            # Skip common desktop window handles
            class_name = win32gui.GetClassName(hwnd)
            if class_name in ("Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"):
                return None
                
            # Verify window visibility and minimized state
            if not win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
                return None
                
            rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = rect
            w = right - left
            h = bottom - top
            
            # Sanity check for valid foreground sizes
            if w > 100 and h > 100:
                return QRect(left, top, w, h)
    except Exception as e:
        print(f"Error reading foreground window geometry: {e}")
        
    return None
