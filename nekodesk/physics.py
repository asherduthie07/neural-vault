import sys
from typing import Tuple, Optional
from PySide6.QtCore import QRect

class PhysicsEngine:
    def __init__(self, x: float = 0, y: float = 0, width: int = 128, height: int = 128):
        self.x: float = x
        self.y: float = y
        self.width: int = width
        self.height: int = height
        
        self.vx: float = 0.0
        self.vy: float = 0.0
        
        # Physics constants
        self.gravity: float = 0.6
        self.friction: float = 0.88
        self.terminal_velocity: float = 16.0
        self.bounce_coefficient: float = 0.4
        
        self.grounded: bool = False
        self.is_dragged: bool = False
        
        # Platform window collision settings
        self.enable_window_collision: bool = False
        self.active_window_rect: Optional[QRect] = None

    def update(self, screen_rect: QRect) -> None:
        if self.is_dragged:
            self.grounded = False
            return

        # Apply gravity if not grounded
        if not self.grounded:
            self.vy += self.gravity
            if self.vy > self.terminal_velocity:
                self.vy = self.terminal_velocity
        else:
            self.vy = 0.0
            # Apply friction on ground
            self.vx *= self.friction
            if abs(self.vx) < 0.1:
                self.vx = 0.0

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Floor detection (Standard Desktop Bottom)
        floor_y = screen_rect.height() - self.height
        
        # Windows platform-specific window-collision check
        on_window = False
        if self.enable_window_collision and self.active_window_rect:
            win = self.active_window_rect
            # Check if cat is vertically near the top of the window
            # and horizontally within the window boundaries
            cat_bottom = self.y + self.height
            cat_center_x = self.x + self.width / 2
            
            # We treat the top edge of active window as a floor
            if (win.left() <= cat_center_x <= win.right()) and (abs(cat_bottom - win.top()) <= 8) and self.vy >= 0:
                self.y = win.top() - self.height
                self.vy = 0.0
                on_window = True
                self.grounded = True

        if not on_window:
            if self.y >= floor_y:
                self.y = floor_y
                self.vy = 0.0
                self.grounded = True
            else:
                self.grounded = False

        # Collision with Screen Boundaries (Left / Right / Top)
        if self.x < screen_rect.left():
            self.x = screen_rect.left()
            self.vx = -self.vx * self.bounce_coefficient
        elif self.x > screen_rect.right() - self.width:
            self.x = screen_rect.right() - self.width
            self.vx = -self.vx * self.bounce_coefficient

        if self.y < screen_rect.top():
            self.y = screen_rect.top()
            self.vy = 0.0 # Slide down if hitting ceiling

    def set_position(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def set_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def apply_impulse(self, vx: float, vy: float) -> None:
        self.vx = vx
        self.vy = vy
        self.grounded = False

    def check_walk_off_edge(self, screen_rect: QRect) -> None:
        # If sitting on a window and walking off, trigger fall
        if self.grounded and self.y < screen_rect.height() - self.height:
            # Check if still on the active window
            if self.enable_window_collision and self.active_window_rect:
                win = self.active_window_rect
                cat_center_x = self.x + self.width / 2
                if not (win.left() <= cat_center_x <= win.right()):
                    self.grounded = False
