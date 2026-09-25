import random
from typing import Tuple, Optional
from states import CatState

class BehaviorScheduler:
    def __init__(self) -> None:
        self.state_timer: float = 0.0
        self.state_duration: float = 3.0
        self.walk_target_x: Optional[float] = None
        self.zoom_target_x: Optional[float] = None
        self.inactivity_timer: float = 0.0
        self.idle_trigger_sleep_time: float = 45.0  # 45 seconds of idle/sitting triggers sleep

    def select_random_state(self, current_x: float, screen_width: int) -> CatState:
        # Weighted options
        choices = [
            (CatState.IDLE, 25),
            (CatState.SIT, 25),
            (CatState.WALK_LEFT if current_x > 150 else CatState.WALK_RIGHT, 15),
            (CatState.WALK_RIGHT if current_x < screen_width - 250 else CatState.WALK_LEFT, 15),
            (CatState.HAPPY, 12),
            (CatState.ANGRY, 3),
            (CatState.SLEEP, 5)
        ]
        
        states, weights = zip(*choices)
        selected = random.choices(states, weights=weights, k=1)[0]
        return selected

    def trigger_zoom(self, current_x: float, screen_width: int) -> Tuple[CatState, float]:
        # Cat zooms to the other side of screen
        self.state_timer = 0.0
        self.state_duration = random.uniform(1.5, 3.0)
        if current_x > screen_width / 2:
            self.zoom_target_x = random.uniform(50.0, 200.0)
            return CatState.WALK_LEFT, self.state_duration
        else:
            self.zoom_target_x = random.uniform(screen_width - 300.0, screen_width - 150.0)
            return CatState.WALK_RIGHT, self.state_duration

    def update(self, current_state: CatState, dt: float, current_x: float, screen_width: int) -> Tuple[CatState, float]:
        self.state_timer += dt
        
        # Inactivity sleep trigger:
        if current_state in (CatState.IDLE, CatState.SIT):
            self.inactivity_timer += dt
            if self.inactivity_timer >= self.idle_trigger_sleep_time:
                self.inactivity_timer = 0.0
                self.state_timer = 0.0
                self.state_duration = random.uniform(20.0, 40.0)
                return CatState.SLEEP, self.state_duration
        else:
            self.inactivity_timer = 0.0

        # Sleep state keeps running until duration is up or user interacts
        if current_state == CatState.SLEEP:
            if self.state_timer >= self.state_duration:
                # Wake up happy
                self.state_timer = 0.0
                self.state_duration = 3.0
                return CatState.HAPPY, self.state_duration
            return CatState.SLEEP, self.state_duration

        # Zoom state override
        if self.zoom_target_x is not None:
            dist = abs(current_x - self.zoom_target_x)
            if dist < 10 or self.state_timer >= self.state_duration:
                self.zoom_target_x = None
                self.state_timer = 0.0
                self.state_duration = 2.0
                return CatState.SIT, self.state_duration
            # Keep zoom walking state
            target_state = CatState.WALK_LEFT if self.zoom_target_x < current_x else CatState.WALK_RIGHT
            return target_state, self.state_duration

        # Standard walk target completion check
        if self.walk_target_x is not None:
            dist = abs(current_x - self.walk_target_x)
            if dist < 10 or self.state_timer >= self.state_duration:
                self.walk_target_x = None
                self.state_timer = 0.0
                self.state_duration = random.uniform(2.0, 4.0)
                # Randomly sit or lick paw
                return random.choice([CatState.IDLE, CatState.SIT, CatState.HAPPY]), self.state_duration
            # Keep walking state
            target_state = CatState.WALK_LEFT if self.walk_target_x < current_x else CatState.WALK_RIGHT
            return target_state, self.state_duration

        # Switch state when timer expires
        if self.state_timer >= self.state_duration:
            # 5% chance to trigger zoom
            if random.random() < 0.08:
                return self.trigger_zoom(current_x, screen_width)
            
            self.state_timer = 0.0
            next_state = self.select_random_state(current_x, screen_width)
            
            if next_state in (CatState.WALK_LEFT, CatState.WALK_RIGHT):
                walk_dist = random.uniform(120.0, 350.0)
                if next_state == CatState.WALK_LEFT:
                    self.walk_target_x = max(50.0, current_x - walk_dist)
                else:
                    self.walk_target_x = min(screen_width - 200.0, current_x + walk_dist)
                self.state_duration = random.uniform(3.0, 7.0)
            elif next_state == CatState.SLEEP:
                self.state_duration = random.uniform(20.0, 50.0)
            else:
                self.state_duration = random.uniform(2.0, 5.0)
                
            return next_state, self.state_duration

        return current_state, self.state_duration
