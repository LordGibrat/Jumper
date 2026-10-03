import pygame
import sys
import os
import math
import random
import time

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Backflip Project")

white = (255, 255, 255)
GROUND_Y = 550          # objects stand on this line

font1 = pygame.font.SysFont('trebuchetms', 24, bold=True)
font_small = pygame.font.SysFont('trebuchetms', 16, bold=True)
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
# Helpers
# ---------------------------------------------------------------------------
def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_text(txt, fnt, color, pos, anchor="left", shadow=2):
    img = fnt.render(txt, True, color)
    sh = fnt.render(txt, True, (0, 0, 0))
    x, y = pos
    if anchor == "center":
        x -= img.get_width() // 2
    elif anchor == "right":
        x -= img.get_width()
    screen.blit(sh, (x + shadow, y + shadow))
    screen.blit(img, (x, y))


def limb(surf, points, color, width):
    for a, b in zip(points, points[1:]):
        pygame.draw.line(surf, color, a, b, width)
    for p in points:
        pygame.draw.circle(surf, color, p, width // 2)


# ---------------------------------------------------------------------------
# Player character (procedural, used when wgs/player.png is missing)
# ---------------------------------------------------------------------------
def make_player(pose, shoe=(240, 240, 240), stripe=(220, 50, 45), appearance="normal"):
    s = pygame.Surface((40, 80), pygame.SRCALPHA)
    skin = (255, 205, 160)
    hair = (70, 40, 20)
    shirt = (60, 110, 220)
    shirt_dark = (40, 80, 170)
    pants = (45, 55, 100)
    band = (220, 50, 50)
    bare = appearance == "barefoot"
    mega = appearance == "mega"
    legend = appearance in ("legend", "mega")
    foot = skin if bare else shoe               # barefoot: draw toes, not a shoe
    if mega:                                      # top-of-aura outfit: sparkly showman look
        shirt, shirt_dark, band = (25, 25, 30), (10, 10, 15), (220, 30, 40)
    oy = 20 if pose == "crouch" else 0

    if pose == "tuck":
        # cannonball tuck: knees pulled up to the chest while spinning
        pygame.draw.rect(s, shirt, (11, 30, 18, 20), border_radius=6)
        limb(s, [(13, 34), (8, 52)], skin, 5)                     # back arm wraps shins
        limb(s, [(15, 50), (9, 62), (17, 38)], pants, 6)          # back leg folded up
        pygame.draw.ellipse(s, foot, (7, 34, 13, 8))
        if not bare:
            pygame.draw.line(s, stripe, (8, 39), (16, 39), 1)
        hy = 20
        pygame.draw.polygon(s, hair, [(11, hy - 4), (3, hy + 3), (12, hy + 1)])
        pygame.draw.circle(s, skin, (21, hy), 10)
        pygame.draw.ellipse(s, hair, (11, hy - 11, 20, 11))
        pygame.draw.rect(s, band, (11, hy - 2, 20, 3))
        pygame.draw.circle(s, white, (26, hy + 2), 3)
        pygame.draw.circle(s, (20, 20, 20), (27, hy + 2), 1)
        limb(s, [(25, 50), (31, 62), (23, 38)], pants, 6)         # front leg folded up
        pygame.draw.ellipse(s, foot, (18, 34, 13, 8))
        if not bare:
            pygame.draw.line(s, stripe, (19, 39), (27, 39), 1)
        limb(s, [(27, 34), (32, 52)], skin, 5)                    # front arm wraps shins
        if legend:
            pygame.draw.circle(s, white, (32, 52), 4)
            pygame.draw.circle(s, (40, 40, 45), (32, 52), 4, 1)
        return s

    if pose == "stand":
        limb(s, [(13, 28), (8, 44)], skin, 5)
        limb(s, [(16, 50), (14, 72)], pants, 7)
        pygame.draw.ellipse(s, foot, (8, 71, 13, 8))
        if not bare:
            pygame.draw.line(s, stripe, (10, 76), (19, 76), 2)
    elif pose == "crouch":
        limb(s, [(14, 52), (6, 64)], skin, 5)
        limb(s, [(15, 63), (26, 69), (18, 76)], pants, 7)
        pygame.draw.ellipse(s, foot, (10, 73, 13, 7))
    else:
        limb(s, [(13, 28), (6, 14)], skin, 5)
        limb(s, [(16, 50), (9, 62), (14, 74)], pants, 7)
        pygame.draw.ellipse(s, foot, (8, 71, 13, 8))

    torso_h = 20 if pose == "crouch" else 26
    pygame.draw.rect(s, shirt, (11, 25 + oy, 18, torso_h), border_radius=6)
    pygame.draw.rect(s, shirt_dark, (11, 25 + oy + torso_h - 5, 18, 3))
    pygame.draw.line(s, (200, 40, 50) if mega else white, (14, 30 + oy), (26, 30 + oy), 2)

    hy = 13 + oy
    pygame.draw.polygon(s, hair, [(11, hy - 4), (3, hy + 3), (12, hy + 1)])
    pygame.draw.circle(s, skin, (21, hy), 11)
    pygame.draw.ellipse(s, hair, (10, hy - 12, 22, 12))
    if mega:
        pygame.draw.polygon(s, (20, 20, 25), [(8, hy - 8), (34, hy - 8), (30, hy - 15), (12, hy - 15)])
        pygame.draw.ellipse(s, (20, 20, 25), (6, hy - 10, 30, 6))     # fedora brim
        pygame.draw.rect(s, band, (10, hy - 9, 22, 3))                # hat band
    else:
        pygame.draw.rect(s, band, (10, hy - 3, 22, 3))
    if legend:
        pygame.draw.rect(s, (20, 20, 25), (14, hy - 1, 16, 4), border_radius=2)   # shades
    else:
        pygame.draw.circle(s, white, (26, hy + 2), 3)
        pygame.draw.circle(s, (20, 20, 20), (27, hy + 2), 1)
    pygame.draw.line(s, (150, 70, 60), (25, hy + 7), (29, hy + 7), 1)

    if pose == "stand":
        limb(s, [(24, 50), (26, 72)], pants, 7)
        pygame.draw.ellipse(s, foot, (22, 71, 15, 8))
        if not bare:
            pygame.draw.line(s, stripe, (24, 76), (35, 76), 2)
        limb(s, [(27, 28), (31, 44)], skin, 5)
        if mega:
            pygame.draw.circle(s, white, (31, 44), 5)
            pygame.draw.circle(s, (40, 40, 45), (31, 44), 5, 1)
    elif pose == "crouch":
        limb(s, [(24, 63), (33, 68), (27, 76)], pants, 7)
        pygame.draw.ellipse(s, foot, (23, 73, 15, 7))
        limb(s, [(26, 50), (34, 60)], skin, 5)
    else:
        limb(s, [(24, 50), (32, 60), (27, 73)], pants, 7)
        pygame.draw.ellipse(s, foot, (23, 70, 15, 8))
        limb(s, [(27, 28), (35, 14)], skin, 5)
        if mega:
            pygame.draw.circle(s, white, (35, 14), 5)
            pygame.draw.circle(s, (40, 40, 45), (35, 14), 5, 1)
    return s


def appearance_tier(a):
    """How the character looks, tied to his current aura."""
    if a < 1_000:
        return "barefoot"
    if a < 100_000:
        return "normal"
    if a < AURA_MAX:
        return "legend"
    return "mega"


# ---------------------------------------------------------------------------
# Sneakers (bought for coins).  jump = jump height, speed = flight speed,
# spin = degrees per frame while flipping, coins = coin reward multiplier.
# ---------------------------------------------------------------------------
SHOES = [
    {"id": "basic", "name": "Обычные", "desc": "Стандартные, без бонусов", "price": 0,
     "jump": 1.0, "speed": 1.0, "spin": 14, "coins": 1.0,
     "color": (240, 240, 240), "stripe": (220, 50, 50)},
    {"id": "spring", "name": "Пружинки", "desc": "Прыгают намного выше", "price": 120,
     "jump": 1.3, "speed": 1.0, "spin": 14, "coins": 1.0,
     "color": (80, 200, 90), "stripe": (255, 255, 255)},
    {"id": "sprint", "name": "Спринтеры", "desc": "Летят и крутятся быстрее", "price": 120,
     "jump": 1.0, "speed": 1.35, "spin": 18, "coins": 1.0,
     "color": (60, 150, 255), "stripe": (255, 230, 60)},
    {"id": "gold", "name": "Золотые", "desc": "Всё лучше и +50% монет", "price": 400,
     "jump": 1.15, "speed": 1.15, "spin": 16, "coins": 1.5,
     "color": (255, 205, 60), "stripe": (255, 255, 255)},
]
shoe_id = "basic"
owned_shoes = {"basic"}


def current_shoe():
    for sh in SHOES:
        if sh["id"] == shoe_id:
            return sh
    return SHOES[0]


def build_sprites():
    """(Re)build the character sprites. *_b = mirrored: the character stands with
    his back to the landing spot (backflip mode)."""
    global surf_stand, surf_air, surf_crouch, surf_tuck
    global surf_stand_b, surf_air_b, surf_crouch_b, surf_tuck_b
    sh = current_shoe()
    tier = appearance_tier(aura)
    if images_loaded:
        surf_stand = player_img
        surf_air = player_img
        surf_crouch = pygame.transform.scale(player_img, (40, 50))
        surf_tuck = player_img
    else:
        surf_stand = make_player("stand", sh["color"], sh["stripe"], tier)
        surf_air = make_player("air", sh["color"], sh["stripe"], tier)
        surf_crouch = make_player("crouch", sh["color"], sh["stripe"], tier)
        surf_tuck = make_player("tuck", sh["color"], sh["stripe"], tier)
    surf_stand_b = pygame.transform.flip(surf_stand, True, False)
    surf_air_b = pygame.transform.flip(surf_air, True, False)
    surf_crouch_b = pygame.transform.flip(surf_crouch, True, False)
    surf_tuck_b = pygame.transform.flip(surf_tuck, True, False)


aura = 0                # placeholder so appearance_tier(aura) works before "aura + crowd" below re-declares it
current_appearance = appearance_tier(aura)
build_sprites()


# ---------------------------------------------------------------------------
# Real-world objects used as platforms.  Every object has a flat top at y,
# is `w` wide and stands on the ground (height h = GROUND_Y - y).
# ---------------------------------------------------------------------------
def draw_crates(x, y, w, h):
    n = max(1, h // 50)
    ch = h / n
    for i in range(n):
        r = pygame.Rect(x, int(y + i * ch), w, int(ch) + 1)
        pygame.draw.rect(screen, (176, 124, 66), r)
        pygame.draw.rect(screen, (110, 72, 32), r, 3)
        pygame.draw.line(screen, (110, 72, 32), r.topleft, r.bottomright, 3)
        pygame.draw.line(screen, (110, 72, 32), r.topright, r.bottomleft, 3)


def draw_taxi(x, y, w, h):
    bh = h - 14
    pygame.draw.rect(screen, (245, 190, 40), (x, y, w, bh), border_radius=8)
    pygame.draw.rect(screen, (170, 220, 240), (x + 10, y + 12, w - 20, 30), border_radius=4)
    for k in (1, 2):
        pygame.draw.line(screen, (245, 190, 40), (x + k * w // 3, y + 12), (x + k * w // 3, y + 42), 4)
    for i in range(0, w, 6):
        c = (20, 20, 20) if (i // 6) % 2 == 0 else white
        pygame.draw.rect(screen, c, (x + i, y + bh - 30, 6, 6))
    pygame.draw.rect(screen, (255, 250, 180), (x + w - 10, y + bh - 22, 8, 8))
    pygame.draw.rect(screen, (220, 40, 40), (x + 2, y + bh - 22, 8, 8))
    pygame.draw.rect(screen, (150, 150, 155), (x, y + bh - 6, w, 6))
    for cx in (x + 32, x + w - 32):
        pygame.draw.circle(screen, (25, 25, 25), (cx, y + h - 14), 14)
        pygame.draw.circle(screen, (170, 170, 175), (cx, y + h - 14), 6)


def draw_mailbox(x, y, w, h):
    bh = h - 34
    pygame.draw.rect(screen, (110, 90, 70), (x + w // 2 - 7, y + bh, 14, 34))
    pygame.draw.rect(screen, (150, 150, 155), (x + w // 2 - 14, y + h - 6, 28, 6))
    pygame.draw.rect(screen, (40, 90, 200), (x + 2, y, w - 4, bh), border_radius=4)
    pygame.draw.rect(screen, (20, 20, 40), (x + 10, y + 14, w - 20, 5))
    pygame.draw.circle(screen, (255, 210, 60), (x + w // 2, y + 40), 8)
    pygame.draw.rect(screen, (220, 40, 40), (x + w - 4, y + 10, 8, 22))


def draw_tree(x, y, w, h):
    tx = x + w // 2
    pygame.draw.rect(screen, (105, 68, 38), (tx - 15, y + 40, 30, h - 40))
    pygame.draw.polygon(screen, (105, 68, 38), [(tx - 15, GROUND_Y), (tx - 30, GROUND_Y), (tx - 15, GROUND_Y - 22)])
    pygame.draw.polygon(screen, (105, 68, 38), [(tx + 15, GROUND_Y), (tx + 30, GROUND_Y), (tx + 15, GROUND_Y - 22)])
    for k in range(4):
        pygame.draw.rect(screen, (85, 52, 28), (tx - 10 + (k % 2) * 12, y + 70 + k * 35, 4, 18))
    pygame.draw.rect(screen, (46, 140, 58), (x, y, w, 96), border_radius=22)
    for i in range(7):
        cx = x + 14 + i * (w - 28) // 6
        cy = y + 28 + (i % 3) * 22
        pygame.draw.circle(screen, (70, 175, 80), (cx, cy), 15)
    for ax, ay in ((x + 30, y + 40), (x + w - 34, y + 62), (x + w // 2, y + 80)):
        pygame.draw.circle(screen, (220, 50, 50), (ax, ay), 4)


def draw_office(x, y, w, h):
    pygame.draw.rect(screen, (95, 110, 140), (x, y, w, h))
    for r in range(max(1, (h - 50) // 26)):
        for c in range(3):
            lit = (r * 3 + c) % 4 == 0
            col = (255, 225, 120) if lit else (60, 80, 110)
            pygame.draw.rect(screen, col, (x + 8 + c * 17, y + 16 + r * 26, 11, 16))
    pygame.draw.rect(screen, (60, 70, 95), (x, y, w, 8))
    pygame.draw.rect(screen, (50, 50, 60), (x + w // 2 - 9, GROUND_Y - 24, 18, 24))


def draw_bus_stop(x, y, w, h):
    pygame.draw.rect(screen, (190, 225, 240), (x + 8, y + 10, w - 16, h - 30))
    pygame.draw.line(screen, white, (x + 50, y + h - 40), (x + 74, y + 20), 2)
    pygame.draw.line(screen, white, (x + 60, y + h - 40), (x + 84, y + 20), 2)
    pygame.draw.rect(screen, (70, 80, 90), (x + 2, y + 10, 6, h - 10))
    pygame.draw.rect(screen, (70, 80, 90), (x + w - 8, y + 10, 6, h - 10))
    pygame.draw.rect(screen, (240, 240, 240), (x + 14, y + 18, 26, 40))
    pygame.draw.rect(screen, (230, 80, 90), (x + 17, y + 21, 20, 20))
    pygame.draw.rect(screen, (140, 95, 50), (x + 16, y + h - 56, w - 32, 7))
    pygame.draw.rect(screen, (100, 65, 35), (x + 20, y + h - 49, 4, 29))
    pygame.draw.rect(screen, (100, 65, 35), (x + w - 24, y + h - 49, 4, 29))
    pygame.draw.rect(screen, (35, 95, 160), (x, y, w, 10))          # roof
    pygame.draw.rect(screen, (30, 120, 220), (x + w - 24, y + 14, 14, 18))
    pygame.draw.rect(screen, white, (x + w - 21, y + 18, 8, 4))
    pygame.draw.rect(screen, (120, 120, 125), (x, GROUND_Y - 4, w, 4))


def draw_floor(x, y, w, h):
    for r in range(0, h, 25):
        for c in range(0, w, 25):
            col = (205, 205, 210) if ((r // 25) + (c // 25)) % 2 == 0 else (165, 165, 175)
            pygame.draw.rect(screen, col, (x + c, y + r, min(25, w - c), min(25, h - r)))
    pygame.draw.rect(screen, (60, 60, 70), (x, y, w, h), 2)


def draw_dumpster(x, y, w, h):
    pygame.draw.rect(screen, (35, 105, 60), (x + 2, y + 12, w - 4, h - 28))
    for k in range(1, 4):
        vx_ = x + 2 + (w - 4) * k // 4
        pygame.draw.line(screen, (28, 85, 50), (vx_, y + 16), (vx_, y + h - 20), 2)
    pygame.draw.rect(screen, (240, 200, 40), (x + 2, y + 34, w - 4, 6))
    pygame.draw.rect(screen, (25, 75, 45), (x, y, w, 14), border_radius=3)
    pygame.draw.rect(screen, (150, 155, 160), (x + w // 2 - 10, y + 5, 20, 4))
    for cx in (x + 12, x + w - 12):
        pygame.draw.circle(screen, (25, 25, 25), (cx, y + h - 8), 8)
        pygame.draw.circle(screen, (150, 150, 155), (cx, y + h - 8), 3)


def draw_shop(x, y, w, h):
    pygame.draw.rect(screen, (165, 68, 50), (x, y, w, h))
    for row, by in enumerate(range(y + 14, GROUND_Y, 12)):
        pygame.draw.line(screen, (130, 50, 38), (x, by), (x + w, by), 1)
        for bx in range(x + (row % 2) * 10, x + w, 20):
            pygame.draw.line(screen, (130, 50, 38), (bx, by), (bx, by + 12), 1)
    pygame.draw.rect(screen, (235, 225, 195), (x, y, w, 12))
    pygame.draw.rect(screen, (30, 30, 40), (x + 12, y + 24, w - 24, 26))
    draw_text("SHOP", font_small, (255, 220, 80), (x + w // 2, y + 27), "center", 0)
    for wx in (x + 10, x + w - 42):
        pygame.draw.rect(screen, (235, 225, 195), (wx, y + 64, 32, 44))
        pygame.draw.rect(screen, (150, 200, 230), (wx + 3, y + 67, 26, 38))
    for i in range(w // 10):
        c = (200, 50, 50) if i % 2 == 0 else (245, 245, 245)
        pygame.draw.rect(screen, c, (x + i * 10, GROUND_Y - 128, 10, 14))
    pygame.draw.rect(screen, (170, 215, 235), (x + 8, GROUND_Y - 112, w - 50, 70))
    pygame.draw.rect(screen, (235, 225, 195), (x + 8, GROUND_Y - 112, w - 50, 70), 3)
    pygame.draw.rect(screen, (110, 70, 40), (x + w - 34, GROUND_Y - 70, 26, 70))
    pygame.draw.circle(screen, (255, 210, 60), (x + w - 14, GROUND_Y - 34), 3)


def draw_skyscraper(x, y, w, h):
    pygame.draw.rect(screen, (55, 115, 175), (x, y, w, h))
    for ry in range(y + 18, GROUND_Y - 40, 22):
        for c in range(4):
            lit = ((ry - y) // 22 + c * 3) % 5 == 0
            col = (255, 235, 140) if lit else (140, 200, 235)
            pygame.draw.rect(screen, col, (x + 7 + c * 22, ry, 16, 12))
    pygame.draw.rect(screen, (25, 55, 95), (x, y, w, 8))
    pygame.draw.rect(screen, (35, 60, 90), (x + 10, GROUND_Y - 30, w - 20, 30))
    pygame.draw.line(screen, (150, 200, 235), (x + w // 2, GROUND_Y - 30), (x + w // 2, GROUND_Y), 2)


def draw_chimney(x, y, w, h):
    for i in range(0, h, 50):
        c = white if (i // 50) % 2 else (200, 50, 45)
        pygame.draw.rect(screen, c, (x, y + i, w, min(50, h - i)))
    pygame.draw.rect(screen, (30, 30, 35), (x, y, w, 8))
    pygame.draw.rect(screen, (60, 60, 65), (x, y, w, h), 2)


def draw_vending(x, y, w, h):
    pygame.draw.rect(screen, (200, 40, 45), (x, y, w, h), border_radius=4)
    pygame.draw.rect(screen, (230, 90, 90), (x + 4, y + 4, w - 8, 6))
    ww, wh = w - 32, h - 64
    pygame.draw.rect(screen, (25, 30, 45), (x + 8, y + 16, ww, wh))
    palette = [(240, 200, 40), (60, 170, 230), (240, 240, 240), (80, 200, 90)]
    for r in range((wh - 8) // 18):
        for c in range((ww - 8) // 14):
            pygame.draw.rect(screen, palette[(r + c) % 4], (x + 12 + c * 14, y + 20 + r * 18, 10, 14))
    pygame.draw.rect(screen, (160, 165, 175), (x + w - 20, y + 18, 12, 30))
    for k in range(3):
        pygame.draw.circle(screen, (60, 60, 70), (x + w - 14, y + 25 + k * 9), 2)
    pygame.draw.rect(screen, (0, 0, 0), (x + w - 20, y + 56, 12, 4))
    pygame.draw.rect(screen, (20, 20, 25), (x + 10, y + h - 38, w - 32, 20))
    pygame.draw.rect(screen, (120, 20, 25), (x, y + h - 10, w, 10))


def draw_clock_tower(x, y, w, h):
    pygame.draw.rect(screen, (205, 190, 165), (x, y, w, h))
    for by in range(y + 24, GROUND_Y, 14):
        pygame.draw.line(screen, (185, 170, 145), (x, by), (x + w, by), 1)
    pygame.draw.rect(screen, (80, 65, 90), (x, y, w, 10))
    pygame.draw.rect(screen, (150, 130, 110), (x, y + 10, w, 6))
    cx, cy = x + w // 2, y + 56
    pygame.draw.circle(screen, white, (cx, cy), 26)
    pygame.draw.circle(screen, (60, 50, 40), (cx, cy), 26, 3)
    for k in range(12):
        a = math.radians(k * 30)
        pygame.draw.line(screen, (60, 50, 40),
                         (cx + 20 * math.sin(a), cy - 20 * math.cos(a)),
                         (cx + 23 * math.sin(a), cy - 23 * math.cos(a)), 2)
    t = time.localtime()
    ma = math.radians(t.tm_min * 6)
    ha = math.radians(((t.tm_hour % 12) + t.tm_min / 60) * 30)
    pygame.draw.line(screen, (30, 30, 30), (cx, cy), (cx + 19 * math.sin(ma), cy - 19 * math.cos(ma)), 2)
    pygame.draw.line(screen, (30, 30, 30), (cx, cy), (cx + 12 * math.sin(ha), cy - 12 * math.cos(ha)), 3)
    for wy in range(y + 110, GROUND_Y - 50, 44):
        pygame.draw.rect(screen, (60, 50, 70), (x + w // 2 - 7, wy, 14, 26), border_radius=6)
    pygame.draw.rect(screen, (90, 60, 40), (x + w // 2 - 12, GROUND_Y - 34, 24, 34),
                     border_top_left_radius=12, border_top_right_radius=12)


def draw_cat(x, y, w, h):
    fur, dark, light = (240, 150, 60), (200, 105, 30), (255, 235, 205)
    cx = x + w // 2
    pygame.draw.rect(screen, fur, (x, y, w, h), border_radius=10)
    pygame.draw.polygon(screen, fur, [(x + 4, y + 2), (x + 10, y - 10), (x + 22, y + 2)])
    pygame.draw.polygon(screen, fur, [(x + w - 22, y + 2), (x + w - 10, y - 10), (x + w - 4, y + 2)])
    pygame.draw.polygon(screen, (255, 170, 170), [(x + 9, y + 1), (x + 11, y - 5), (x + 17, y + 1)])
    pygame.draw.polygon(screen, (255, 170, 170), [(x + w - 17, y + 1), (x + w - 11, y - 5), (x + w - 9, y + 1)])
    for dx in (-10, 0, 10):
        pygame.draw.line(screen, dark, (cx + dx, y + 3), (cx + dx, y + 15), 3)
    pygame.draw.ellipse(screen, light, (cx - 20, y + 66, 40, max(10, h - 92)))
    for ex in (int(x + w * 0.3), int(x + w * 0.7)):
        pygame.draw.ellipse(screen, (250, 250, 190), (ex - 8, y + 26, 16, 18))
        pygame.draw.rect(screen, (0, 0, 0), (ex - 2, y + 28, 4, 14))
    pygame.draw.polygon(screen, (255, 120, 140), [(cx - 4, y + 50), (cx + 4, y + 50), (cx, y + 56)])
    pygame.draw.line(screen, dark, (cx, y + 56), (cx - 6, y + 62), 2)
    pygame.draw.line(screen, dark, (cx, y + 56), (cx + 6, y + 62), 2)
    for dy, ty_ in ((52, 48), (58, 61)):
        pygame.draw.line(screen, (90, 60, 30), (x + 12, y + dy), (x - 6, y + ty_), 1)
        pygame.draw.line(screen, (90, 60, 30), (x + w - 12, y + dy), (x + w + 6, y + ty_), 1)
    for px_ in (x + 12, x + w - 34):
        pygame.draw.ellipse(screen, light, (px_, GROUND_Y - 14, 22, 14))
        pygame.draw.ellipse(screen, dark, (px_, GROUND_Y - 14, 22, 14), 2)
    pygame.draw.lines(screen, fur, False,
                      [(x + w - 6, GROUND_Y - 12), (x + w + 12, GROUND_Y - 30), (x + w + 14, GROUND_Y - 62)], 8)
    pygame.draw.circle(screen, dark, (x + w + 14, GROUND_Y - 62), 4)


def draw_cart(x, y, w, h, body, roof, label):
    bh = h - 30
    pygame.draw.rect(screen, body, (x, y + 20, w, bh), border_radius=6)
    pygame.draw.rect(screen, roof, (x - 4, y + 6, w + 8, 16), border_radius=6)
    pygame.draw.rect(screen, (30, 30, 35), (x + 6, y + 26, w - 12, 18))
    draw_text(label, font_small, white, (x + w // 2, y + 27), "center", 0)
    pygame.draw.rect(screen, (230, 230, 235), (x + 4, y + h - 22, w - 8, 10))
    for cx in (x + 14, x + w - 14):
        pygame.draw.circle(screen, (30, 30, 30), (cx, y + h - 10), 9)
        pygame.draw.circle(screen, (170, 170, 175), (cx, y + h - 10), 3)


def draw_stack(x, y, w, h, color, dark, rounds=False):
    n = max(1, h // 46)
    ch = h / n
    for i in range(n):
        ry = int(y + i * ch)
        r = pygame.Rect(x, ry, w, int(ch) + 1)
        if rounds:
            pygame.draw.rect(screen, color, r, border_radius=14)
            pygame.draw.rect(screen, dark, r, 2, border_radius=14)
            pygame.draw.ellipse(screen, dark, (x + 4, ry - 4, w - 8, 10), 2)
        else:
            pygame.draw.rect(screen, color, r)
            pygame.draw.rect(screen, dark, r, 3)
            pygame.draw.line(screen, dark, r.topleft, r.bottomright, 2)


def draw_kiosk(x, y, w, h, body, roof, label):
    pygame.draw.rect(screen, body, (x, y + 14, w, h - 14))
    pygame.draw.polygon(screen, roof, [(x - 6, y + 18), (x + w // 2, y - 6), (x + w + 6, y + 18)])
    pygame.draw.rect(screen, (230, 230, 235), (x + 6, y + 26, w - 12, 32))
    draw_text(label, font_small, (30, 30, 40), (x + w // 2, y + 34), "center", 0)
    pygame.draw.rect(screen, roof, (x + w // 2 - 16, y + h - 30, 32, 30))


def draw_subway(x, y, w, h, top_col):
    pygame.draw.rect(screen, (60, 60, 65), (x, y + h - 60, w, 60))
    for i in range(3):
        pygame.draw.rect(screen, (30, 30, 35), (x + 6 + i * (w - 12) // 3, y + h - 52, (w - 12) // 3 - 6, 40))
    pygame.draw.rect(screen, top_col, (x, y + h - 66, w, 10), border_radius=3)
    pygame.draw.circle(screen, top_col, (x + w // 2, y + h - 80), 12)
    draw_text("M", font_small, white, (x + w // 2, y + h - 88), "center", 0)
    for i in range(h - 60):
        pass


def draw_torii(x, y, w, h):
    col = (200, 50, 45)
    pygame.draw.rect(screen, col, (x + 6, y + h - 130, 12, 130))
    pygame.draw.rect(screen, col, (x + w - 18, y + h - 130, 12, 130))
    pygame.draw.rect(screen, col, (x - 6, y + h - 140, w + 12, 16))
    pygame.draw.rect(screen, (40, 30, 25), (x - 2, y + h - 122, w + 4, 8))
    pygame.draw.rect(screen, (150, 150, 155), (x, y, w, h - 150))


def draw_cafe(x, y, w, h):
    pygame.draw.rect(screen, (235, 220, 195), (x, y + 30, w, h - 30))
    pygame.draw.rect(screen, (60, 90, 70), (x, y + 30, w, 10))
    for i in range(4):
        cx = x + 10 + i * (w - 20) // 3
        pygame.draw.line(screen, (60, 90, 70), (cx, y + 6), (cx - 6, y + 30), 4)
    for i in range(4):
        cx = x + 4 + i * (w - 8) // 4
        pygame.draw.polygon(screen, (60, 90, 70) if i % 2 == 0 else white,
                            [(cx, y + 2), (cx + (w - 8) // 4, y + 2), (cx + (w - 8) // 8, y + 12)])
    pygame.draw.rect(screen, (150, 110, 70), (x + 8, y + 44, w - 16, 26))
    draw_text("CAFE", font_small, (255, 240, 210), (x + w // 2, y + 50), "center", 0)


def draw_book_stall(x, y, w, h):
    pygame.draw.rect(screen, (40, 90, 60), (x, y + h - 46, w, 46))
    pygame.draw.rect(screen, (35, 80, 55), (x - 4, y + h - 54, w + 8, 10))
    palette = [(200, 60, 50), (60, 110, 190), (230, 200, 60), (90, 160, 90)]
    for i in range(min(6, w // 12)):
        c = palette[i % 4]
        pygame.draw.rect(screen, c, (x + 6 + i * 12, y + h - 40, 10, 22))
    pygame.draw.rect(screen, (150, 150, 155), (x, y, w, h - 54))


def draw_phone_booth(x, y, w, h):
    pygame.draw.rect(screen, (200, 30, 30), (x + 4, y + 20, w - 8, h - 20))
    pygame.draw.rect(screen, (30, 30, 40), (x + 10, y + 30, w - 20, h - 40))
    for gy in range(y + 34, y + h - 20, 16):
        pygame.draw.line(screen, (200, 30, 30), (x + 10, gy), (x + w - 10, gy), 2)
    pygame.draw.rect(screen, (200, 30, 30), (x, y + 6, w, 16), border_radius=3)
    pygame.draw.rect(screen, (150, 150, 155), (x + w // 2 - 14, y, 28, 8))


def draw_double_decker(x, y, w, h):
    top_h = (h - 20) // 2
    pygame.draw.rect(screen, (200, 30, 40), (x, y + 6, w, h - 26), border_radius=6)
    pygame.draw.rect(screen, (170, 220, 240), (x + 6, y + 12, w - 12, top_h - 10))
    for i in range(1, 3):
        pygame.draw.line(screen, (200, 30, 40), (x + i * w // 3, y + 12), (x + i * w // 3, y + top_h + 2), 4)
    pygame.draw.rect(screen, (170, 220, 240), (x + 6, y + top_h + 14, w - 12, top_h - 24))
    pygame.draw.rect(screen, white, (x + 4, y + h - 24, w - 8, 6))
    for cx in (x + 24, x + w - 24):
        pygame.draw.circle(screen, (25, 25, 25), (cx, y + h - 8), 12)
        pygame.draw.circle(screen, (170, 170, 175), (cx, y + h - 8), 5)


def draw_yurt(x, y, w, h):
    cx = x + w // 2
    pygame.draw.ellipse(screen, (235, 225, 200), (x, y + h - 90, w, 90))
    pygame.draw.ellipse(screen, (150, 110, 60), (x, y + h - 90, w, 90), 3)
    for i in range(1, 4):
        pygame.draw.line(screen, (150, 110, 60), (x + i * w // 4, y + h - 88), (x + i * w // 4, y + h - 4), 2)
    pygame.draw.polygon(screen, (210, 170, 90), [(x - 4, y + h - 92), (cx, y + h - 150), (x + w + 4, y + h - 92)])
    pygame.draw.circle(screen, (90, 60, 30), (cx, y + h - 150), 6)
    pygame.draw.rect(screen, (150, 150, 155), (x, y, w, max(0, h - 150)))


def draw_dome(x, y, w, h):
    cx = x + w // 2
    r = w // 2
    pygame.draw.rect(screen, (200, 210, 220), (x, y + h - 20, w, 20))
    pygame.draw.polygon(screen, (150, 190, 225), [(x, y + h - 20), (x + w, y + h - 20), (cx, y + h - 20 - r * 2)])
    for k in range(-2, 3):
        pygame.draw.line(screen, (90, 140, 180), (cx, y + h - 20), (cx + k * r // 2, y + h - 20 - r * 2 + 6), 2)
    for k in range(1, 3):
        yy = y + h - 20 - k * r * 2 // 3
        pygame.draw.line(screen, (90, 140, 180), (x + k * 6, yy), (x + w - k * 6, yy), 1)
    pygame.draw.rect(screen, (150, 150, 155), (x, y, w, max(0, h - r * 2 - 20)))


def draw_sushi_cart(x, y, w, h):
    pygame.draw.rect(screen, (60, 40, 30), (x, y + h - 60, w, 60), border_radius=4)
    pygame.draw.rect(screen, (220, 60, 60), (x - 4, y + h - 74, w + 8, 16))
    for i in range(3):
        cx = x + 10 + i * (w - 20) // 2
        pygame.draw.circle(screen, white, (cx, y + h - 40), 9)
        pygame.draw.circle(screen, (230, 60, 60), (cx, y + h - 40), 4)
    pygame.draw.rect(screen, (150, 150, 155), (x, y, w, max(0, h - 74)))
    for cx in (x + 12, x + w - 12):
        pygame.draw.circle(screen, (30, 30, 30), (cx, y + h - 6), 6)


# --- city landmarks (final pad of each city's 5th level) ---------------------
def draw_statue_liberty(x, y, w, h):
    cx = x + w // 2
    pygame.draw.rect(screen, (150, 155, 145), (x + w // 2 - 16, y + h - 34, 32, 34))
    pygame.draw.polygon(screen, (100, 190, 170), [(cx - 22, y + h - 34), (cx + 22, y + h - 34),
                                                    (cx + 14, y + 50), (cx - 14, y + 50)])
    pygame.draw.circle(screen, (110, 195, 175), (cx, y + 40), 16)
    for k in range(7):
        a = math.radians(-90 + k * 180 / 6)
        pygame.draw.line(screen, (230, 210, 90), (cx, y + 26),
                         (cx + 22 * math.cos(a), y + 26 - 22 * math.sin(a)), 3)
    pygame.draw.line(screen, (100, 190, 170), (cx + 14, y + 55), (cx + 34, y + 10), 6)
    pygame.draw.polygon(screen, (230, 210, 90), [(cx + 34, y + 10), (cx + 30, y - 4), (cx + 40, y + 4)])


def draw_baiterek(x, y, w, h):
    cx = x + w // 2
    pygame.draw.rect(screen, (200, 205, 210), (cx - 6, y + 46, 12, h - 46))
    for k in range(-1, 2, 2):
        pygame.draw.line(screen, (170, 175, 180), (cx, y + h - 4), (cx + k * 26, y + h - 4), 3)
        pygame.draw.line(screen, (170, 175, 180), (cx + k * 26, y + h - 4), (cx + k * 4, y + 48), 2)
    pygame.draw.circle(screen, (235, 200, 60), (cx, y + 30), 30)
    pygame.draw.circle(screen, (255, 225, 110), (cx, y + 30), 30, 3)
    pygame.draw.circle(screen, (200, 160, 30), (cx, y + 30), 12)


def draw_tokyo_tower(x, y, w, h):
    cx = x + w // 2
    base = 44
    pygame.draw.polygon(screen, (230, 90, 60), [(cx - base, y + h), (cx + base, y + h), (cx, y)])
    pygame.draw.polygon(screen, white, [(cx - base * 0.55, y + h), (cx + base * 0.55, y + h),
                                        (cx, y + h * 0.35)])
    for k in range(1, 4):
        yy = y + h - k * h // 4
        ww = base * (1 - k / 4.4)
        pygame.draw.line(screen, (230, 90, 60), (cx - ww, yy), (cx + ww, yy), 3)
    pygame.draw.line(screen, (230, 90, 60), (cx, y), (cx, y - 14), 3)


def draw_eiffel(x, y, w, h):
    cx = x + w // 2
    base = 46
    pts_outer = [(cx - base, y + h), (cx - base * 0.4, y + h * 0.45), (cx - 8, y + 20), (cx, y),
                 (cx + 8, y + 20), (cx + base * 0.4, y + h * 0.45), (cx + base, y + h)]
    pygame.draw.lines(screen, (70, 60, 55), False, pts_outer, 4)
    pygame.draw.line(screen, (70, 60, 55), (cx - base, y + h), (cx + base, y + h), 4)
    for k in (0.3, 0.55, 0.8):
        yy = y + h - k * h
        ww = base * (1 - k * 0.85)
        pygame.draw.line(screen, (70, 60, 55), (cx - ww, yy), (cx + ww, yy), 2)
    pygame.draw.line(screen, (70, 60, 55), (cx - base, y + h), (cx + 8, y + 20), 2)
    pygame.draw.line(screen, (70, 60, 55), (cx + base, y + h), (cx - 8, y + 20), 2)


def draw_bigben(x, y, w, h):
    pygame.draw.rect(screen, (190, 165, 100), (x, y + 30, w, h - 30))
    for by in range(y + 40, y + h, 16):
        pygame.draw.line(screen, (160, 135, 75), (x, by), (x + w, by), 1)
    pygame.draw.rect(screen, (150, 120, 60), (x - 4, y + 22, w + 8, 10))
    cx = x + w // 2
    pygame.draw.circle(screen, (245, 235, 210), (cx, y + 12), 16)
    pygame.draw.circle(screen, (90, 70, 30), (cx, y + 12), 16, 2)
    pygame.draw.line(screen, (60, 45, 20), (cx, y + 12), (cx + 8, y + 6), 2)
    pygame.draw.line(screen, (60, 45, 20), (cx, y + 12), (cx, y + 3), 2)
    pygame.draw.polygon(screen, (90, 70, 30), [(cx - 10, y - 4), (cx, y - 22), (cx + 10, y - 4)])


OBJECTS = {
    "crates": draw_crates, "taxi": draw_taxi, "mailbox": draw_mailbox,
    "tree": draw_tree, "office": draw_office, "bus_stop": draw_bus_stop,
    "floor": draw_floor, "dumpster": draw_dumpster, "shop": draw_shop,
    "skyscraper": draw_skyscraper, "chimney": draw_chimney,
    "vending": draw_vending, "clock_tower": draw_clock_tower, "cat": draw_cat,

    "hotdog_cart": lambda x, y, w, h: draw_cart(x, y, w, h, (210, 40, 40), (240, 240, 240), "HOT DOG"),
    "luggage": lambda x, y, w, h: draw_stack(x, y, w, h, (90, 70, 150), (60, 45, 110), True),
    "subway": lambda x, y, w, h: draw_subway(x, y, w, h, (40, 150, 90)),
    "statue_liberty": draw_statue_liberty,

    "yurt": draw_yurt,
    "dome": draw_dome,
    "baiterek": draw_baiterek,

    "torii": draw_torii,
    "sushi_cart": draw_sushi_cart,
    "vending_jp": lambda x, y, w, h: draw_kiosk(x, y, w, h, (230, 40, 60), (250, 250, 250), "自販機"),
    "tokyo_tower": draw_tokyo_tower,

    "cafe": draw_cafe,
    "book_stall": draw_book_stall,
    "eiffel": draw_eiffel,

    "phone_booth": draw_phone_booth,
    "double_decker": draw_double_decker,
    "bigben": draw_bigben,
}


def draw_object(kind, x, y, w):
    OBJECTS[kind](x, y, w, GROUND_Y - y)


# ---------------------------------------------------------------------------
# Levels (each one has its own scenery)
# ---------------------------------------------------------------------------
lvl1 = {"name": "Улица", "sky": (100, 200, 250), "ground": (50, 180, 50),
        "start": (50, 400), "start_obj": "crates",
        "pads": [(300, 450, 150)], "objs": ["taxi"]}
lvl2 = {"name": "Двор", "sky": (140, 215, 245), "ground": (60, 170, 60),
        "start": (50, 450), "start_obj": "mailbox",
        "pads": [(400, 300, 120)], "objs": ["tree"]}
lvl3 = {"name": "Остановка", "sky": (255, 190, 130), "ground": (90, 160, 80),
        "start": (50, 200), "start_obj": "office",
        "pads": [(300, 350, 100), (600, 500, 100)], "objs": ["bus_stop", "floor"]}
lvl4 = {"name": "Центр города", "sky": (150, 170, 230), "ground": (70, 140, 90),
        "start": (50, 450), "start_obj": "dumpster",
        "pads": [(300, 300, 100), (550, 150, 100)], "objs": ["shop", "skyscraper"]}
lvl5 = {"name": "Ночная площадь", "sky": (25, 30, 70), "ground": (30, 100, 50), "night": True,
        "start": (20, 250), "start_obj": "chimney",
        "pads": [(200, 400, 80), (450, 250, 80), (680, 400, 80)],
        "objs": ["vending", "clock_tower", "cat"]}

# a shared layout of takeoff spots and pads, reused by every city so only the
# scenery (start_obj / objs / colors) changes from one city to the next
_START = [(50, 400), (50, 450), (50, 200), (50, 450), (20, 250)]
_PADS = [
    [(300, 450, 150)],
    [(400, 300, 120)],
    [(300, 350, 100), (600, 500, 100)],
    [(300, 300, 100), (550, 150, 100)],
    [(190, 400, 80), (440, 250, 80), (610, 380, 170)],
]


def _city_levels(names, skies, grounds, start_objs, objs_list, night5=False):
    lvls = []
    for i in range(5):
        lv = {"name": names[i], "sky": skies[i], "ground": grounds[i],
              "start": _START[i], "start_obj": start_objs[i],
              "pads": _PADS[i], "objs": objs_list[i]}
        if i == 4 and night5:
            lv["night"] = True
        lvls.append(lv)
    return lvls


ny_levels = _city_levels(
    ["Бруклин", "Квинс", "Центральный парк", "Таймс-сквер", "Остров Свободы"],
    [(120, 190, 235), (150, 205, 235), (170, 215, 190), (140, 160, 200), (20, 25, 60)],
    [(60, 130, 150), (70, 140, 120), (60, 150, 80), (70, 90, 110), (25, 60, 60)],
    ["luggage", "hotdog_cart", "subway", "luggage", "hotdog_cart"],
    [["taxi"], ["hotdog_cart"], ["subway", "luggage"], ["taxi", "subway"],
     ["hotdog_cart", "subway", "statue_liberty"]],
    night5=True,
)

astana_levels = _city_levels(
    ["Степь", "Проспект", "Хан Шатыр", "Экспо", "Байтерек"],
    [(150, 205, 245), (170, 210, 245), (210, 195, 160), (160, 190, 235), (15, 20, 55)],
    [(210, 190, 120), (90, 150, 90), (200, 175, 110), (80, 140, 150), (40, 45, 70)],
    ["yurt", "mailbox", "dome", "yurt", "dome"],
    [["taxi"], ["office"], ["dome", "skyscraper"], ["yurt", "skyscraper"],
     ["dome", "skyscraper", "baiterek"]],
    night5=True,
)

tokyo_levels = _city_levels(
    ["Сибуя", "Асакуса", "Акихабара", "Синдзюку", "Токийская башня"],
    [(190, 215, 245), (235, 205, 170), (170, 195, 240), (150, 160, 210), (15, 15, 45)],
    [(70, 90, 130), (150, 100, 70), (70, 100, 150), (60, 70, 110), (25, 25, 55)],
    ["sushi_cart", "torii", "vending_jp", "sushi_cart", "torii"],
    [["taxi"], ["sushi_cart"], ["vending_jp", "office"], ["torii", "skyscraper"],
     ["vending_jp", "skyscraper", "tokyo_tower"]],
    night5=True,
)

paris_levels = _city_levels(
    ["Монмартр", "Латинский квартал", "Лувр", "Елисейские Поля", "Марсово поле"],
    [(200, 210, 230), (215, 200, 210), (190, 200, 220), (170, 175, 205), (35, 30, 60)],
    [(100, 110, 130), (110, 90, 90), (120, 120, 140), (90, 90, 120), (40, 40, 65)],
    ["book_stall", "cafe", "mailbox", "book_stall", "cafe"],
    [["cafe"], ["book_stall"], ["office", "book_stall"], ["cafe", "skyscraper"],
     ["book_stall", "cafe", "eiffel"]],
    night5=True,
)

london_levels = _city_levels(
    ["Кэмден", "Сохо", "Вестминстер", "Пикадилли", "Биг-Бен"],
    [(180, 190, 200), (170, 180, 195), (150, 160, 180), (140, 150, 175), (20, 22, 40)],
    [(80, 100, 90), (90, 95, 110), (70, 80, 100), (60, 70, 95), (30, 35, 50)],
    ["phone_booth", "double_decker", "phone_booth", "double_decker", "phone_booth"],
    [["double_decker"], ["phone_booth"], ["office", "phone_booth"], ["double_decker", "skyscraper"],
     ["phone_booth", "double_decker", "bigben"]],
    night5=True,
)

CITIES = [
    {"name": "Наш город", "levels": [lvl1, lvl2, lvl3, lvl4, lvl5]},
    {"name": "Нью-Йорк", "levels": ny_levels},
    {"name": "Астана", "levels": astana_levels},
    {"name": "Токио", "levels": tokyo_levels},
    {"name": "Париж", "levels": paris_levels},
    {"name": "Лондон", "levels": london_levels},
]

city_num = 0
levels = CITIES[city_num]["levels"]
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

# fall animation
fall_t = 0
fdir = 1
fx, fy = 0, 0

EDGE_TOLERANCE = 14
GRAVITY = 0.4

# aura + crowd
AURA_MAX = 1_000_000
AURA_MIN = -1_000_000
aura = 0               # real value, from -1,000,000 to +1,000,000
aura_disp = 0.0        # smoothly animated value shown on the bar
landings = 0           # landings in the current run (makes each landing worth more)
last_gain = 0
last_penalty = 0
last_score = 0
MAX_CROWD = 120        # people that can be drawn (the counter itself goes up to 1000)
tick = 0

# flip mode: "front" = frontflip, "back" = backflip (jump with the back to the target)
flip_mode = "front"
flip_bonus = 0.0       # frontflip = 1.0 per flip, backflip = 1.5 per flip

# money and UI
coins = 0
last_coins = 0
shop_open = False
shop_msg = ""
BTN_MODE = pygame.Rect(20, 560, 240, 32)
BTN_SHOP = pygame.Rect(272, 560, 150, 32)
BTN_CITIES = pygame.Rect(432, 560, 150, 32)
SHOP_CLOSE = pygame.Rect(330, 476, 140, 34)
CITY_CLOSE = pygame.Rect(330, 528, 140, 34)
city_select_open = False
unlocked_max = 0                                    # furthest city ever reached (can always be replayed)

revive_count = 0                                    # revives used in the current run, raises the price
BTN_REVIVE = pygame.Rect(250, 330, 300, 46)
BTN_CITY_NEXT = pygame.Rect(230, 330, 340, 46)
BTN_CITY_AGAIN = pygame.Rect(280, 386, 240, 38)

_rng = random.Random(3)
SHIRTS = [(220, 60, 60), (60, 140, 220), (240, 190, 50), (90, 200, 110),
          (190, 90, 220), (240, 130, 60), (240, 240, 240), (60, 200, 200)]
SKINS = [(255, 220, 185), (240, 190, 150), (200, 150, 110), (150, 100, 70)]
HAIRS = [(40, 30, 20), (90, 60, 30), (200, 160, 60), (20, 20, 20), (150, 60, 40)]
crowd = [{"x": _rng.randint(10, 790), "row": i % 3, "shirt": _rng.choice(SHIRTS),
          "skin": _rng.choice(SKINS), "hair": _rng.choice(HAIRS),
          "phase": _rng.random() * 6.28} for i in range(MAX_CROWD)]
stars = [(_rng.randint(0, 800), _rng.randint(0, 380), _rng.choice([1, 1, 2])) for _ in range(70)]
clouds = [(80, 90, 1.0), (330, 140, 0.8), (560, 70, 1.2), (720, 160, 0.9)]


def aura_frac(a):
    """Position on a logarithmic scale: 0 -> 0.0, 1,000,000 -> 1.0 (sign ignored)."""
    return max(0.0, min(1.0, math.log10(1 + abs(a)) / 6))


def people_count():
    return int(math.sqrt(max(aura, 0)))        # 1,000 people at 1,000,000 aura


def aura_tier(a):
    if a < 0:
        return "Позор"
    if a < 1_000:
        return "Новичок"
    if a < 10_000:
        return "Заметный"
    if a < 100_000:
        return "Звезда"
    if a < AURA_MAX:
        return "Легенда"
    return "МЕГА-ЛЕГЕНДА!"


def miss_penalty(factor=1.0):
    """Missing the object costs aura. Even at 0 aura it drops below zero."""
    global aura, last_penalty
    p = int((200 * (lvl_num + 1) + 0.4 * max(aura, 0)) * factor)
    aura = max(AURA_MIN, aura - p)
    last_penalty = p


def setup_level():
    global px, py, pad_num, state
    px = levels[lvl_num]["start"][0]
    py = levels[lvl_num]["start"][1] - 80
    pad_num = 0
    reset_jump()


def reset_jump():
    global vx, vy, angle, power, spinning, flips, rot, state, fall_t, flip_bonus
    vx, vy, angle, power, rot, flips = 0, 0, 0, 0, 0, 0
    flip_bonus = 0.0
    fall_t = 0
    spinning = False
    state = "wait"


def reposition_to_pad():
    """Put the character back on the last pad he successfully stood on
    (or the takeoff spot, if he hasn't landed on anything yet)."""
    global px, py
    lvl = levels[lvl_num]
    if pad_num == 0:
        sx, sy = lvl["start"]
        px, py = sx, sy - 80
    else:
        prev = lvl["pads"][pad_num - 1]
        px, py = prev[0] + (prev[2] - 40) // 2, prev[1] - 80


def restart_game():
    global city_num, levels, lvl_num, score, landings, last_gain, last_penalty, revive_count
    city_num = 0
    levels = CITIES[city_num]["levels"]
    lvl_num = 0
    score = 0
    landings = 0        # aura is kept between attempts (it can be negative)
    last_gain = 0
    last_penalty = 0
    revive_count = 0
    setup_level()


def travel_to_next_city():
    """Move on to the next city's level 1, keeping score/aura/coins/landings."""
    global city_num, levels, lvl_num, unlocked_max
    if city_num < len(CITIES) - 1:
        city_num += 1
        unlocked_max = max(unlocked_max, city_num)
        levels = CITIES[city_num]["levels"]
        lvl_num = 0
        setup_level()


def select_city(i):
    """Jump straight to any city the player has already unlocked."""
    global city_num, levels, lvl_num
    if 0 <= i <= unlocked_max:
        city_num = i
        levels = CITIES[city_num]["levels"]
        lvl_num = 0
        setup_level()


def replay_city():
    """Play the current city again from level 1 (e.g. to earn more coins)."""
    global lvl_num
    lvl_num = 0
    setup_level()


def revive_cost():
    return 100 * (revive_count + 1) + 60 * (lvl_num + 1)


def do_revive():
    """Pay coins to continue the same attempt instead of restarting the city."""
    global coins, revive_count, state, last_penalty
    if state != "dead":
        return
    cost = revive_cost()
    if coins < cost:
        return
    coins -= cost
    revive_count += 1
    last_penalty = 0
    reposition_to_pad()
    reset_jump()


def launch_velocity(pw):
    """Launch speed for a given power, including the bonuses of the equipped sneakers."""
    sh = current_shoe()
    return (3 + pw / 20) * sh["speed"], (-6 - pw / 10) * sh["jump"]


def pad_collision(prev_feet, x, y, vel_y, pad):
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
    v_x, v_y = launch_velocity(power)
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
            dots.append((x + 20, pad[1]))
            break
        if hit == "wall" or y > 600 or x > 820:
            break
        if step % 4 == 3:
            dots.append((x + 20, y + 40))
    return dots


# ---------------------------------------------------------------------------
# Drawing: scenery, crowd, player
# ---------------------------------------------------------------------------
def draw_background(level):
    if images_loaded:
        screen.blit(bg_img, (0, 0))
        return
    screen.fill(level["sky"])
    if level.get("night"):
        for sx_, sy_, sz in stars:
            if (tick // 20 + sx_) % 7 != 0:
                pygame.draw.circle(screen, (240, 240, 255), (sx_, sy_), sz)
        pygame.draw.circle(screen, (240, 240, 215), (700, 100), 30)
        pygame.draw.circle(screen, level["sky"], (713, 91), 26)
    else:
        for cx, cy, sc in clouds:
            x = int((cx + tick * 0.15 * sc) % 900) - 50
            for dx, dy, r in ((0, 0, 22), (24, 6, 18), (-24, 8, 16), (8, -10, 18)):
                pygame.draw.circle(screen, (255, 255, 255), (x + int(dx * sc), cy + int(dy * sc)), int(r * sc))
    pygame.draw.rect(screen, level["ground"], (0, GROUND_Y, 800, 50))


def draw_person(cx, fy, s, shirt, skin, hair, arms_up):
    def S(v):
        return max(1, int(v * s))
    pygame.draw.line(screen, (40, 45, 70), (cx - S(2.5), fy - S(12)), (cx - S(2.5), fy), S(3))
    pygame.draw.line(screen, (40, 45, 70), (cx + S(2.5), fy - S(12)), (cx + S(2.5), fy), S(3))
    pygame.draw.rect(screen, shirt, (cx - S(5), fy - S(25), S(10), S(14)), border_radius=S(3))
    if arms_up:
        pygame.draw.line(screen, skin, (cx - S(5), fy - S(23)), (cx - S(9), fy - S(34)), S(3))
        pygame.draw.line(screen, skin, (cx + S(5), fy - S(23)), (cx + S(9), fy - S(34)), S(3))
    else:
        pygame.draw.line(screen, skin, (cx - S(5), fy - S(23)), (cx - S(7), fy - S(13)), S(3))
        pygame.draw.line(screen, skin, (cx + S(5), fy - S(23)), (cx + S(7), fy - S(13)), S(3))
    pygame.draw.circle(screen, skin, (cx, fy - S(30)), S(5))
    pygame.draw.rect(screen, hair, (cx - S(5), fy - S(36), S(10), S(4)),
                     border_top_left_radius=S(4), border_top_right_radius=S(4))


ROWS = {0: (548, 1.0), 1: (535, 0.85), 2: (523, 0.7)}   # (feet y, scale)


def draw_crowd(n, cheer):
    n = min(n, MAX_CROWD)
    if n <= 0:
        return
    fr = aura_frac(aura_disp)
    amp = 2 + fr * 6 + (6 if cheer else 0)
    for row in (2, 1, 0):                    # back row first
        fy_base, s = ROWS[row]
        for p in crowd[:n]:
            if p["row"] != row:
                continue
            jump = int(abs(math.sin(tick * 0.14 + p["phase"])) * amp)
            arms = cheer or (fr > 0.3 and math.sin(tick * 0.15 + p["phase"]) > 0.2)
            draw_person(p["x"], fy_base - jump, s, p["shirt"], p["skin"], p["hair"], arms)


def draw_glow(cx, cy):
    fr = aura_frac(aura_disp)
    if fr < 0.02:
        return
    R = int(34 + fr * 45 + 3 * math.sin(tick * 0.1))
    if aura_disp < 0:
        col = mix((120, 20, 30), (255, 50, 50), fr)
    else:
        col = mix((160, 80, 240), (255, 210, 60), fr)
    g = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    for k in range(4):
        pygame.draw.circle(g, (*col, 25 + k * 18), (R, R), R - k * R // 5)
    screen.blit(g, (cx - R, cy - R))


def draw_player():
    back = flip_mode == "back"          # backflip: back turned to the landing spot
    if state == "sit":
        surf = surf_crouch_b if back else surf_crouch
        draw_y = py + 30 if images_loaded else py
    elif state == "fly" and spinning:
        surf = surf_tuck_b if back else surf_tuck    # knees tucked to the chest mid-flip
        draw_y = py
    elif state in ("fly", "fall"):
        surf = surf_air_b if back else surf_air
        draw_y = py
    else:
        surf = surf_stand_b if back else surf_stand
        draw_y = py
    if state != "dead":
        draw_glow(px + 20, draw_y + 40)
    rot_surf = pygame.transform.rotate(surf, angle)
    rect = rot_surf.get_rect(center=(px + 20, draw_y + 40))
    screen.blit(rot_surf, rect)


def draw_hud():
    panel = pygame.Surface((800, 88), pygame.SRCALPHA)
    panel.fill((10, 10, 25, 120))
    screen.blit(panel, (0, 0))

    draw_text(f"{city_num + 1}/6 {CITIES[city_num]['name']}", font1, white, (16, 6))
    draw_text(f"Уровень {lvl_num + 1}/5 · {levels[lvl_num]['name']}", font_small,
              (255, 240, 200), (16, 34), "left", 1)
    draw_text(f"Очки: {score}", font_small, white, (16, 54), "left", 1)

    draw_text(f"Люди: {people_count():,}", font_small, white, (784, 6), "right", 1)
    draw_text(f"Монеты: {coins:,}", font_small, (255, 215, 80), (784, 26), "right", 1)
    draw_text(f"Кроссовки: {current_shoe()['name']}", font_small, current_shoe()["color"],
              (784, 46), "right", 1)

    # aura bar: logarithmic scale, so it moves at 100 aura as well as at 1,000,000
    # kept clear of the city/level text on the left and the stats on the right
    bx, by, bw, bh = 300, 10, 260, 24
    pygame.draw.rect(screen, (25, 20, 45), (bx, by, bw, bh), border_radius=12)
    fr = aura_frac(aura_disp)
    fw = int(bw * fr)
    if fw > 0:
        if aura_disp < 0:
            col = mix((120, 20, 30), (255, 60, 60), fr)
        else:
            col = mix((160, 80, 240), (255, 210, 60), fr)
        pygame.draw.rect(screen, col, (bx, by, max(fw, 8), bh), border_radius=12)
    pygame.draw.rect(screen, white, (bx, by, bw, bh), 2, border_radius=12)
    draw_text(f"АУРА {int(round(aura_disp)):,}", font_small, white, (bx + bw // 2, by + 2), "center", 1)
    tier_col = (255, 90, 90) if aura < 0 else mix((190, 140, 255), (255, 220, 90), aura_frac(aura))
    draw_text(aura_tier(aura), font_small, tier_col, (bx + bw // 2, by + bh + 6), "center", 1)


def ui_allowed():
    """Mode/shop buttons work only while actively playing, between jumps."""
    return state in ("wait", "land")


def toggle_mode():
    global flip_mode
    flip_mode = "back" if flip_mode == "front" else "front"


def shop_button_rect(i):
    return pygame.Rect(120 + 560 - 132, 108 + i * 92 + 22, 116, 40)


def handle_click(pos):
    global shop_open, shoe_id, coins, shop_msg, city_select_open
    if city_select_open:
        if CITY_CLOSE.collidepoint(pos):
            city_select_open = False
            return
        for i in range(len(CITIES)):
            if city_row_button(i).collidepoint(pos) and i <= unlocked_max:
                select_city(i)
                city_select_open = False
        return
    if shop_open:
        if SHOP_CLOSE.collidepoint(pos):
            shop_open = False
            return
        for i, sh in enumerate(SHOES):
            if shop_button_rect(i).collidepoint(pos):
                if sh["id"] in owned_shoes:
                    shoe_id = sh["id"]
                    build_sprites()
                    shop_msg = ""
                elif coins >= sh["price"]:
                    coins -= sh["price"]
                    owned_shoes.add(sh["id"])
                    shoe_id = sh["id"]
                    build_sprites()
                    shop_msg = ""
                else:
                    shop_msg = "Не хватает монет!"
        return
    if state == "dead" and BTN_REVIVE.collidepoint(pos):
        do_revive()
        return
    if state == "city_clear":
        if BTN_CITY_NEXT.collidepoint(pos):
            travel_to_next_city()
        elif BTN_CITY_AGAIN.collidepoint(pos):
            replay_city()
        return
    if not ui_allowed():
        return
    if BTN_MODE.collidepoint(pos):
        toggle_mode()
    elif BTN_SHOP.collidepoint(pos):
        shop_open = True
        shop_msg = ""
    elif BTN_CITIES.collidepoint(pos):
        city_select_open = True


def draw_button(rect, text, enabled=True, active=False):
    hover = enabled and rect.collidepoint(pygame.mouse.get_pos())
    if not enabled:
        bg, fg, border = (60, 60, 70), (150, 150, 155), (110, 110, 115)
    elif active:
        bg, fg, border = ((255, 180, 80) if hover else (255, 150, 40)), (30, 20, 10), white
    else:
        bg, fg, border = ((70, 70, 100) if hover else (40, 40, 60)), white, white
    pygame.draw.rect(screen, bg, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, 2, border_radius=8)
    img = font_small.render(text, True, fg)
    screen.blit(img, img.get_rect(center=rect.center))


def draw_buttons():
    en = ui_allowed() and not shop_open and not city_select_open
    back = flip_mode == "back"
    draw_button(BTN_MODE, "БЭКФЛИП: ВКЛ" if back else "БЭКФЛИП: ВЫКЛ", en, back)
    draw_button(BTN_SHOP, "МАГАЗИН", en)
    draw_button(BTN_CITIES, "ГОРОДА", en)


def draw_shoe_icon(x, y, sh):
    pygame.draw.polygon(screen, sh["color"],
                        [(x + 2, y + 14), (x + 4, y - 8), (x + 22, y - 8), (x + 34, y + 2),
                         (x + 54, y + 6), (x + 56, y + 14)])
    pygame.draw.line(screen, sh["stripe"], (x + 10, y + 2), (x + 30, y + 10), 3)
    pygame.draw.line(screen, (30, 30, 40), (x + 8, y - 3), (x + 20, y - 3), 1)
    pygame.draw.rect(screen, (245, 245, 245), (x, y + 14, 58, 7), border_radius=3)
    pygame.draw.polygon(screen, (30, 30, 40),
                        [(x + 2, y + 14), (x + 4, y - 8), (x + 22, y - 8), (x + 34, y + 2),
                         (x + 54, y + 6), (x + 56, y + 14)], 2)


def draw_shop():
    overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))
    panel = pygame.Rect(100, 50, 600, 470)
    pygame.draw.rect(screen, (30, 30, 50), panel, border_radius=14)
    pygame.draw.rect(screen, white, panel, 2, border_radius=14)
    draw_text("МАГАЗИН КРОССОВОК", font1, white, (120, 62))
    draw_text(f"МОНЕТЫ: {coins:,}", font1, (255, 215, 80), (680, 62), "right")
    for i, sh in enumerate(SHOES):
        y = 108 + i * 92
        equipped = sh["id"] == shoe_id
        card = pygame.Rect(120, y, 560, 84)
        pygame.draw.rect(screen, (60, 90, 70) if equipped else (55, 55, 85), card, border_radius=10)
        pygame.draw.rect(screen, sh["color"], card, 2, border_radius=10)
        draw_shoe_icon(136, y + 30, sh)
        draw_text(sh["name"], font1, sh["color"], (215, y + 6), "left", 1)
        draw_text(sh["desc"], font_small, white, (215, y + 38), "left", 1)
        draw_text(f"Высота x{sh['jump']:g}  •  Скорость x{sh['speed']:g}", font_small,
                  (190, 190, 210), (215, y + 58), "left", 1)
        rect = shop_button_rect(i)
        if equipped:
            draw_button(rect, "НАДЕТО", False)
        elif sh["id"] in owned_shoes:
            draw_button(rect, "НАДЕТЬ", True, True)
        else:
            draw_button(rect, f"КУПИТЬ {sh['price']}", coins >= sh["price"])
    if shop_msg:
        draw_text(shop_msg, font_small, (255, 100, 100), (120, 486), "left", 1)
    draw_button(SHOP_CLOSE, "ЗАКРЫТЬ (Esc)")


def city_row_button(i):
    return pygame.Rect(560, 108 + i * 70 + 8, 130, 40)


def draw_city_select():
    overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))
    panel = pygame.Rect(90, 40, 620, 528)
    pygame.draw.rect(screen, (30, 30, 50), panel, border_radius=14)
    pygame.draw.rect(screen, white, panel, 2, border_radius=14)
    draw_text("ВЫБОР ГОРОДА", font1, white, (110, 54))
    for i, c in enumerate(CITIES):
        y = 108 + i * 70
        unlocked = i <= unlocked_max
        current = i == city_num
        card = pygame.Rect(110, y, 560, 60)
        bg = (60, 90, 70) if current else ((55, 55, 85) if unlocked else (45, 45, 50))
        pygame.draw.rect(screen, bg, card, border_radius=10)
        pygame.draw.rect(screen, white if unlocked else (100, 100, 105), card, 2, border_radius=10)
        name_col = white if unlocked else (140, 140, 145)
        draw_text(f"{i + 1}. {c['name']}", font1, name_col, (128, y + 8), "left", 1)
        if not unlocked:
            draw_text("Закрыто — сначала пройди предыдущий город", font_small,
                      (200, 130, 130), (128, y + 38), "left", 1)
        elif current:
            draw_text("ты здесь сейчас", font_small, (190, 220, 200), (128, y + 38), "left", 1)
        rect = city_row_button(i)
        if current:
            draw_button(rect, "ЗДЕСЬ", False)
        elif unlocked:
            draw_button(rect, "ЕХАТЬ", True, True)
        else:
            draw_button(rect, "ЗАКРЫТО", False)
    draw_button(CITY_CLOSE, "ЗАКРЫТЬ (Esc)")


setup_level()
clock = pygame.time.Clock()

run = True
while run:
    tick += 1
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            run = False

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            handle_click(ev.pos)

        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            shop_open = False
            city_select_open = False

        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_b \
                and not shop_open and not city_select_open and ui_allowed():
            toggle_mode()

        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE and not shop_open and not city_select_open:
            if state == "wait":
                state = "sit"
            elif state == "fly":
                spinning = True
            elif state == "land":
                pad_num += 1
                if pad_num >= len(levels[lvl_num]["pads"]):
                    if lvl_num >= len(levels) - 1:
                        state = "win" if city_num >= len(CITIES) - 1 else "city_clear"
                    else:
                        lvl_num += 1
                        setup_level()
                else:
                    reset_jump()
            elif state == "city_clear":
                travel_to_next_city()
            elif state in ("dead", "win"):
                restart_game()

        if ev.type == pygame.KEYUP and ev.key == pygame.K_SPACE:
            if state == "sit":
                state = "fly"
                vx, vy = launch_velocity(power)
            elif state == "fly":
                spinning = False

    # ------------------------------------------------------------------ logic
    aura_disp += (aura - aura_disp) * 0.08
    if abs(aura - aura_disp) < 1:
        aura_disp = float(aura)

    _tier = appearance_tier(aura)
    if _tier != current_appearance:
        current_appearance = _tier
        build_sprites()

    if state == "sit":
        power += 2.5 * power_dir
        if power > 100 or power < 0:
            power_dir *= -1
        # lean toward the flight direction (in backflip mode that is backwards for him)
        angle = -(power / 100) * 40

    elif state == "fly":
        prev_feet = py + 80
        px += vx
        py += vy
        vy += GRAVITY

        if spinning:
            # rotation is always toward the flight direction; in backflip mode the
            # character faces away, so it is a real backflip
            spin_rate = current_shoe()["spin"]
            angle -= spin_rate
            rot += spin_rate
            if rot >= 360:
                flips += 1
                flip_bonus += 1.5 if flip_mode == "back" else 1.0   # backflips are harder
                rot -= 360

        cur_pad = levels[lvl_num]["pads"][pad_num]
        tx, ty, tw = cur_pad
        hit = pad_collision(prev_feet, px, py, vy, cur_pad)

        if py > 600:
            state = "dead"
            miss_penalty()

        elif hit == "top":
            py = ty - 80
            vy = 0
            cx = px + 20
            if tx <= cx <= tx + tw:
                norm_angle = abs(angle % 360)
                if norm_angle < 40 or norm_angle > 320:
                    state = "land"
                    angle = 0
                    last_score = 50 + int(flip_bonus * 100)
                    score += last_score
                    # each landing is worth 3x more than the previous one, flips multiply it
                    landings += 1
                    last_gain = int(25 * 3 ** landings * (1 + flip_bonus))
                    aura = min(AURA_MAX, aura + last_gain)
                    last_coins = int((10 + 5 * (lvl_num + 1) + int(flip_bonus * 20)
                                      + people_count() // 10) * current_shoe()["coins"])
                    coins += last_coins
                else:
                    state = "dead"
                    angle = -90
                    py = ty - 52
                    miss_penalty(0.5)         # landed on it, but crashed
            else:
                state = "fall"
                spinning = False
                fall_t = 0
                fdir = -1 if cx < tx else 1
                fx, fy = cx, ty
                angle = 0
                miss_penalty()                # only touched the edge

        elif hit == "wall":
            state = "fall"
            spinning = False
            fall_t = 25
            fdir = -1 if (px + 20) < tx + tw / 2 else 1
            px = tx - 33 if fdir == -1 else tx + tw - 7
            vy = -3
            miss_penalty()                    # hit the wall of the object

    elif state == "fall":
        if fall_t < 25:
            fall_t += 1
            fx += fdir * 0.7
            angle = -fdir * fall_t * 2.6
            a = math.radians(angle)
            px = fx - 40 * math.sin(a) - 20
            py = fy - 40 * math.cos(a) - 40
        else:
            fall_t += 1
            px += fdir * 1.6
            vy += 0.5
            py += vy
            angle += -fdir * 7
            if py > 600:
                state = "dead"

    # ---------------------------------------------------------------- drawing
    level = levels[lvl_num]
    draw_background(level)
    draw_crowd(people_count(), state in ("land", "win", "city_clear"))

    # a falling character is drawn behind the objects so it drops past them
    if state == "fall":
        draw_player()

    sx, sy = level["start"]
    draw_object(level["start_obj"], sx, sy, 60)

    for i, pad in enumerate(level["pads"]):
        draw_object(level["objs"][i], pad[0], pad[1], pad[2])
        pad_color = (200, 200, 200)
        if i == pad_num and state not in ("win", "city_clear"):
            pad_color = (255, 50, 50)
        elif i < pad_num or state in ("win", "city_clear"):
            pad_color = (50, 200, 50)
        pygame.draw.rect(screen, pad_color, (pad[0], pad[1], pad[2], 6))

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

    draw_hud()
    if state in ("wait", "land"):
        draw_buttons()

    if state == "wait":
        draw_text("Жми ПРОБЕЛ", font1, white, (px - 20, py - 40))
    elif state == "sit":
        pygame.draw.rect(screen, (255, 0, 0), (px - 10, py - 15, int(power / 1.5), 8))
        draw_text("Отпускай!", font1, (255, 100, 100), (px - 10, py - 40))
    elif state == "fly" and flips > 0:
        label = "Бэкфлип" if flip_mode == "back" else "Сальто"
        draw_text(f"{label}: {flips}", font1, (255, 200, 0), (px - 10, py - 40))

    if state == "land":
        draw_text(f"КРУТО! +{last_score}", font_big, (50, 255, 50), (400, 190), "center", 3)
        draw_text(f"+{last_gain:,} АУРЫ  •  людей: {people_count():,}", font1, (220, 170, 255),
                  (400, 262), "center")
        draw_text(f"+{last_coins} МОНЕТ", font1, (255, 215, 80), (400, 296), "center")

    elif state == "fall":
        draw_text(f"ПРОМАХ!  -{last_penalty:,} АУРЫ", font1, (255, 80, 80), (400, 110), "center")

    elif state == "dead":
        draw_text("АУЧ! ЗАНОВО", font_big, (255, 50, 50), (400, 150), "center", 3)
        if last_penalty:
            draw_text(f"-{last_penalty:,} АУРЫ", font1, (255, 120, 120), (400, 222), "center")
        cost = revive_cost()
        can_pay = coins >= cost
        draw_button(BTN_REVIVE, f"ОЖИТЬ ЗДЕСЬ ЗА {cost:,} МОНЕТ", can_pay, can_pay)
        draw_text("(продолжить с этого места)", font_small, (200, 200, 210), (400, 380), "center", 1)
        draw_text("ПРОБЕЛ — начать город заново", font1, white, (400, 430), "center")

    elif state == "city_clear":
        next_name = CITIES[city_num + 1]["name"]
        draw_text(f"ГОРОД «{CITIES[city_num]['name']}» ПРОЙДЕН!", font_big, (255, 200, 0),
                  (400, 150), "center", 3)
        draw_text(f"Аура: {int(aura):,}  •  Людей: {people_count():,}  •  Монеты: {coins:,}",
                  font1, white, (400, 236), "center")
        draw_button(BTN_CITY_NEXT, f"ЕХАТЬ В {next_name.upper()} (ПРОБЕЛ)", True, True)
        draw_button(BTN_CITY_AGAIN, "ПРОЙТИ ЕЩЁ РАЗ")

    elif state == "win":
        draw_text("ТЫ ОБЪЕХАЛ ВСЕ ГОРОДА!", font_big, (255, 200, 0), (400, 190), "center", 3)
        draw_text(f"Аура: {int(aura):,}  •  Людей: {people_count():,}  •  Очки: {score}",
                  font1, white, (400, 262), "center")
        draw_text("ПРОБЕЛ — начать заново", font1, (220, 220, 230), (400, 300), "center")

    if shop_open:
        draw_shop()
    if city_select_open:
        draw_city_select()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
