import pygame
import sys
import time

# ========== 初始化 ==========
pygame.init()

# 模拟240x240屏幕，放大到480x480方便观看
SCALE = 2
SCREEN_W, SCREEN_H = 240 * SCALE, 240 * SCALE
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("像素电子宠物 - PC版")
clock = pygame.time.Clock()

# 颜色定义 (RGB)
C_B = (0, 0, 0)
C_W = (255, 255, 255)
C_O = (255, 150, 60)
C_C = (250, 240, 220)
C_P = (255, 160, 180)
C_BR = (160, 90, 50)
C_SK = (135, 206, 235)
C_G = (50, 180, 50)
C_GD = (30, 140, 30)
C_Y = (255, 255, 0)
C_SH = (60, 60, 60)
C_F = (255, 180, 50)
C_HUN = (255, 80, 80)
C_SLP = (100, 180, 255)
C_HAP = (50, 255, 100)

# 颜色方案
SCHEMES = [
    (C_O, C_C, '柴犬'),
    ((100,100,100), (180,180,180), '灰狗'),
    ((139,69,19), (210,180,140), '棕狗'),
    ((255,215,0), (255,250,205), '金毛'),
]
c_color = 0

def get_main(): return SCHEMES[c_color][0]
def get_face(): return SCHEMES[c_color][1]

# 状态
affection, saturation = 50, 60
MAX_A, MAX_S = 100, 100
A_DECAY, S_DECAY = 2, 10
PET_LIMIT = 10
pet_today, last_pet_day, last_decay = 0, -1, 0
menu_on, flash_on = False, False
flash_val, flash_t = 0, 0
sleeping = False
SCREEN_LIMIT = 5 * 3600
screen_start = time.time()

# 尾巴摇摆
tail_wagging = False
wag_count = 0
wag_frame = 0
wag_timer = 0
WAG_MAX = 3
WAG_SPEED = 8
WAG_OFFSET = 1

# 眨眼
blinking = False
blink_frame = 0
blink_timer = 0
BLINK_INTERVAL = 100
BLINK_DURATION = 3

FOODS = [25, 20, 15, 18]

BS = 4

# ========== 像素数据 ==========
head = [
    "000000000000000000","000000000000000000","000000000000000000",
    "000011111111110000","000111111111111000","001111111111111100",
    "001112222222221100","011122222222222110","011222222222222210",
    "111222222222222211","111222222222222211","111222222222222211",
    "011222222222222210","011122222222222110","001112222222221100",
    "000111111111111000","000011111111110000","000000000000000000",
]
body = [
    "000011111111000000","001111111111110000","011111111111111000",
    "011122222222211100","011222222222221100","011222222222221100",
    "011122222222211100","001112222222211000","000111111111110000",
    "000011111111100000","000001111111000000","000000111110000000",
    "000000011100000000","000000001000000000",
]
fleg = ["01110","11111","12221","12221","11111","01110"]
bleg = ["011110","111111","122221","122221","111111"]
tail_base = [
    "00000000","00000110","00001111","00011121","00111221","00112210","00112100","00011000",
]

# ========== 绘制函数 ==========
def b(surf, x, y, c, s):
    x, y, s = int(x), int(y), int(s)
    pygame.draw.rect(surf, c, (x, y, s, s))

def scene(surf):
    surf.fill(C_SK)
    pygame.draw.rect(surf, C_Y, (175*SCALE, 35*SCALE, 20*SCALE, 20*SCALE))
    pygame.draw.rect(surf, C_G, (0, 150*SCALE, 240*SCALE, 90*SCALE))
    for y in range(150*SCALE, 240*SCALE, 4*SCALE):
        for x in range(0, 240*SCALE, 4*SCALE):
            b(surf, x, y, C_GD, SCALE)

def draw_tail(surf, cx, cy, sc, wag_dy=0):
    p = BS * SCALE * sc
    mc2, fc2 = get_main(), get_face()
    tx = cx + 7 * p
    ty = cy + 6 * p + wag_dy * p
    for r, row in enumerate(tail_base):
        for c, ch in enumerate(row):
            if ch == '1':
                b(surf, tx + (c - 3) * p, ty + (r - 3) * p, mc2, p)
            elif ch == '2':
                b(surf, tx + (c - 3) * p, ty + (r - 3) * p, fc2, p)

