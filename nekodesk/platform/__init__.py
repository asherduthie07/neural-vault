import sys
from typing import Optional
from PySide6.QtCore import QRect

def get_foreground_window_rect() -> Optional[QRect]:
    if sys.platform == "win32":
        try:
            from .windows import get_active_window_rect
            return get_active_window_rect()
        except ImportError:
            pass
    return None

def apply_platform_window_tweaks(window_id) -> None:
    if sys.platform == "darwin":
        try:
            from .macos import apply_macos_tweaks
            apply_macos_tweaks(window_id)
        except Exception as e:
            print(f"macOS tweaks error: {e}")
    elif sys.platform == "linux":
        try:
            from .linux import apply_linux_tweaks
            apply_linux_tweaks(window_id)
        except Exception as e:
            print(f"Linux tweaks error: {e}")
