import os
import math
import struct
import wave
from PIL import Image, ImageDraw

def create_dirs(base_path):
    states = [
        "idle", "walk_left", "walk_right", "sleep", "sit", 
        "jump", "fall", "land", "chase_cursor", "dragged", "happy", "angry"
    ]
    for state in states:
        os.makedirs(os.path.join(base_path, "assets", "sprites", state), exist_ok=True)
    os.makedirs(os.path.join(base_path, "assets", "audio"), exist_ok=True)

def draw_heart(draw, x, y, size=10):
    # Cute little heart shape
    draw.polygon([
        (x, y), 
        (x - size//2, y - size//2), 
        (x - size//2, y - size), 
        (x, y - size//2), 
        (x + size//2, y - size), 
        (x + size//2, y - size//2)
    ], fill=(255, 64, 129))

def draw_z(draw, x, y, size=8):
    # Draw a cute 'Z'
    draw.line([(x, y), (x + size, y)], fill=(120, 180, 255), width=2)
    draw.line([(x + size, y), (x, y + size)], fill=(120, 180, 255), width=2)
    draw.line([(x, y + size), (x + size, y + size)], fill=(120, 180, 255), width=2)

def generate_sprites(base_path):
    sprite_dir = os.path.join(base_path, "assets", "sprites")
    
    # Colors
    ORANGE = (255, 145, 0)
    DARK_ORANGE = (230, 81, 0)
    WHITE = (255, 255, 255)
    PINK = (255, 128, 171)
    BLACK = (33, 33, 33)
    RED = (244, 67, 54)
    
    # Let's generate sprites frame-by-frame
    # We will define helper drawing steps for a 128x128 canvas
    
    # 1. IDLE (4 frames)
    for frame in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Tail
        tail_y_offset = -4 if frame in (1, 3) else 0
        draw.ellipse([20, 60 + tail_y_offset, 36, 95 + tail_y_offset], fill=ORANGE)
        draw.ellipse([24, 56 + tail_y_offset, 32, 70 + tail_y_offset], fill=WHITE)
        
        # Legs
        draw.ellipse([45, 95, 58, 115], fill=ORANGE) # Back leg
        draw.ellipse([48, 110, 60, 118], fill=WHITE) # Back paw
        draw.ellipse([70, 95, 83, 115], fill=ORANGE) # Front leg
        draw.ellipse([73, 110, 85, 118], fill=WHITE) # Front paw
        
        # Body
        draw.ellipse([35, 60, 85, 105], fill=ORANGE)
        draw.ellipse([45, 65, 75, 95], fill=DARK_ORANGE) # Cute stripes
        
        # Head
        draw.ellipse([65, 40, 105, 80], fill=ORANGE)
        # Chest/Snout white bib
        draw.ellipse([75, 65, 95, 80], fill=WHITE)
        
        # Ears
        draw.polygon([(68, 48), (62, 28), (78, 42)], fill=ORANGE)
        draw.polygon([(70, 46), (65, 32), (76, 42)], fill=PINK) # Left ear
        
        draw.polygon([(92, 42), (108, 28), (102, 48)], fill=ORANGE)
        draw.polygon([(94, 42), (105, 32), (100, 46)], fill=PINK) # Right ear
        
        # Eyes
        if frame == 1: # Blink
            draw.line([(80, 56), (88, 56)], fill=BLACK, width=2)
            draw.line([(92, 56), (100, 56)], fill=BLACK, width=2)
        else:
            draw.ellipse([81, 52, 87, 58], fill=BLACK)
            draw.ellipse([93, 52, 99, 58], fill=BLACK)
            # Glint
            draw.ellipse([82, 53, 84, 55], fill=WHITE)
            draw.ellipse([94, 53, 96, 55], fill=WHITE)
            
        # Nose
        draw.polygon([(88, 60), (92, 60), (90, 62)], fill=PINK)
        # Mouth
        draw.arc([86, 61, 90, 65], start=0, end=180, fill=BLACK, width=1)
        draw.arc([90, 61, 94, 65], start=0, end=180, fill=BLACK, width=1)
        
        img.save(os.path.join(sprite_dir, "idle", f"{frame}.png"))
        
    # 2. WALK RIGHT (4 frames)
    for frame in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Bobbing
        bob = -4 if frame in (0, 2) else 0
        
        # Tail
        tail_angle = 5 if frame in (0, 1) else -5
        draw.ellipse([20 + tail_angle, 60 + bob, 36 + tail_angle, 95 + bob], fill=ORANGE)
        draw.ellipse([24 + tail_angle, 56 + bob, 32 + tail_angle, 70 + bob], fill=WHITE)
        
        # Legs walking animation
        leg_offset = 8 if frame == 0 else (-8 if frame == 2 else 0)
        # Back leg 1
        draw.ellipse([40 + leg_offset, 95, 53 + leg_offset, 115], fill=ORANGE)
        draw.ellipse([43 + leg_offset, 110, 55 + leg_offset, 118], fill=WHITE)
        # Back leg 2
        draw.ellipse([55 - leg_offset, 95, 68 - leg_offset, 115], fill=DARK_ORANGE)
        draw.ellipse([58 - leg_offset, 110, 70 - leg_offset, 118], fill=WHITE)
        # Front leg 1
        draw.ellipse([70 + leg_offset, 95, 83 + leg_offset, 115], fill=ORANGE)
        draw.ellipse([73 + leg_offset, 110, 85 + leg_offset, 118], fill=WHITE)
        # Front leg 2
        draw.ellipse([80 - leg_offset, 95, 93 - leg_offset, 115], fill=DARK_ORANGE)
        draw.ellipse([83 - leg_offset, 110, 95 - leg_offset, 118], fill=WHITE)
        
        # Body
        draw.ellipse([35, 60 + bob, 85, 105 + bob], fill=ORANGE)
        # Head
        draw.ellipse([65, 40 + bob, 105, 80 + bob], fill=ORANGE)
        draw.ellipse([75, 65 + bob, 95, 80 + bob], fill=WHITE)
        
        # Ears
        draw.polygon([(68, 48 + bob), (62, 28 + bob), (78, 42 + bob)], fill=ORANGE)
        draw.polygon([(70, 46 + bob), (65, 32 + bob), (76, 42 + bob)], fill=PINK)
        draw.polygon([(92, 42 + bob), (108, 28 + bob), (102, 48 + bob)], fill=ORANGE)
        draw.polygon([(94, 42 + bob), (105, 32 + bob), (100, 46 + bob)], fill=PINK)
        
        # Eyes
        draw.ellipse([81, 52 + bob, 87, 58 + bob], fill=BLACK)
        draw.ellipse([93, 52 + bob, 99, 58 + bob], fill=BLACK)
        draw.ellipse([82, 53 + bob, 84, 55 + bob], fill=WHITE)
        draw.ellipse([94, 53 + bob, 96, 55 + bob], fill=WHITE)
        
        # Nose
        draw.polygon([(88, 60 + bob), (92, 60 + bob), (90, 62 + bob)], fill=PINK)
        # Mouth
        draw.arc([86, 61 + bob, 90, 65 + bob], start=0, end=180, fill=BLACK, width=1)
        draw.arc([90, 61 + bob, 94, 65 + bob], start=0, end=180, fill=BLACK, width=1)
        
        img.save(os.path.join(sprite_dir, "walk_right", f"{frame}.png"))
        
        # Save flipped for walk_left
        left_img = img.transpose(Image.FLIP_LEFT_RIGHT)
        left_img.save(os.path.join(sprite_dir, "walk_left", f"{frame}.png"))

    # 3. SLEEP (4 frames)
    for frame in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Breathing scale
        breathe = 2 if frame in (0, 1) else 0
        
        # Tail wrapped
        draw.ellipse([30, 85, 60, 115], fill=ORANGE)
        draw.ellipse([32, 90, 45, 112], fill=WHITE)
        
        # Tucked body
        draw.ellipse([35, 70 - breathe, 95, 115], fill=ORANGE)
        draw.ellipse([45, 75 - breathe, 85, 105], fill=DARK_ORANGE)
        
        # Low head
        draw.ellipse([70, 75, 105, 110], fill=ORANGE)
        
        # Low ears
        draw.polygon([(75, 80), (68, 65), (82, 78)], fill=ORANGE)
        draw.polygon([(77, 79), (72, 69), (81, 78)], fill=PINK)
        draw.polygon([(92, 78), (102, 65), (98, 80)], fill=ORANGE)
        draw.polygon([(93, 78), (99, 69), (97, 80)], fill=PINK)
        
        # Closed eyes
        draw.line([(80, 92), (86, 95)], fill=BLACK, width=2)
        draw.line([(92, 95), (98, 92)], fill=BLACK, width=2)
        
        # Nose
        draw.polygon([(88, 97), (92, 97), (90, 99)], fill=PINK)
        
        # Zzz bubble rising
        if frame == 1:
            draw_z(draw, 100, 50, size=6)
        elif frame == 2:
            draw_z(draw, 105, 38, size=10)
        elif frame == 3:
            draw_z(draw, 112, 26, size=14)
            
        img.save(os.path.join(sprite_dir, "sleep", f"{frame}.png"))

    # 4. SIT (4 frames)
    for frame in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Tail wags close to ground
        twag = 2 if frame in (1, 3) else 0
        draw.ellipse([20 + twag, 90, 45, 115], fill=ORANGE)
        draw.ellipse([22, 95, 32, 105], fill=WHITE)
        
        # Body upright
        draw.ellipse([45, 65, 83, 115], fill=ORANGE)
        # Front legs straight down
        draw.ellipse([64, 95, 74, 118], fill=ORANGE)
        draw.ellipse([66, 112, 74, 118], fill=WHITE)
        draw.ellipse([74, 95, 84, 118], fill=ORANGE)
        draw.ellipse([76, 112, 84, 118], fill=WHITE)
        
        # Head centered higher
        draw.ellipse([54, 38, 94, 78], fill=ORANGE)
        draw.ellipse([64, 63, 84, 78], fill=WHITE)
        
        # Ears upright
        draw.polygon([(56, 46), (50, 26), (66, 40)], fill=ORANGE)
        draw.polygon([(58, 44), (53, 30), (64, 40)], fill=PINK)
        draw.polygon([(82, 40), (98, 26), (92, 46)], fill=ORANGE)
        draw.polygon([(84, 40), (95, 30), (90, 44)], fill=PINK)
        
        # Eyes looking at you
        draw.ellipse([64, 52, 70, 58], fill=BLACK)
        draw.ellipse([78, 52, 84, 58], fill=BLACK)
        draw.ellipse([65, 53, 67, 55], fill=WHITE)
        draw.ellipse([79, 53, 81, 55], fill=WHITE)
        
        draw.polygon([(70, 60), (74, 60), (72, 62)], fill=PINK)
        draw.arc([68, 61, 72, 65], start=0, end=180, fill=BLACK, width=1)
        draw.arc([72, 61, 76, 65], start=0, end=180, fill=BLACK, width=1)
        
        img.save(os.path.join(sprite_dir, "sit", f"{frame}.png"))

    # 5. JUMP (2 frames)
    for frame in range(2):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Jump 0 is launch (pushing up), Jump 1 is mid-air (tucked)
        is_mid = frame == 1
        
        # Tail pointing down-back
        draw.ellipse([15, 75 if is_mid else 85, 35, 110 if is_mid else 120], fill=ORANGE)
        
        # Body stretched
        draw.ellipse([30, 45 if is_mid else 55, 80, 95 if is_mid else 105], fill=ORANGE)
        
        # Legs extended
        if not is_mid: # pushing off
            draw.ellipse([35, 95, 48, 122], fill=ORANGE)
            draw.ellipse([65, 95, 78, 122], fill=ORANGE)
        else: # tucked
            draw.ellipse([40, 85, 52, 105], fill=ORANGE)
            draw.ellipse([60, 85, 72, 105], fill=ORANGE)
            
        # Head high and forward
        draw.ellipse([65, 30 if is_mid else 40, 105, 70 if is_mid else 80], fill=ORANGE)
        draw.ellipse([75, 55 if is_mid else 65, 95, 70 if is_mid else 80], fill=WHITE)
        
        # Ears back
        draw.polygon([(68, 38 if is_mid else 48), (60, 23 if is_mid else 33), (76, 35 if is_mid else 45)], fill=ORANGE)
        draw.polygon([(90, 35 if is_mid else 45), (98, 23 if is_mid else 33), (96, 38 if is_mid else 48)], fill=ORANGE)
        
        # Determined eyes
        draw.ellipse([82, 44 if is_mid else 54, 88, 50 if is_mid else 60], fill=BLACK)
        draw.ellipse([92, 44 if is_mid else 54, 98, 50 if is_mid else 60], fill=BLACK)
        
        img.save(os.path.join(sprite_dir, "jump", f"{frame}.png"))

    # 6. FALL (2 frames)
    for frame in range(2):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Tail floating up
        draw.ellipse([25, 35, 41, 75], fill=ORANGE)
        
        # Body vertical
        draw.ellipse([35, 50, 80, 100], fill=ORANGE)
        
        # Dangling legs
        leg_wig = 4 if frame == 1 else 0
        draw.ellipse([40 - leg_wig, 95, 50 - leg_wig, 120], fill=ORANGE)
        draw.ellipse([65 + leg_wig, 95, 75 + leg_wig, 120], fill=ORANGE)
        
        # Head looking down/worried
        draw.ellipse([50, 30, 90, 70], fill=ORANGE)
        draw.ellipse([60, 55, 80, 70], fill=WHITE)
        
        # Ears up, wide
        draw.polygon([(52, 38), (45, 18), (62, 34)], fill=ORANGE)
        draw.polygon([(78, 34), (85, 18), (88, 38)], fill=ORANGE)
        
        # Worried eyes (wide)
        draw.ellipse([62, 42, 70, 50], fill=BLACK)
        draw.ellipse([74, 42, 82, 50], fill=BLACK)
        
        img.save(os.path.join(sprite_dir, "fall", f"{frame}.png"))

    # 7. LAND (2 frames)
    for frame in range(2):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Squashed body
        crouch = 6 if frame == 0 else 2
        
        # Tail low
        draw.ellipse([20, 85, 45, 115], fill=ORANGE)
        
        # Squashed body
        draw.ellipse([35, 70 + crouch, 95, 115], fill=ORANGE)
        
        # Legs bent wide
        draw.ellipse([40, 105, 58, 118], fill=ORANGE)
        draw.ellipse([75, 105, 93, 118], fill=ORANGE)
        
        # Head low
        draw.ellipse([65, 55 + crouch, 105, 95 + crouch], fill=ORANGE)
        draw.ellipse([75, 80 + crouch, 95, 95 + crouch], fill=WHITE)
        
        # Ears
        draw.polygon([(68, 63 + crouch), (62, 43 + crouch), (78, 57 + crouch)], fill=ORANGE)
        draw.polygon([(92, 57 + crouch), (108, 43 + crouch), (102, 63 + crouch)], fill=ORANGE)
        
        # Eyes looking straight
        draw.ellipse([80, 68 + crouch, 86, 74 + crouch], fill=BLACK)
        draw.ellipse([92, 68 + crouch, 98, 74 + crouch], fill=BLACK)
        
        img.save(os.path.join(sprite_dir, "land", f"{frame}.png"))

    # 8. CHASE CURSOR (4 frames)
    for frame in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Low fast run, head forwards
        run_cycle = frame % 2
        head_bob = -2 if run_cycle == 0 else 2
        
        # Tail straight back
        draw.ellipse([10, 65, 40, 80], fill=ORANGE)
        draw.ellipse([10, 65, 20, 75], fill=WHITE)
        
        # Body stretched
        draw.ellipse([30, 60, 90, 100], fill=ORANGE)
        
        # Extended legs
        if run_cycle == 0:
            draw.ellipse([35, 90, 52, 115], fill=ORANGE)
            draw.ellipse([75, 90, 92, 115], fill=ORANGE)
        else:
            draw.ellipse([45, 90, 62, 115], fill=ORANGE)
            draw.ellipse([65, 90, 82, 115], fill=ORANGE)
            
        # Head low and forward
        draw.ellipse([75, 45 + head_bob, 115, 85 + head_bob], fill=ORANGE)
        draw.ellipse([85, 70 + head_bob, 105, 85 + head_bob], fill=WHITE)
        
        # Ears forward/flat
        draw.polygon([(78, 53 + head_bob), (72, 33 + head_bob), (88, 47 + head_bob)], fill=ORANGE)
        draw.polygon([(102, 47 + head_bob), (112, 33 + head_bob), (108, 53 + head_bob)], fill=ORANGE)
        
        # Big focused eyes
        draw.ellipse([91, 57 + head_bob, 97, 63 + head_bob], fill=BLACK)
        draw.ellipse([103, 57 + head_bob, 109, 63 + head_bob], fill=BLACK)
        
        img.save(os.path.join(sprite_dir, "chase_cursor", f"{frame}.png"))

    # 9. DRAGGED (4 frames)
    for frame in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Dangling stretched vertical cat
        wig = frame * 3
        
        # Tail wiggling wildly
        draw.ellipse([56 + (wig % 9) - 4, 15, 72 + (wig % 9) - 4, 50], fill=ORANGE)
        
        # Stretched body
        draw.ellipse([45, 45, 83, 105], fill=ORANGE)
        
        # Flailing paws
        p1 = 8 if frame in (0, 2) else -8
        p2 = -8 if frame in (0, 2) else 8
        draw.ellipse([35, 85 + p1, 50, 110 + p1], fill=ORANGE) # back left
        draw.ellipse([78, 85 + p2, 93, 110 + p2], fill=ORANGE) # back right
        draw.ellipse([40, 55 + p2, 52, 75 + p2], fill=WHITE)   # front left
        draw.ellipse([76, 55 + p1, 88, 75 + p1], fill=WHITE)   # front right
        
        # Dizzy head looking straight at screen
        draw.ellipse([49, 25, 89, 65], fill=ORANGE)
        draw.ellipse([59, 50, 79, 65], fill=WHITE)
        
        # Ears wide and dynamic
        draw.polygon([(51, 33), (42, 16), (61, 29)], fill=ORANGE)
        draw.polygon([(77, 29), (96, 16), (87, 33)], fill=ORANGE)
        
        # Dizzy X eyes or spiral
        if frame % 2 == 0:
            # X eyes
            draw.line([(58, 40), (64, 46)], fill=BLACK, width=2)
            draw.line([(64, 40), (58, 46)], fill=BLACK, width=2)
            draw.line([(74, 40), (80, 46)], fill=BLACK, width=2)
            draw.line([(80, 40), (74, 46)], fill=BLACK, width=2)
        else:
            # Spiral/swirl eyes
            draw.arc([57, 39, 65, 47], start=0, end=360, fill=BLACK, width=2)
            draw.arc([73, 39, 81, 47], start=0, end=360, fill=BLACK, width=2)
            
        img.save(os.path.join(sprite_dir, "dragged", f"{frame}.png"))

    # 10. HAPPY (4 frames)
    for frame in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Vibration/purr offset
        vib_x = 2 if frame in (0, 2) else -2
        vib_y = 1 if frame in (0, 1) else -1
        
        # Tail high and wagging
        twag = 6 if frame % 2 == 0 else -6
        draw.ellipse([20 + twag + vib_x, 40 + vib_y, 36 + twag + vib_x, 80 + vib_y], fill=ORANGE)
        
        # Body
        draw.ellipse([35 + vib_x, 60 + vib_y, 85 + vib_x, 105 + vib_y], fill=ORANGE)
        
        # Legs
        draw.ellipse([45 + vib_x, 95 + vib_y, 58 + vib_x, 115 + vib_y], fill=ORANGE)
        draw.ellipse([70 + vib_x, 95 + vib_y, 83 + vib_x, 115 + vib_y], fill=ORANGE)
        
        # Head
        draw.ellipse([65 + vib_x, 40 + vib_y, 105 + vib_x, 80 + vib_y], fill=ORANGE)
        draw.ellipse([75 + vib_x, 65 + vib_y, 95 + vib_x, 80 + vib_y], fill=WHITE)
        
        # Ears
        draw.polygon([(68+vib_x, 48+vib_y), (62+vib_x, 28+vib_y), (78+vib_x, 42+vib_y)], fill=ORANGE)
        draw.polygon([(92+vib_x, 42+vib_y), (108+vib_x, 28+vib_y), (102+vib_x, 48+vib_y)], fill=ORANGE)
        
        # Happy eyes (^ ^)
        draw.arc([78+vib_x, 50+vib_y, 86+vib_x, 58+vib_y], start=180, end=360, fill=BLACK, width=2)
        draw.arc([90+vib_x, 50+vib_y, 98+vib_x, 58+vib_y], start=180, end=360, fill=BLACK, width=2)
        
        # Mouth open smiling
        draw.polygon([(87+vib_x, 63+vib_y), (93+vib_x, 63+vib_y), (90+vib_x, 67+vib_y)], fill=PINK)
        
        # Hearts floating
        if frame == 1:
            draw_heart(draw, 100, 30, size=8)
        elif frame == 3:
            draw_heart(draw, 110, 20, size=10)
            
        img.save(os.path.join(sprite_dir, "happy", f"{frame}.png"))

    # 11. ANGRY (4 frames)
    for frame in range(4):
        img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Arched back, puffed tail
        back_arch = -6 if frame % 2 == 0 else -4
        
        # Puffed spiky tail
        draw.ellipse([15, 40 + back_arch, 38, 85 + back_arch], fill=DARK_ORANGE)
        draw.polygon([(10, 60), (20, 50), (15, 40)], fill=ORANGE) # Spikes
        draw.polygon([(25, 45), (35, 35), (30, 25)], fill=ORANGE)
        
        # Arched body
        draw.ellipse([35, 50 + back_arch, 85, 105], fill=ORANGE)
        draw.polygon([(50, 55 + back_arch), (60, 40 + back_arch), (70, 55 + back_arch)], fill=ORANGE) # Spiked back fur
        
        # Tense legs
        draw.ellipse([42, 90, 54, 116], fill=ORANGE)
        draw.ellipse([73, 90, 85, 116], fill=ORANGE)
        
        # Head low and tense
        draw.ellipse([68, 50, 108, 90], fill=ORANGE)
        draw.ellipse([78, 75, 98, 90], fill=WHITE)
        
        # Ears flat out sides
        draw.polygon([(70, 58), (56, 48), (76, 52)], fill=ORANGE)
        draw.polygon([(72, 57), (59, 50), (75, 52)], fill=PINK)
        draw.polygon([(96, 52), (110, 48), (100, 58)], fill=ORANGE)
        draw.polygon([(97, 52), (107, 50), (99, 57)], fill=PINK)
        
        # Angry eyes slanting inward
        draw.line([(80, 60), (87, 65)], fill=BLACK, width=2)
        draw.line([(96, 60), (89, 65)], fill=BLACK, width=2)
        draw.ellipse([81, 64, 85, 68], fill=RED)
        draw.ellipse([91, 64, 95, 68], fill=RED)
        
        # Mouth open hissing
        draw.polygon([(86, 73), (94, 73), (90, 78)], fill=BLACK)
        # Tiny fangs
        draw.polygon([(87, 73), (89, 73), (88, 75)], fill=WHITE)
        draw.polygon([(91, 73), (93, 73), (92, 75)], fill=WHITE)
        
        # Angry storm cloud or cross veins
        if frame in (1, 3):
            # Cross veins mark
            draw.line([(106, 30), (112, 36)], fill=RED, width=2)
            draw.line([(112, 30), (106, 36)], fill=RED, width=2)
            
        img.save(os.path.join(sprite_dir, "angry", f"{frame}.png"))

def synthesize_wav(filename, samples, sample_rate=22050):
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        for s in samples:
            s = max(-1.0, min(1.0, s))
            val = int(s * 32767)
            w.writeframes(struct.pack('<h', val))

def generate_audio(base_path):
    audio_dir = os.path.join(base_path, "assets", "audio")
    sample_rate = 22050
    
    # 1. MEOW
    # Frequency sweeps 450Hz -> 850Hz -> 600Hz
    duration_meow = 0.4
    samples_meow = []
    phase = 0.0
    for i in range(int(sample_rate * duration_meow)):
        t = i / sample_rate
        if t < 0.15:
            freq = 450 + (800 - 450) * (t / 0.15)
        else:
            freq = 800 - (800 - 550) * ((t - 0.15) / (duration_meow - 0.15))
        
        phase += 2 * math.pi * freq / sample_rate
        # Sine wave + 1st harmonic + some noise for raspiness
        val = math.sin(phase) + 0.3 * math.sin(2 * phase)
        
        # Envelope
        if t < 0.05:
            env = t / 0.05
        elif t > duration_meow - 0.1:
            env = (duration_meow - t) / 0.1
        else:
            env = 1.0
        samples_meow.append(val * env * 0.4)
    synthesize_wav(os.path.join(audio_dir, "meow.wav"), samples_meow, sample_rate)
    
    # 2. PURR
    # Amplitude modulated low rumble
    duration_purr = 1.5
    samples_purr = []
    for i in range(int(sample_rate * duration_purr)):
        t = i / sample_rate
        freq = 55.0
        mod = 0.6 + 0.4 * math.sin(2 * math.pi * 12 * t)
        val = math.sin(2 * math.pi * freq * t) * mod
        
        if t < 0.2:
            env = t / 0.2
        elif t > duration_purr - 0.2:
            env = (duration_purr - t) / 0.2
        else:
            env = 1.0
        samples_purr.append(val * env * 0.3)
    synthesize_wav(os.path.join(audio_dir, "purr.wav"), samples_purr, sample_rate)
    
    # 3. ANGRY HISS
    # Shaped white noise
    import random
    duration_hiss = 0.6
    samples_hiss = []
    for i in range(int(sample_rate * duration_hiss)):
        t = i / sample_rate
        val = random.uniform(-1.0, 1.0)
        
        # High-pass filter emulation (simple difference)
        # (reduces bass, makes noise sound more like a hiss)
        if i > 0:
            val = val - 0.9 * samples_hiss[-1]
            
        if t < 0.05:
            env = t / 0.05
        else:
            env = 1.0 - (t - 0.05) / (duration_hiss - 0.05)
        samples_hiss.append(val * env * 0.12)
    synthesize_wav(os.path.join(audio_dir, "hiss.wav"), samples_hiss, sample_rate)
    
    # 4. SLEEP SNORE
    # Cyclic hum and hiss
    duration_snore = 3.0
    samples_snore = []
    for i in range(int(sample_rate * duration_snore)):
        t = i / sample_rate
        # Inhale [0.0, 1.2]
        if t < 1.2:
            ratio = t / 1.2
            freq = 70 + 20 * ratio
            sig = (t * freq % 1.0) - 0.5
            sig += 0.15 * random.uniform(-1.0, 1.0)
            env = math.sin(math.pi * ratio) * 0.12
            val = sig * env
        # Pause [1.2, 1.5]
        elif t < 1.5:
            val = 0.0
        # Exhale [1.5, 2.7]
        elif t < 2.7:
            ratio = (t - 1.5) / 1.2
            sig = random.uniform(-1.0, 1.0)
            if i > 0:
                sig = sig - 0.85 * samples_snore[-1]
            env = math.sin(math.pi * ratio) * 0.08
            val = sig * env
        # Pause [2.7, 3.0]
        else:
            val = 0.0
        samples_snore.append(val)
    synthesize_wav(os.path.join(audio_dir, "snore.wav"), samples_snore, sample_rate)

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Creating folders and assets under: {base_path}")
    create_dirs(base_path)
    print("Generating transparent cat sprites...")
    generate_sprites(base_path)
    print("Synthesizing context-sensitive WAV audio effects...")
    generate_audio(base_path)
    print("Asset generation complete!")

if __name__ == "__main__":
    main()
