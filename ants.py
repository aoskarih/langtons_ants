import pygame
import numpy as np
import time
import datetime
import random
import sys
import os

palette = { 0 : (0, 0, 0),
            1 : (126, 37, 83),
            2 : (0, 135, 81),
            3 : (171, 82, 54),
            4 : (95, 87, 79),
            5 : (194, 195, 199),
            6 : (255, 241, 232),
            7 : (255, 0, 77),
            8 : (255, 163, 0),
            9 : (255, 236, 39),
            10: (0, 228, 54),
            11: (41, 173, 255),
            12: (131, 118, 156),
            13: (255, 119, 168),
            14: (255, 204, 170),
            15 : (29, 43, 83)
            }

palette_values = [v for k, v in palette.items()]

screen_size = (512, 512)
fullscreen = True

turn = {"left"  : np.array([[0, -1], [1, 0]]),
        "right" : np.array([[0, 1], [-1, 0]]),
        "back"  : np.array([[-1, 0],[0, -1]]),
        "none"  : np.array([[1, 0],[0, 1]])}
directions = [k for k in turn]

"""
Fun cases:

one ant:
rblnbb
rlbrbr
rrlrrb
rllllrrl        !!
lrrrlllr        !
llrrrrll        !!
lrllllrr        
lrrrrrllr
llrrrlrlrllr    
rrlllrlllrrr    !!
rrlllrlllrrrlr
rrlllrlllrrrrr
rnbrnlllnn

two ants:
rrlllrlllrrrrr
rrlllrlllrrrrrl

rrlllrlllrrr  
    a = Ant(np.array([60, 0]), np.array([1, 0]), beh)
    b = Ant(np.array([-60, 0]), np.array([-1, 0]), beh)

    a = Ant(np.array([100, 0]), np.array([1, 0]), beh)
    b = Ant(np.array([-100, -50]), np.array([-1, 0]), beh)
    
    a = Ant(np.array([0, -7]), np.array([1, 0]), beh)
    b = Ant(np.array([9, 8]), np.array([1, 0]), beh)
    
    !!!
    a = Ant(np.array([-2, 9]), np.array([1, 0]), beh)
    b = Ant(np.array([-7, -7]), np.array([0, -1]), beh)
    
    fast grid
    a = Ant(np.array([2, 4]), np.array([1, 0]), beh)
    b = Ant(np.array([6, 7]), np.array([1, 0]), beh)

n ants:
lr
llrn
rbbbn
blbrln
llrbbll
rbnrllb
rblnnbbbrr
bnrnrnnnnl
bllbnnbnbblbbr
bbnbbrrlbbbnrr
lblrrbnbllrnrr
"""

color_n = 2
ant_n = 1
args = sys.argv[1:]
beh_s = ""
scale = 1
for arg in [a.split("=") for a in args]:
    if arg[0] == "beh":
        beh_s = arg[1]
    elif arg[0] == "color_n":
        color_n = int(arg[1])
    elif arg[0] == "ant_n":
        ant_n = int(arg[1])
    elif arg[0] == "scale":
        scale = int(arg[1])
    
if len(beh_s) > 0:
    color_n = len(beh_s)

center = [256, 256]
speed = 50
limits = [1, 5, 25, 100, 500, 0]
ants = []
surfs = {(0, 0) : pygame.Surface((128, 128))}
d = 128

pause = False
speed_lim = 0



beh = {}

class Key():
    
    def __init__(self, action, key):
        self.action = action
        self.key = key

keys = {0 : Key("pause", pygame.K_p),
        1 : Key("in", pygame.K_i),
        2 : Key("out", pygame.K_o),
        3 : Key("up", pygame.K_w),
        4 : Key("down", pygame.K_s),
        5 : Key("left", pygame.K_a),
        6 : Key("right", pygame.K_d),
        7 : Key("quit", pygame.K_ESCAPE),
        8 : Key("max speed", pygame.K_t),
        9 : Key("slow speed", pygame.K_g),
        10: Key("restart", pygame.K_r),
        11: Key("scroll up", pygame.K_q),
        12: Key("scroll down", pygame.K_e),
        13: Key("save", pygame.K_c)
        }

input_arr = [False for k in range(len(keys))]

class Cell:
    
    def __init__(self, r):
        self.r = (r[0], r[1])
    
    def __eq__(self, other):
        return other.r[0] == self.r[0] and other.r[1] == self.r[1] 
    
    def __hash__(self):
        return hash(self.r)

class Grid:
    grid = {}
    new_items = {}
    
    def change(self, r):
        c = Cell(r)
        self.grid[c] = (self.grid.get(c, 0) + 1) % (color_n)
        self.new_items[c] = self.grid[c]


class Ant:
    
    def __init__(self, r, v, beh):
        self.r = r
        self.v = v
        self.beh = beh
    
    def move(self, g):
        self.v = self.v @ turn[self.beh[g.grid.get(Cell(self.r), 0)]]
        g.change(self.r)
        self.r = self.r + self.v
    
    def to_str(self):
        return str(self.r) + " " + str(self.v)

