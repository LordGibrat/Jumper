import pygame
import sys
import os
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Backflip Project")

box_color = (70, 70, 70)
white = (255, 255, 255)

font1 = pygame.font.SysFont('trebuchetms', 24, bold=True)
font_big = pygame.font.SysFont('impact', 60)

try:
    bg_img = pygame.image.load(os.path.join("wgs", "background.jpg")).convert()
    bg_img = pygame.transform.scale(bg_img, (800, 600))

    player_img = pygame.image.load(os.path.join("wgs", "player.png")).convert_alpha()
    player_img = pygame.transform.scale(player_img, (40, 80))

    images_loaded = True
except FileNotFoundError:
    images_loaded = False


# ---------------------------------------------------------------------------
# Procedural character (used when wgs/player.png is not found)
# ---------------------------------------------------------------------------
def limb(surf, points, color, width):
    """Draw a jointed limb (polyline with rounded joints)."""
    for a, b in zip(points, points[1:]):
        pygame.draw.line(surf, color, a, b, width)
    for p in points:
        pygame.draw.circle(surf, color, p, width // 2)


def make_player(pose):
    """Return a 40x80 character surface. pose: 'stand', 'crouch' or 'air'."""
    s = pygame.Surface((40, 80), pygame.SRCALPHA)
    skin = (255, 205, 160)
    hair = (70, 40, 20)
    shirt = (60, 110, 220)
    shirt_dark = (40, 80, 170)
    pants = (45, 55, 100)
    shoe = (240, 240, 240)
    stripe = (220, 50, 50)

    oy = 20 if pose == "crouch" else 0   # crouching shifts upper body down

    # --- back arm and back leg (drawn first, so they sit behind the body) ---
    if pose == "stand":
        limb(s, [(13, 28), (8, 44)], skin, 5)
        limb(s, [(16, 50), (14, 72)], pants, 7)
        pygame.draw.ellipse(s, shoe, (8, 71, 13, 8))
        pygame.draw.line(s, stripe, (10, 76), (19, 76), 2)
    elif pose == "crouch":
        limb(s, [(14, 50 + 2), (6, 64)], skin, 5)
        limb(s, [(15, 63), (26, 69), (18, 76)], pants, 7)
        pygame.draw.ellipse(s, shoe, (10, 73, 13, 7))
    else:  # air
        limb(s, [(13, 28), (6, 14)], skin, 5)
        limb(s, [(16, 50), (9, 62), (14, 74)], pants, 7)
        pygame.draw.ellipse(s, shoe, (8, 71, 13, 8))

    # --- torso ---
    torso_h = 20 if pose == "crouch" else 26
    pygame.draw.rect(s, shirt, (11, 25 + oy, 18, torso_h), border_radius=6)
    pygame.draw.rect(s, shirt_dark, (11, 25 + oy + torso_h - 5, 18, 3))   # belt
    pygame.draw.line(s, white, (14, 30 + oy), (26, 30 + oy), 2)           # shirt stripe

    # --- head ---
    hy = 13 + oy
    pygame.draw.polygon(s, hair, [(11, hy - 4), (3, hy + 3), (12, hy + 1)])  # back tuft
    pygame.draw.circle(s, skin, (21, hy), 11)
    pygame.draw.ellipse(s, hair, (10, hy - 12, 22, 12))                      # hair top
    pygame.draw.rect(s, stripe, (10, hy - 3, 22, 3))                         # headband
    pygame.draw.circle(s, white, (26, hy + 2), 3)                            # eye
    pygame.draw.circle(s, (20, 20, 20), (27, hy + 2), 1)
    pygame.draw.line(s, (150, 70, 60), (25, hy + 7), (29, hy + 7), 1)        # mouth

    # --- front leg and front arm ---
    if pose == "stand":
        limb(s, [(24, 50), (26, 72)], pants, 7)
        pygame.draw.ellipse(s, shoe, (22, 71, 15, 8))
        pygame.draw.line(s, stripe, (24, 76), (35, 76), 2)
        limb(s, [(27, 28), (31, 44)], skin, 5)
    elif pose == "crouch":
        limb(s, [(24, 63), (33, 68), (27, 76)], pants, 7)
        pygame.draw.ellipse(s, shoe, (23, 73, 15, 7))
        limb(s, [(26, 50), (34, 60)], skin, 5)
    else:  # air
        limb(s, [(24, 50), (32, 60), (27, 73)], pants, 7)
        pygame.draw.ellipse(s, shoe, (23, 70, 15, 8))
        limb(s, [(27, 28), (35, 14)], skin, 5)

    return s


if images_loaded:
    surf_stand = player_img
    surf_air = player_img
    surf_crouch = pygame.transform.scale(player_img, (40, 50))
else:
    surf_stand = make_player("stand")
    surf_air = make_player("air")
    surf_crouch = make_player("crouch")


# ---------------------------------------------------------------------------
# Levels
# ---------------------------------------------------------------------------
lvl1 = {"start": (50, 400), "pads": [(300, 450, 150)]}
lvl2 = {"start": (50, 450), "pads": [(400, 300, 120)]}
lvl3 = {"start": (50, 200), "pads": [(300, 350, 100), (600, 500, 100)]}
lvl4 = {"start": (50, 450), "pads": [(300, 300, 100), (550, 150, 100)]}
lvl5 = {"start": (20, 250), "pads": [(200, 400, 80), (450, 250, 80), (680, 400, 80)]}

levels = [lvl1, lvl2, lvl3, lvl4, lvl5]
lvl_num = 0
pad_num = 0
score = 0
state = "wait"

px, py = 0, 0
vx, vy = 0, 0
angle = 0
power = 0
power_dir = 1
spinning = False
flips = 0
rot = 0

# fall animation variables
fall_t = 0      # frame counter of the fall
fdir = 1        # direction the character falls (-1 left, +1 right)
fx, fy = 0, 0   # pivot point (the edge the character teeters on)

EDGE_TOLERANCE = 14   # how far the feet may hang over the edge and still touch it
GRAVITY = 0.4


def setup_level():
    global px, py, pad_num, state
    px = levels[lvl_num]["start"][0]
    py = levels[lvl_num]["start"][1] - 80
    pad_num = 0
    reset_jump()


def reset_jump():
    global vx, vy, angle, power, spinning, flips, rot, state, fall_t
    vx, vy, angle, power, rot, flips = 0, 0, 0, 0, 0, 0
    fall_t = 0
    spinning = False
    state = "wait"


def pad_collision(prev_feet, x, y, vel_y, pad):
    """Return 'top' if the feet reach the pad's top (even on the very edge),
    'wall' if the body hits the pad's side, otherwise None."""
    tx, ty, tw = pad
    feet = y + 80
    cx = x + 20
    if vel_y > 0 and prev_feet <= ty + 1 and feet >= ty \
            and tx - EDGE_TOLERANCE <= cx <= tx + tw + EDGE_TOLERANCE:
        return "top"
    if feet > ty + 4 and x + 32 > tx and x + 8 < tx + tw:
        return "wall"
    return None


def calc_trajectory():
    """Simulate the jump with the current power and return the aim dots."""
    v_x = 3 + (power / 20)
    v_y = -6 - (power / 10)
    x, y = px, py
    pad = levels[lvl_num]["pads"][pad_num]
    dots = []
    for step in range(300):
        prev_feet = y + 80
        x += v_x
        y += v_y
        v_y += GRAVITY
        hit = pad_collision(prev_feet, x, y, v_y, pad)
        if hit == "top":
            dots.append((x + 20, pad[1]))       # landing point
            break
        if hit == "wall" or y > 600 or x > 820:
            break
        if step % 4 == 3:
            dots.append((x + 20, y + 40))       # body center
    return dots


setup_level()
clock = pygame.time.Clock()

run = True
while run:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            run = False

        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
            if state == "wait":
                state = "sit"
            elif state == "fly":
                spinning = True
            elif state == "land":
                pad_num += 1
                if pad_num >= len(levels[lvl_num]["pads"]):
                    lvl_num += 1
                    if lvl_num > 4:
                        state = "win"
                    else:
                        setup_level()
                else:
                    reset_jump()
            elif state == "dead":
                lvl_num = 0
                score = 0
                setup_level()

        if ev.type == pygame.KEYUP and ev.key == pygame.K_SPACE:
            if state == "sit":
                state = "fly"
                vx = 3 + (power / 20)
                vy = -6 - (power / 10)
            elif state == "fly":
                spinning = False

    # ------------------------------------------------------------------ logic
    if state == "sit":
        power += 2.5 * power_dir
        if power > 100 or power < 0:
            power_dir *= -1
        angle = -(power / 100) * 40

    elif state == "fly":
        prev_feet = py + 80
        px += vx
        py += vy
        vy += GRAVITY

        if spinning:
            angle -= 14
            rot += 14
            if rot >= 360:
                flips += 1
                rot = 0

        cur_pad = levels[lvl_num]["pads"][pad_num]
        tx, ty, tw = cur_pad
        hit = pad_collision(prev_feet, px, py, vy, cur_pad)

        if py > 600:
            state = "dead"

        elif hit == "top":
            py = ty - 80
            vy = 0
            cx = px + 20
            if tx <= cx <= tx + tw:
                # centre of the body is over the pad -> normal landing
                norm_angle = abs(angle % 360)
                if norm_angle < 40 or norm_angle > 320:
                    state = "land"
                    angle = 0
                    score += 50 + (flips * 100)
                else:
                    # bad angle: crash and lie on the pad
                    state = "dead"
                    angle = -90
                    py = ty - 52
            else:
                # only the toes touched the edge -> teeter and fall off
                state = "fall"
                spinning = False
                fall_t = 0
                fdir = -1 if cx < tx else 1
                fx, fy = cx, ty
                angle = 0

        elif hit == "wall":
            # slammed into the side of the platform -> bounce back and fall
            state = "fall"
            spinning = False
            fall_t = 25                       # skip the teeter phase
            fdir = -1 if (px + 20) < tx + tw / 2 else 1
            px = tx - 33 if fdir == -1 else tx + tw - 7
            vy = -3

    elif state == "fall":
        if fall_t < 25:
            # phase 1: teeter - pivot around the edge and tip over
            fall_t += 1
            fx += fdir * 0.7
            angle = -fdir * fall_t * 2.6
            a = math.radians(angle)
            px = fx - 40 * math.sin(a) - 20
            py = fy - 40 * math.cos(a) - 40
        else:
            # phase 2: free fall, tumbling
            fall_t += 1
            px += fdir * 1.6
            vy += 0.5
            py += vy
            angle += -fdir * 7
            if py > 600:
                state = "dead"

    # ---------------------------------------------------------------- drawing
    if images_loaded:
        screen.blit(bg_img, (0, 0))
    else:
        screen.fill((100, 200, 250))
        pygame.draw.rect(screen, (50, 180, 50), (0, 550, 800, 50))

    def draw_player():
        if state == "sit":
            surf = surf_crouch
            draw_y = py + 30 if images_loaded else py
        elif state in ("fly", "fall"):
            surf = surf_air
            draw_y = py
        else:
            surf = surf_stand
            draw_y = py
        rot_surf = pygame.transform.rotate(surf, angle)
        rect = rot_surf.get_rect(center=(px + 20, draw_y + 40))
        screen.blit(rot_surf, rect)

    # a falling character is drawn behind the platforms (so it drops past them)
    if state == "fall":
        draw_player()

    sx, sy = levels[lvl_num]["start"]
    pygame.draw.rect(screen, box_color, (sx, sy, 60, 600))

    for i, pad in enumerate(levels[lvl_num]["pads"]):
        pad_color = (200, 200, 200)
        if i == pad_num:
            pad_color = (255, 50, 50)
        elif i < pad_num:
            pad_color = (50, 200, 50)

        pygame.draw.rect(screen, box_color, (pad[0], pad[1], pad[2], 600))
        pygame.draw.rect(screen, pad_color, (pad[0], pad[1], pad[2], 10))

    # aim: white dots showing the trajectory of the jump
    if state == "sit":
        dots = calc_trajectory()
        for i, (dx, dy) in enumerate(dots):
            r = max(2, 5 - i // 6)
            pygame.draw.circle(screen, white, (int(dx), int(dy)), r)
        if dots:
            pygame.draw.circle(screen, white, (int(dots[-1][0]), int(dots[-1][1])), 9, 2)

    if state != "fall":
        draw_player()

    screen.blit(font1.render(f"УРОВЕНЬ: {lvl_num + 1}/5", True, white), (20, 520))
    screen.blit(font1.render(f"ОЧКИ: {score}", True, white), (640, 520))

    if state == "wait":
        screen.blit(font1.render("Жми ПРОБЕЛ", True, white), (px - 20, py - 40))
    elif state == "sit":
        pygame.draw.rect(screen, (255, 0, 0), (px - 10, py - 15, int(power / 1.5), 8))
        screen.blit(font1.render("Отпускай!", True, (255, 100, 100)), (px - 10, py - 40))
    elif state == "fly" and flips > 0:
        screen.blit(font1.render(f"Сальто: {flips}", True, (255, 200, 0)), (px - 10, py - 40))

    if state == "land":
        msg = font_big.render(f"КРУТО! +{50 + flips*100}", True, (50, 255, 50))
        screen.blit(msg, (400 - msg.get_width()//2, 200))
    elif state == "dead":
        msg = font_big.render("АУЧ! ЗАНОВО", True, (255, 50, 50))
        screen.blit(msg, (400 - msg.get_width()//2, 200))
    elif state == "win":
        msg = font_big.render("ТЫ ПРОШЕЛ ИГРУ!", True, (255, 200, 0))
        screen.blit(msg, (400 - msg.get_width()//2, 200))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