def draw_eyes(surf, cx, cy, sc, closed=False):
    p = BS * SCALE * sc
    hy = cy - 2 * p
    if closed:
        b(surf, cx - 4*p, hy - 1*p, C_B, p)
        b(surf, cx - 3*p, hy - 1*p, C_B, p)
        b(surf, cx + 3*p, hy - 1*p, C_B, p)
        b(surf, cx + 4*p, hy - 1*p, C_B, p)
    else:
        b(surf, cx - 3*p, hy - 1*p, C_W, p)
        b(surf, cx + 3*p, hy - 1*p, C_W, p)
        b(surf, cx - 4*p, hy, C_B, p)
        b(surf, cx - 3*p, hy, C_B, p)
        b(surf, cx + 3*p, hy, C_B, p)
        b(surf, cx + 4*p, hy, C_B, p)

def draw_pet(surf, cx, cy, sc):
    p = BS * SCALE * sc
    mc2, fc2 = get_main(), get_face()
    for dx in range(-12, 13):
        b(surf, cx+dx*p, cy+22*p, C_SH, p)
    if tail_wagging:
        if wag_frame == 0:
            draw_tail(surf, cx, cy, sc, -WAG_OFFSET)
        else:
            draw_tail(surf, cx, cy, sc, WAG_OFFSET)
    else:
        draw_tail(surf, cx, cy, sc, 0)
    for bx, by in [(cx-6*p, cy+12*p), (cx+6*p, cy+12*p)]:
        for r, row in enumerate(bleg):
            for c, ch in enumerate(row):
                if ch == '1': b(surf, bx+(c-3)*p, by+(r-2)*p, mc2, p)
                elif ch == '2': b(surf, bx+(c-3)*p, by+(r-2)*p, fc2, p)
    bx, by = cx, cy+10*p
    for r, row in enumerate(body):
        for c, ch in enumerate(row):
            if ch == '1': b(surf, bx+(c-9)*p, by+(r-7)*p, mc2, p)
            elif ch == '2': b(surf, bx+(c-9)*p, by+(r-7)*p, fc2, p)
    for fx, fy in [(cx-4*p, cy+13*p), (cx+4*p, cy+13*p)]:
        for r, row in enumerate(fleg):
            for c, ch in enumerate(row):
                if ch == '1': b(surf, fx+(c-2)*p, fy+(r-3)*p, mc2, p)
                elif ch == '2': b(surf, fx+(c-2)*p, fy+(r-3)*p, fc2, p)
    hy = cy - 2*p
    for r, row in enumerate(head):
        for c, ch in enumerate(row):
            if ch == '1': b(surf, cx+(c-9)*p, hy+(r-9)*p, mc2, p)
            elif ch == '2': b(surf, cx+(c-9)*p, hy+(r-9)*p, fc2, p)
    for ex in [cx-6*p, cx-5*p, cx+4*p, cx+5*p]:
        for ey in [hy-3*p, hy-2*p]:
            b(surf, ex, ey, mc2, p)
    draw_eyes(surf, cx, cy, sc, closed=blinking and blink_frame == 1)
    b(surf, cx-1*p, hy+2*p, C_BR, p); b(surf, cx, hy+2*p, C_BR, p)
    b(surf, cx+1*p, hy+2*p, C_BR, p); b(surf, cx, hy+3*p, C_BR, p)
    for dx in [-2,-1,0,1,2]:
        b(surf, cx+dx*p, hy+4*p, C_B, p)
    b(surf, cx-5*p, hy+1*p, C_P, p); b(surf, cx-4*p, hy+1*p, C_P, p)
    b(surf, cx+4*p, hy+1*p, C_P, p); b(surf, cx+5*p, hy+1*p, C_P, p)

# ========== UI 绘制 ==========
def get_status():
    if time.time() - screen_start >= SCREEN_LIMIT:
        return "SLEEPY", C_SLP
    if saturation < 30:
        return "HUNGRY", C_HUN
    return "HAPPY", C_HAP

def draw_status(surf):
    txt, c = get_status()
    font = pygame.font.SysFont("simhei", 32)
    text = font.render(txt, True, c)
    rect = text.get_rect(center=(120*SCALE, 10*SCALE + 16))
    surf.blit(text, rect)

