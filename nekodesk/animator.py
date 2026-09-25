import os
from typing import Dict, List
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from states import CatState
from config import Settings

class Animator:
    def __init__(self, base_path: str):
        self.settings = Settings()
        self.sprite_dir = os.path.join(base_path, "assets", "sprites")
        self.cache: Dict[CatState, List[QPixmap]] = {}
        self.load_all_sprites()

    def get_state_folder(self, state: CatState) -> str:
        return state.name.lower()

    def load_all_sprites(self) -> None:
        for state in CatState:
            folder_name = self.get_state_folder(state)
            folder_path = os.path.join(self.sprite_dir, folder_name)
            
            self.cache[state] = []
            if not os.path.exists(folder_path):
                print(f"Warning: Sprite folder not found for {state.name}: {folder_path}")
                continue

            try:
                files = [f for f in os.listdir(folder_path) if f.lower().endswith(".png")]
                # Sort numerically by filename e.g. "0.png", "1.png"
                files.sort(key=lambda x: int(os.path.splitext(x)[0]))
            except Exception as e:
                print(f"Error reading directory {folder_path}: {e}")
                continue

            for file in files:
                img_path = os.path.join(folder_path, file)
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    self.cache[state].append(pixmap)
                else:
                    print(f"Failed to load image: {img_path}")

            print(f"Loaded {len(self.cache[state])} frames for {state.name}")

    def get_frame(self, state: CatState, frame_index: int, flipped: bool = False, scale: float = 1.0) -> QPixmap:
        frames = self.cache.get(state, [])
        if not frames:
            # Return an empty transparent QPixmap as a fallback
            fallback = QPixmap(128, 128)
            fallback.fill(Qt.GlobalColor.transparent)
            return fallback

        frame = frames[frame_index % len(frames)]
        
        # Determine scale factor
        config_scale = self.settings.get("cat_scale")
        final_scale = scale * config_scale
        
        if final_scale != 1.0:
            w = int(frame.width() * final_scale)
            h = int(frame.height() * final_scale)
            if w > 0 and h > 0:
                frame = frame.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        if flipped:
            image = frame.toImage()
            flipped_image = image.mirrored(True, False)
            frame = QPixmap.fromImage(flipped_image)

        return frame

    def get_frame_count(self, state: CatState) -> int:
        return len(self.cache.get(state, []))
