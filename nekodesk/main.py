import os
import sys
import time
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QEnterEvent
from PySide6.QtWidgets import QApplication, QWidget

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from states import CatState
from cat import Cat
from config import Settings
from tray import SystemTrayManager
from platform import get_foreground_window_rect, apply_platform_window_tweaks


class PetWindow(QWidget):
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
        self.settings = Settings()
        self.cat = Cat(base_path)

        self.paused = False
        self.last_update_time = time.time()

        self.init_window()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(16)

    def init_window(self):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        self.update_window_flags()

        screen = QApplication.primaryScreen().availableGeometry()

        start_x = int((screen.width() - self.cat.physics.width) / 2)
        start_y = 50

        print("Screen size:", screen.width(), screen.height())
        print("Starting cat at:", start_x, start_y)

        self.cat.physics.set_position(start_x, start_y)

        self.setGeometry(
            start_x,
            start_y,
            self.cat.physics.width,
            self.cat.physics.height
        )

        apply_platform_window_tweaks(self.winId())

        self.show()
        self.raise_()
        self.activateWindow()

        print("Pet window initialized")

    def update_window_flags(self):
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setWindowFlags(flags)

    def game_loop(self):
        print("Running")

        curr_time = time.time()
        dt = curr_time - self.last_update_time
        self.last_update_time = curr_time
        dt = min(0.05, dt)

        screen = QApplication.primaryScreen().availableGeometry()

        if self.settings.get("enable_ai") and sys.platform == "win32":
            self.cat.physics.enable_window_collision = True
            self.cat.physics.active_window_rect = get_foreground_window_rect()
        else:
            self.cat.physics.enable_window_collision = False
            self.cat.physics.active_window_rect = None

        self.cat.update(dt, screen, self.paused)

        self.setGeometry(
            int(self.cat.physics.x),
            int(self.cat.physics.y),
            self.cat.physics.width,
            self.cat.physics.height
        )

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        pixmap = self.cat.get_current_pixmap()

        if pixmap and not pixmap.isNull():
            print("Pixmap loaded successfully")
            painter.drawPixmap(0, 0, pixmap)
        else:
            print("Pixmap failed to load — drawing fallback")
            painter.fillRect(self.rect(), Qt.GlobalColor.red)

        painter.end()

    def mousePressEvent(self, event):
        self.cat.interaction_handler.handle_mouse_press(self.cat, event)

    def mouseMoveEvent(self, event):
        self.cat.interaction_handler.handle_mouse_move(self.cat, event)

    def mouseReleaseEvent(self, event):
        self.cat.interaction_handler.handle_mouse_release(self.cat, event)

    def mouseDoubleClickEvent(self, event):
        self.cat.interaction_handler.handle_double_click(self.cat, event)

    def enterEvent(self, event: QEnterEvent):
        self.cat.interaction_handler.handle_hover(self.cat, True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.cat.interaction_handler.handle_hover(self.cat, False)
        super().leaveEvent(event)

    def set_pause(self, paused: bool):
        self.paused = paused
        if paused:
            self.cat.set_state(CatState.SIT)
            self.cat.sound_manager.stop_all()

    def restart_pet(self):
        screen = QApplication.primaryScreen().availableGeometry()
        start_x = int((screen.width() - self.cat.physics.width) / 2)

        self.cat.physics.set_position(start_x, 50)
        self.cat.physics.vx = 0.0
        self.cat.physics.vy = 0.0
        self.cat.physics.grounded = False

        self.cat.set_state(CatState.FALL)
        self.cat.sound_manager.play("meow")

    def sync_settings(self):
        self.update_window_flags()
        self.cat.update_dimensions()


def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    base_path = os.path.dirname(os.path.abspath(__file__))

    assets_dir = os.path.join(base_path, "assets")

    if not os.path.exists(assets_dir) or not os.listdir(assets_dir):
        print("Assets folder missing or empty. Generating assets...")
        import generate_assets
        generate_assets.main()

    window = PetWindow(base_path)

    tray = SystemTrayManager(
        base_path,
        window.cat.sound_manager,
        window
    )

    tray.quit_requested.connect(app.quit)
    tray.pause_toggled.connect(window.set_pause)
    tray.restart_requested.connect(window.restart_pet)
    tray.settings_updated.connect(window.sync_settings)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()