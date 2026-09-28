import pygame
import sys
import os

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

def setup_level():
    global px, py, pad_num, state
    px = levels[lvl_num]["start"][0]
    py = levels[lvl_num]["start"][1] - 80
    pad_num = 0
    reset_jump()

def reset_jump():
    global vx, vy, angle, power, spinning, flips, rot, state
    vx, vy, angle, power, rot, flips = 0, 0, 0, 0, 0, 0
    spinning = False
    state = "wait"

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

    if state == "sit":
        power += 2.5 * power_dir
        if power > 100 or power < 0:
            power_dir *= -1
        angle = -(power / 100) * 40

    elif state == "fly":
        px += vx
        py += vy
        vy += 0.4
        
        if spinning:
            angle -= 14
            rot += 14
            if rot >= 360:
                flips += 1
                rot = 0
                
        cur_pad = levels[lvl_num]["pads"][pad_num]
        tx, ty, tw = cur_pad[0], cur_pad[1], cur_pad[2]
        
        if py > 600:
            state = "dead"
        elif vy > 0 and (ty <= py + 80 <= ty + 20):
            if tx <= px + 20 <= tx + tw:
                py = ty - 80
                vy = 0
                norm_angle = abs(angle % 360)
                if norm_angle < 40 or norm_angle > 320:
                    state = "land"
                    score += 50 + (flips * 100)
                else:
                    state = "dead"

    if images_loaded:
        screen.blit(bg_img, (0, 0)) 
    else:
        screen.fill((100, 200, 250)) 
        pygame.draw.rect(screen, (50, 180, 50), (0, 550, 800, 50))
    
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

    if images_loaded:
        surf = player_img.copy() 
    else:
        surf = pygame.Surface((40, 80), pygame.SRCALPHA)
        surf.fill((40, 40, 40))
        pygame.draw.rect(surf, white, (0, 10, 15, 15))
    
    if state == "sit":
        surf = pygame.transform.scale(surf, (40, 50))
        draw_y = py + 30
    else:
        draw_y = py
        
    rot_surf = pygame.transform.rotate(surf, angle)
    rect = rot_surf.get_rect(center=(px+20, draw_y+40))
    screen.blit(rot_surf, rect)

    screen.blit(font1.render(f"УРОВЕНЬ: {lvl_num + 1}/5", True, white), (20, 520))
    screen.blit(font1.render(f"ОЧКИ: {score}", True, white), (640, 520))

    if state == "wait":
        screen.blit(font1.render("Жми ПРОБЕЛ", True, white), (px - 20, py - 40))
    elif state == "sit":
        pygame.draw.rect(screen, (255,0,0), (px-10, py-15, int(power/1.5), 8))
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
