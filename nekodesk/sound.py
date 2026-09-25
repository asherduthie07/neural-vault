import os
from PySide6.QtCore import QObject, QUrl
try:
    from PySide6.QtMultimedia import QSoundEffect
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    MULTIMEDIA_AVAILABLE = False
    print("Warning: PySide6.QtMultimedia not available. Sounds will be disabled.")

from config import Settings

class SoundManager(QObject):
    def __init__(self, base_path: str):
        super().__init__()
        self.settings = Settings()
        self.audio_dir = os.path.join(base_path, "assets", "audio")
        self.effects = {}
        self.sound_names = ["meow", "purr", "hiss", "snore"]
        self.muted = False
        
        if MULTIMEDIA_AVAILABLE:
            for name in self.sound_names:
                path = os.path.join(self.audio_dir, f"{name}.wav")
                if os.path.exists(path):
                    try:
                        effect = QSoundEffect()
                        effect.setSource(QUrl.fromLocalFile(path))
                        # Loop purr and snore infinitely or until stopped
                        if name in ("purr", "snore"):
                            effect.setLoopCount(QSoundEffect.Loop.Infinite)
                        else:
                            effect.setLoopCount(1)
                        
                        vol = self.settings.get("volume") / 100.0
                        effect.setVolume(vol)
                        self.effects[name] = effect
                    except Exception as e:
                        print(f"Error loading sound {name}: {e}")
        else:
            print("Sound playback is disabled due to missing PySide6.QtMultimedia module.")

    def play(self, name: str) -> None:
        if self.muted or not MULTIMEDIA_AVAILABLE or name not in self.effects:
            return
        
        # Stop background looping sounds when active states change
        if name in ("meow", "hiss"):
            self.stop("snore")
            self.stop("purr")
            
        try:
            vol = self.settings.get("volume") / 100.0
            self.effects[name].setVolume(vol)
            # Only play if it is not already playing to prevent stutter
            if not self.effects[name].isPlaying():
                self.effects[name].play()
        except Exception as e:
            print(f"Error playing sound {name}: {e}")

    def stop(self, name: str) -> None:
        if not MULTIMEDIA_AVAILABLE or name not in self.effects:
            return
        try:
            if self.effects[name].isPlaying():
                self.effects[name].stop()
        except Exception as e:
            print(f"Error stopping sound {name}: {e}")

    def stop_all(self) -> None:
        for name in self.effects:
            self.stop(name)

    def set_volume(self, volume: int) -> None:
        self.settings.set("volume", volume)
        vol_float = volume / 100.0
        if MULTIMEDIA_AVAILABLE:
            for effect in self.effects.values():
                try:
                    effect.setVolume(vol_float)
                except Exception:
                    pass

    def set_mute(self, mute: bool) -> None:
        self.muted = mute
        if mute:
            self.stop_all()
