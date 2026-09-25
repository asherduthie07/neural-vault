import time
import random
from typing import Tuple, Optional
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QCursor, QMouseEvent
from states import CatState
from physics import PhysicsEngine
from sound import SoundManager

class InteractionHandler:
    def __init__(self, sound_manager: SoundManager):
        self.sound_manager: SoundManager = sound_manager
        
        # Cursor tracking
        self.last_cursor_pos: QPoint = QPoint(0, 0)
        self.cursor_still_time: float = 0.0
        self.chase_cooldown: float = 0.0
        
        # Drag mechanics
        self.drag_start_pos: QPoint = QPoint(0, 0)
        self.drag_last_pos: QPoint = QPoint(0, 0)
        self.drag_history: list[Tuple[float, QPoint]] = [] # list of (time, pos) for velocity calculation

    def update(self, cat, dt: float) -> None:
        if cat.physics.is_dragged:
            # We record cursor positions to compute throw velocity
            curr_time = time.time()
            curr_pos = QCursor.pos()
            self.drag_history.append((curr_time, curr_pos))
            # Keep history short (last 100ms)
            self.drag_history = [(t, p) for t, p in self.drag_history if curr_time - t < 0.1]
            return

        # Check cursor movement
        current_cursor = QCursor.pos()
        dx = current_cursor.x() - self.last_cursor_pos.x()
        dy = current_cursor.y() - self.last_cursor_pos.y()
        cursor_moved = (abs(dx) > 3 or abs(dy) > 3)
        self.last_cursor_pos = current_cursor

        if cursor_moved:
            self.cursor_still_time = 0.0
        else:
            if cat.physics.grounded:
                self.cursor_still_time += dt

        # Cooldown update
        if self.chase_cooldown > 0:
            self.chase_cooldown -= dt

        # Proximity check
        cat_center_x = cat.physics.x + cat.physics.width / 2
        cat_center_y = cat.physics.y + cat.physics.height / 2
        dist_x = current_cursor.x() - cat_center_x
        dist_y = current_cursor.y() - cat_center_y
        distance = (dist_x**2 + dist_y**2)**0.5

        # Pounce behavior: Cursor still for 2.0+ seconds, cat is close (within 400px), and cat is sitting/idle
        if (self.cursor_still_time >= 2.0 and 
            distance < 400.0 and 
            cat.physics.grounded and 
            cat.state in (CatState.IDLE, CatState.SIT, CatState.HAPPY)):
            
            # Reset still timer so we don't jump continuously
            self.cursor_still_time = -3.0 # negative cooldown
            
            # Calculate leap velocity
            # Target is the cursor
            self.sound_manager.play("meow")
            cat.state = CatState.JUMP
            # Leap towards cursor
            vx_impulse = dist_x / 18.0
            vy_impulse = -8.0 if dist_y >= 0 else (dist_y / 15.0 - 5.0)
            # Clip impulse values
            vx_impulse = max(-10.0, min(10.0, vx_impulse))
            vy_impulse = max(-12.0, min(-5.0, vy_impulse))
            
            cat.physics.apply_impulse(vx_impulse, vy_impulse)
            return

        # Cursor chasing curiosity check
        if (cursor_moved and 
            self.chase_cooldown <= 0.0 and 
            distance < 600.0 and 
            cat.physics.grounded and 
            cat.state in (CatState.IDLE, CatState.SIT)):
            
            # 5% chance to start chasing the cursor
            if random.random() < 0.05:
                cat.state = CatState.CHASE_CURSOR
                self.chase_cooldown = 15.0 # Cooldown between chases

        # Chasing cursor update
        if cat.state == CatState.CHASE_CURSOR:
            # Move towards cursor X
            target_x = current_cursor.x() - cat.physics.width / 2
            walk_speed = 3.5 # faster than walking
            
            if abs(dist_x) < 40:
                # Arrived at cursor!
                cat.state = CatState.HAPPY
                self.sound_manager.play("purr")
                cat.physics.vx = 0.0
            else:
                # Walk towards cursor
                if dist_x < 0:
                    cat.state = CatState.WALK_LEFT
                    cat.physics.vx = -walk_speed
                else:
                    cat.state = CatState.WALK_RIGHT
                    cat.physics.vx = walk_speed

    def handle_mouse_press(self, cat, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            cat.physics.is_dragged = True
            cat.state = CatState.DRAGGED
            cat.physics.vx = 0.0
            cat.physics.vy = 0.0
            self.drag_start_pos = event.globalPosition().toPoint()
            self.drag_last_pos = self.drag_start_pos
            self.drag_history = [(time.time(), self.drag_start_pos)]
            self.sound_manager.play("purr")

    def handle_mouse_move(self, cat, event: QMouseEvent) -> None:
        if cat.physics.is_dragged:
            curr_pos = event.globalPosition().toPoint()
            delta = curr_pos - self.drag_last_pos
            
            # Move the window
            cat.physics.x += delta.x()
            cat.physics.y += delta.y()
            self.drag_last_pos = curr_pos

    def handle_mouse_release(self, cat, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and cat.physics.is_dragged:
            cat.physics.is_dragged = False
            self.sound_manager.stop("purr")
            
            # Compute throw velocity based on drag history
            if len(self.drag_history) >= 2:
                t1, p1 = self.drag_history[0]
                t2, p2 = self.drag_history[-1]
                dt = t2 - t1
                if dt > 0.01:
                    vx = (p2.x() - p1.x()) / (dt * 60.0) # convert to pixels/frame (at 60fps)
                    vy = (p2.y() - p1.y()) / (dt * 60.0)
                    
                    # Clamp velocities
                    vx = max(-15.0, min(15.0, vx))
                    vy = max(-15.0, min(15.0, vy))
                    
                    cat.physics.apply_impulse(vx, vy)
                    
                    if abs(vx) > 8.0 or abs(vy) > 8.0:
                        cat.state = CatState.FALL
                        self.sound_manager.play("hiss")
                        return

            cat.state = CatState.FALL
            self.sound_manager.play("meow")

    def handle_double_click(self, cat, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            cat.state = CatState.HAPPY
            self.sound_manager.play("meow")
            
    def handle_hover(self, cat, entered: bool) -> None:
        if entered and cat.physics.grounded and cat.state in (CatState.IDLE, CatState.SIT):
            cat.state = CatState.HAPPY
            self.sound_manager.play("purr")
        elif not entered and cat.state == CatState.HAPPY:
            self.sound_manager.stop("purr")
            cat.state = CatState.IDLE
