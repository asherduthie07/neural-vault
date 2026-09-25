import os
import sys
from typing import Optional
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QSystemTrayIcon, QMenu, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QSlider, QCheckBox, QPushButton, QWidget
)
from config import Settings
from sound import SoundManager

class SettingsDialog(QDialog):
    settings_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.settings = Settings()
        
        self.setWindowTitle("NekoDesk Settings")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setMinimumWidth(300)
        
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Scale slider
        layout.addWidget(QLabel("Cat Scale (Size)"))
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(50)  # 0.5x
        self.scale_slider.setMaximum(250) # 2.5x
        scale_val = int(self.settings.get("cat_scale") * 100)
        self.scale_slider.setValue(scale_val)
        self.scale_label = QLabel(f"{scale_val}%")
        self.scale_slider.valueChanged.connect(lambda v: self.scale_label.setText(f"{v}%"))
        
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(self.scale_slider)
        scale_layout.addWidget(self.scale_label)
        layout.addLayout(scale_layout)

        # Volume slider
        layout.addWidget(QLabel("Sound Volume"))
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setMinimum(0)
        self.vol_slider.setMaximum(100)
        vol_val = self.settings.get("volume")
        self.vol_slider.setValue(vol_val)
        self.vol_label = QLabel(f"{vol_val}%")
        self.vol_slider.valueChanged.connect(lambda v: self.vol_label.setText(f"{v}%"))
        
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(self.vol_slider)
        vol_layout.addWidget(self.vol_label)
        layout.addLayout(vol_layout)

        # Snapping option (Windows Snapping)
        self.snap_check = QCheckBox("Enable snip-to-window (Windows only)")
        self.snap_check.setChecked(self.settings.get("enable_ai")) # We reuse enable_ai or add snap key
        self.snap_check.setEnabled(sys.platform == "win32")
        layout.addWidget(self.snap_check)

        # Always on top
        self.ontop_check = QCheckBox("Always on Top")
        self.ontop_check.setChecked(self.settings.get("always_on_top"))
        layout.addWidget(self.ontop_check)

        # Start on boot (placeholder logic)
        self.boot_check = QCheckBox("Start on boot")
        self.boot_check.setChecked(self.settings.get("start_on_boot"))
        layout.addWidget(self.boot_check)

        # Spacer
        layout.addSpacing(15)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_settings(self) -> None:
        self.settings.set("cat_scale", self.scale_slider.value() / 100.0)
        self.settings.set("volume", self.vol_slider.value())
        self.settings.set("always_on_top", self.ontop_check.isChecked())
        self.settings.set("start_on_boot", self.boot_check.isChecked())
        self.settings.set("enable_ai", self.snap_check.isChecked()) # snaps flag
        
        self.settings_changed.emit()
        self.accept()

class SystemTrayManager(QObject):
    quit_requested = Signal()
    pause_toggled = Signal(bool)
    restart_requested = Signal()
    settings_updated = Signal()

    def __init__(self, base_path: str, sound_manager: SoundManager, parent: QWidget):
        super().__init__(parent)
        self.sound_manager = sound_manager
        self.parent_widget = parent
        self.is_paused = False
        
        # Load Icon
        icon_path = os.path.join(base_path, "assets", "sprites", "idle", "0.png")
        if os.path.exists(icon_path):
            self.icon = QIcon(icon_path)
        else:
            self.icon = QIcon() # fallback
            
        self.tray_icon = QSystemTrayIcon(self.icon, parent)
        self.create_menu()
        self.tray_icon.show()

    def create_menu(self) -> None:
        menu = QMenu()

        # Pause pet
        self.pause_action = QAction("Pause Pet", self)
        self.pause_action.setCheckable(True)
        self.pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(self.pause_action)

        # Mute sounds
        self.mute_action = QAction("Mute", self)
        self.mute_action.setCheckable(True)
        self.mute_action.triggered.connect(self.toggle_mute)
        menu.addAction(self.mute_action)

        # Settings
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()

        # Restart
        restart_action = QAction("Restart", self)
        restart_action.triggered.connect(self.restart_requested.emit)
        menu.addAction(restart_action)

        # Quit
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

    def toggle_pause(self) -> None:
        self.is_paused = self.pause_action.isChecked()
        self.pause_toggled.emit(self.is_paused)
        if self.is_paused:
            self.tray_icon.setToolTip("NekoDesk (Paused)")
        else:
            self.tray_icon.setToolTip("NekoDesk")

    def toggle_mute(self) -> None:
        muted = self.mute_action.isChecked()
        self.sound_manager.set_mute(muted)

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.parent_widget)
        dialog.settings_changed.connect(self.on_settings_saved)
        dialog.exec()

    def on_settings_saved(self) -> None:
        # Sync volume slider change directly back into SoundManager
        vol = Settings().get("volume")
        self.sound_manager.set_volume(vol)
        self.settings_updated.emit()