def draw_love(surf, v):
    font = pygame.font.SysFont("simhei", 28)
    txt = "LOVE " + str(v) + "/" + str(MAX_A)
    text = font.render(txt, True, C_W)
    rect = text.get_rect(center=(120*SCALE, 188*SCALE + 14))
    surf.blit(text, rect)

def draw_food_txt(surf, v):
    font = pygame.font.SysFont("simhei", 28)
    txt = "FOOD " + str(v) + "/" + str(MAX_S)
    text = font.render(txt, True, C_F)
    rect = text.get_rect(center=(120*SCALE, 215*SCALE + 14))
    surf.blit(text, rect)

def draw_flash(surf, v):
    font = pygame.font.SysFont("simhei", 32)
    txt = "FOOD +" + str(v)
    text = font.render(txt, True, C_F)
    rect = text.get_rect(center=(120*SCALE, 60*SCALE + 16))
    pygame.draw.rect(surf, C_B, rect.inflate(20, 10))
    surf.blit(text, rect)

def draw_menu(surf):
    surf.fill(C_B)
    font = pygame.font.SysFont("simhei", 36)
    text = font.render("FOOD MENU", True, C_W)
    rect = text.get_rect(center=(120*SCALE, 15*SCALE + 18))
    surf.blit(text, rect)

    font = pygame.font.SysFont("simhei", 32)
    for i in range(4):
        y = 55*SCALE + i * 40*SCALE
        txt = str(i+1) + ": +" + str(FOODS[i])
        text = font.render(txt, True, C_Y)
        rect = text.get_rect(center=(120*SCALE, y + 16))
        surf.blit(text, rect)

def draw_sleep(surf):
    surf.fill(C_B)
    font = pygame.font.SysFont("simhei", 40)
    text = font.render("SLEEPING", True, C_W)
    rect = text.get_rect(center=(120*SCALE, 100*SCALE + 20))
    surf.blit(text, rect)

    font = pygame.font.SysFont("simhei", 36)
    text = font.render("Zzz...", True, C_SLP)
    rect = text.get_rect(center=(120*SCALE, 130*SCALE + 18))
    surf.blit(text, rect)

# ========== 刷新与逻辑 ==========
def refresh():
    scene(screen)
    draw_pet(screen, 120*SCALE, 100*SCALE, 1.0)
    draw_status(screen)
    if flash_on: draw_flash(screen, flash_val)
    draw_love(screen, affection)
    draw_food_txt(screen, saturation)

def refresh_menu():
    draw_menu(screen)

def refresh_bars():
    draw_status(screen)
    draw_love(screen, affection)
    draw_food_txt(screen, saturation)