def input():
    global input_arr
    input_arr = [False for k in range(len(keys))]
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            for i in range(len(keys)):
                if event.key == keys[i].key:
                    input_arr[i] = True

def update(g, cycle):

    screen = pygame.display.get_surface()
    update_rects = []
    
    global scale
    global center
    global pause
    global speed
    global d
    
    full_update = False
    draw_all = False
    if cycle % 10000 == 0:
        full_update = True
    
    for i in range(len(input_arr)):
        if input_arr[i]:
            if i == 0: pause = (pause == False)
            if i == 3: 
                center[1] += speed
                full_update = True
            if i == 4: 
                center[1] -= speed
                full_update = True
            if i == 5: 
                center[0] += speed
                full_update = True
            if i == 6: 
                center[0] -= speed
                full_update = True
            if i == 11:
                speed *= 2
            if i == 12:
                speed *= 0.5

    if pause: return 0
    
    
    for ant in ants:
        lt = (ant.r[0]*scale+center[0], ant.r[1]*scale+center[1])
        re = pygame.Rect(lt, (scale, scale))
        update_rects.append(re)
        ant.move(g)
    
    if full_update:
        background = pygame.Surface(screen.get_size()).convert()
        background.fill(palette[0])
        screen.blit(background, (0,0))
    

    for c, v in g.new_items.items():
        p = ((c.r[0]*scale)//d, (c.r[1]*scale)//d)  
        if p in surfs:
            s = surfs[p]
        else:
            s = pygame.Surface((d, d))
            surfs[p] = s
        lt = (c.r[0]*scale-d*p[0], c.r[1]*scale-d*p[1])
        if scale == 1:
            s.set_at(lt, palette[v])
        else:
            pygame.draw.rect(s, palette[v], pygame.Rect(lt, (scale, scale)))
    
    for r, s in surfs.items():
        screen.blit(s, (d*r[0]+center[0], d*r[1]+center[1]))
#    bl = [(s, (d*r[0]+center[0], d*r[1]+center[1])) for r, s in surfs.items()]
#    screen.blits(bl)

    g.new_items.clear()
    
    if full_update:        
        pygame.display.update()
    else:
        pygame.display.update(update_rects)
    
    return 1

def main():
    
    cycle = 0
    
    screen = pygame.display.get_surface()
    background = pygame.Surface(screen.get_size()).convert()
    background.fill(palette[0])
    screen.blit(background, (0,0))
    
    clock = pygame.time.Clock()
    global speed_lim
    s_i = 5
    
    if len(beh_s) > 0:
        for j, c in enumerate(beh_s):
            if c=="l":
                beh[j] = directions[0]
            elif c=="r":
                beh[j] = directions[1]
            elif c=="b":
                beh[j] = directions[2]
            elif c=="n":
                beh[j] = directions[3]
    else:
        for i in range(color_n):
            beh[i] = random.choice(directions)
    
    print([beh[k] for k in beh])

    for _ in range(ant_n):
        sr = [random.randint(-10, 10) for _ in range(2)]
        sv = random.choice([[0, -1],[-1, 0],[1, 0],[0, 1]])
        a = Ant(np.array(sr), np.array(sv), beh)
        ants.append(a)
        #print(a.to_str())
    """    
    a = Ant(np.array([-2, 9]), np.array([1, 0]), beh)
    b = Ant(np.array([-7, -7]), np.array([0, -1]), beh)
    ants.append(a)
    ants.append(b)
    """    
    g = Grid()
    
    cps = []
    t = time.clock()
    run = True
    
    while run:
        dt = time.clock() - t
        t += dt
        cps.append(dt)
        
        clock.tick(limits[s_i])
        
        input()        
        for i in range(len(input_arr)):
            if input_arr[i]:
                if i == 10: 
                    g.grid.clear()
                    surfs.clear()
                    return 1
                if i == 8 and s_i < 5: s_i += 1
                if i == 9 and s_i > 0: s_i += -1
                if i == 7: 
                    print("cycle:      " + str(cycle))
                    print("cycle/s:    " + str(int(cycle/time.clock())))
                    print("time spend: " + str(datetime.timedelta(seconds=int(time.clock()))))
                    return 0
                if i == 13:
                    file_name = beh_s + "_" + str(ant_n) + "_" + str(cycle) + ".png"
                    pygame.image.save(pygame.display.get_surface(), os.path.join("data", file_name))
                    print("saved: " + file_name)
        u = update(g, cycle)
        cycle += u
        
#        os.system("clear")
#        print("cycle:      " + str(i))
#        print("cycle/s:    " + str(int(1/(sum(cps)/10))))
#        print("time spend: " + str(datetime.timedelta(seconds=int(time.clock()))))

if __name__ == "__main__":    
    pygame.init()
    pygame.display.set_caption("Langton's Ant")
    if fullscreen:
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        pygame.display.set_mode(screen_size)
    
    while main():
        del ants[:]
    
    
