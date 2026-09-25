from typing import Tuple
from PySide6.QtCore import QRect
from PySide6.QtGui import QPixmap
from states import CatState
from physics import PhysicsEngine
from animator import Animator
from sound import SoundManager
from behaviors import BehaviorScheduler
from interaction import InteractionHandler

class Cat:
    def __init__(self, base_path: str):
        # Systems
        self.physics = PhysicsEngine()
        self.animator = Animator(base_path)
        self.sound_manager = SoundManager(base_path)
        self.behavior_scheduler = BehaviorScheduler()
        self.interaction_handler = InteractionHandler(self.sound_manager)
        
        # State
        self.state: CatState = CatState.FALL
        self.facing_left: bool = False
        
        # Animation parameters
        self.frame_index: int = 0
        self.frame_timer: float = 0.0
        
        # Set size in physics to match default sprite scale
        self.update_dimensions()

    def update_dimensions(self) -> None:
        # Get frame 0 of idle state to determine size
        pix = self.animator.get_frame(CatState.IDLE, 0)
        self.physics.set_size(pix.width(), pix.height())

    def get_fps_for_state(self, state: CatState) -> float:
        if state in (CatState.WALK_LEFT, CatState.WALK_RIGHT):
            return 10.0
        elif state == CatState.CHASE_CURSOR:
            return 12.0
        elif state == CatState.SLEEP:
            return 1.5
        elif state in (CatState.IDLE, CatState.LAND):
            return 5.0
        elif state == CatState.SIT:
            return 4.0
        elif state in (CatState.JUMP, CatState.FALL, CatState.DRAGGED):
            return 8.0
        elif state in (CatState.HAPPY, CatState.ANGRY):
            return 8.0
        return 6.0

    def set_state(self, new_state: CatState) -> None:
        if self.state == new_state:
            return

        # Sound triggers and background cleanups
        self.sound_manager.stop("snore")
        self.sound_manager.stop("purr")

        if new_state == CatState.SLEEP:
            self.sound_manager.play("snore")
        elif new_state == CatState.HAPPY:
            self.sound_manager.play("purr")
        elif new_state == CatState.ANGRY:
            self.sound_manager.play("hiss")

        self.state = new_state
        self.frame_index = 0
        self.frame_timer = 0.0

    def update(self, dt: float, screen_rect: QRect, paused: bool = False) -> None:
        # If paused, freeze updates
        if paused:
            self.physics.vx = 0
            self.physics.vy = 0
            self.physics.update(screen_rect)
            return

        # 1. Update Interaction Engine
        self.interaction_handler.update(self, dt)

        # 2. Update Physics
        self.physics.update(screen_rect)

        # 3. Handle land / fall transition
        if not self.physics.is_dragged:
            if not self.physics.grounded and self.physics.vy > 0 and self.state not in (CatState.JUMP, CatState.FALL):
                self.set_state(CatState.FALL)
            elif self.physics.grounded and self.state == CatState.FALL:
                self.set_state(CatState.LAND)
            elif self.state == CatState.LAND and self.frame_index >= self.animator.get_frame_count(CatState.LAND) - 1:
                self.set_state(CatState.IDLE)

        # 4. Update Behavior Scheduler
        if self.physics.grounded and self.state not in (CatState.DRAGGED, CatState.LAND, CatState.CHASE_CURSOR):
            next_state, duration = self.behavior_scheduler.update(self.state, dt, self.physics.x, screen_rect.width())
            self.set_state(next_state)

        # 5. Determine orientation facing
        # Force correct walk states based on physics velocity
        if self.state in (CatState.WALK_LEFT, CatState.WALK_RIGHT):
            if self.physics.vx < 0:
                self.set_state(CatState.WALK_LEFT)
                self.facing_left = True
            elif self.physics.vx > 0:
                self.set_state(CatState.WALK_RIGHT)
                self.facing_left = False
        else:
            if self.physics.vx < -0.2:
                self.facing_left = True
            elif self.physics.vx > 0.2:
                self.facing_left = False

        # 6. Update Frame pacing
        fps = self.get_fps_for_state(self.state)
        frame_duration = 1.0 / fps
        self.frame_timer += dt
        if self.frame_timer >= frame_duration:
            self.frame_timer -= frame_duration
            self.frame_index += 1
            
            # Loop check
            num_frames = self.animator.get_frame_count(self.state)
            if num_frames > 0:
                self.frame_index %= num_frames

    def get_current_pixmap(self) -> QPixmap:
        # Flipped check
        # Walk left uses pre-generated flipped sprites, but we double-guard it
        is_left_walk = (self.state == CatState.WALK_LEFT)
        flip_required = self.facing_left and not is_left_walk
        
        return self.animator.get_frame(self.state, self.frame_index, flipped=flip_required)