def check_decay():
    global affection, saturation, last_decay
    t = time.time()
    elapsed = t - last_decay
    if elapsed >= 3600:
        h = int(elapsed // 3600)
        affection = max(0, affection - A_DECAY * h)
        saturation = max(0, saturation - S_DECAY * h)
        last_decay = t - (elapsed % 3600)
        return True
    return False

def enter_sleep():
    global sleeping, tail_wagging, blinking
    sleeping = True
    tail_wagging = False
    blinking = False
    print("sleep")
    draw_sleep(screen)

def wake_up():
    global sleeping, screen_start
    sleeping = False
    screen_start = time.time()
    print("wake")
    refresh()

# ========== 主循环 ==========
def main():
    global affection, saturation, pet_today, last_pet_day, last_decay
    global menu_on, flash_on, flash_val, flash_t, sleeping
    global c_color, screen_start
    global tail_wagging, wag_count, wag_frame, wag_timer
    global blinking, blink_frame, blink_timer

    last_decay = time.time()
    screen_start = time.time()

    print("=" * 40)
    print("像素电子宠物 - PC版")
    print("=" * 40)
    print("按键说明：")
    print("  1 = 抚摸宠物(摇尾巴)")
    print("  2 = 打开/关闭菜单")
    print("  3 = 切换配色")
    print("  4 = 睡觉/唤醒")
    print("  ESC = 退出")
    print("=" * 40)

    refresh()
    pygame.display.flip()

    tick = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                key = None
                if event.key == pygame.K_1:
                    key = 1
                elif event.key == pygame.K_2:
                    key = 2
                elif event.key == pygame.K_3:
                    key = 3
                elif event.key == pygame.K_4:
                    key = 4
                elif event.key == pygame.K_ESCAPE:
                    running = False

                if key and not sleeping:
                    if tail_wagging and key != 1:
                        tail_wagging = False
                        wag_count, wag_frame, wag_timer = 0, 0, 0
                        refresh()

                    if key == 1:
                        if menu_on:
                            fv = FOODS[0]
                            old = saturation
                            saturation = min(saturation + fv, MAX_S)
                            print("eat 1 +", saturation-old)
                            menu_on = False
                            flash_on, flash_val, flash_t = True, fv, 0
                            refresh()
                        else:
                            tail_wagging = True
                            wag_count, wag_frame, wag_timer = 0, 0, 0
                            print("wag start")
                            current_day = time.localtime().tm_mday
                            if current_day != last_pet_day:
                                pet_today, last_pet_day = 0, current_day
                            rem = PET_LIMIT - pet_today
                            if rem > 0:
                                add = min(5, rem)
                                affection = min(affection + add, MAX_A)
                                pet_today += add
                                print("pet", affection, pet_today)
                            else:
                                print("no pet")
                            refresh()

                    elif key == 2:
                        if menu_on:
                            fv = FOODS[1]
                            old = saturation
                            saturation = min(saturation + fv, MAX_S)
                            print("eat 2 +", saturation-old)
                            menu_on = False
                            flash_on, flash_val, flash_t = True, fv, 0
                            refresh()
                        else:
                            menu_on = True
                            print("menu")
                            refresh_menu()

                    elif key == 3:
                        if menu_on:
                            fv = FOODS[2]
                            old = saturation
                            saturation = min(saturation + fv, MAX_S)
                            print("eat 3 +", saturation-old)
                            menu_on = False
                            flash_on, flash_val, flash_t = True, fv, 0
                            refresh()
                        else:
                            c_color = (c_color + 1) % len(SCHEMES)
                            print("color", SCHEMES[c_color][2])
                            refresh()

                    elif key == 4:
                        if menu_on:
                            fv = FOODS[3]
                            old = saturation
                            saturation = min(saturation + fv, MAX_S)
                            print("eat 4 +", saturation-old)
                            menu_on = False
                            flash_on, flash_val, flash_t = True, fv, 0
                            refresh()
                        else:
                            enter_sleep()

                elif key and sleeping:
                    wake_up()

        if sleeping:
            tick += 1
            if tick >= 200:
                tick = 0
                if check_decay():
                    print("sleep decay", affection, saturation)
            pygame.time.delay(50)
            continue

        # 尾巴动画
        if tail_wagging:
            wag_timer += 1
            if wag_timer >= WAG_SPEED:
                wag_timer = 0
                wag_frame = 1 - wag_frame
                if wag_frame == 0:
                    wag_count += 1
                    print("wag", wag_count)
                if wag_count >= WAG_MAX:
                    tail_wagging = False
                    wag_count, wag_frame, wag_timer = 0, 0, 0
                    print("wag end")
                if not menu_on and not flash_on:
                    if tail_wagging:
                        if wag_frame == 0:
                            draw_tail(screen, 120*SCALE, 100*SCALE, 1.0, -WAG_OFFSET)
                        else:
                            draw_tail(screen, 120*SCALE, 100*SCALE, 1.0, WAG_OFFSET)
                    else:
                        refresh()

        # 眨眼动画
        blink_timer += 1
        if not blinking:
            if blink_timer >= BLINK_INTERVAL:
                blink_timer = 0
                blinking = True
                blink_frame = 1
                print("blink")
                if not menu_on and not flash_on and not tail_wagging:
                    draw_eyes(screen, 120*SCALE, 100*SCALE, 1.0, closed=True)
        else:
            if blink_timer >= BLINK_DURATION:
                blink_timer = 0
                blinking = False
                blink_frame = 0
                print("blink end")
                if not menu_on and not flash_on and not tail_wagging:
                    draw_eyes(screen, 120*SCALE, 100*SCALE, 1.0, closed=False)

        # 喂食闪屏
        if flash_on:
            flash_t += 1
            if flash_t == 1:
                refresh()
            elif flash_t >= 2:
                flash_on, flash_t = False, 0
                refresh()

        # 衰减检测
        tick += 1
        if tick >= 200:
            tick = 0
            if not menu_on and not flash_on and not tail_wagging and not blinking and check_decay():
                print("decay", affection, saturation)
                refresh_bars()

        pygame.display.flip()
        clock.tick(20)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
