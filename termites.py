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

screen_size = (1080, 720)
fullscreen = False

turn = {0 : np.array([[0, -1], [1, 0]]),
        1 : np.array([[0, 1], [-1, 0]]),
        2 : np.array([[-1, 0],[0, -1]]),
        3 : np.array([[1, 0],[0, 1]])}
"""
0 = left
1 = right
2 = back
3 = neutral
"""

"""
Fun cases:

one termite
state, color

2, 2
[[[0, 3, 1], [0, 2, 1]], [[1, 1, 0], [1, 0, 1]]]
[[[0, 1, 1], [1, 1, 1]], [[1, 3, 0], [0, 2, 1]]]

2, 3
[[[1, 1, 1], [1, 2, 0], [0, 2, 0]], [[2, 0, 1], [0, 0, 0], [0, 1, 1]]]


"""

color_n = 2
state_n = 2
ant_n = 1
args = sys.argv[1:]
beh_s = ""
scale = 1
for arg in [a.split("=") for a in args]:
    if arg[0] == "color_n":
        color_n = int(arg[1])
    elif arg[0] == "state_n":
        state_n = int(arg[1])
    elif arg[0] == "ant_n":
        ant_n = int(arg[1])
    elif arg[0] == "scale":
        scale = int(arg[1])
    elif arg[0] == "f":
        fullscreen = int(arg[1])
    
if len(beh_s) > 0:
    color_n = len(beh_s)

center = [0, 0]
speed = 50
limits = [1, 5, 25, 100, 500, 0]
ants = []
surfs = {(0, 0) : pygame.Surface((128, 128))}
d = 128

pause = False
speed_lim = 0



beh = [[[0,0,0] for _ in range(color_n)] for _ in range(state_n)]

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
    
    def change(self, r, nc):
        c = Cell(r)
        self.grid[c] = nc
        self.new_items[c] = self.grid[c]


class Ant:
    
    def __init__(self, r, v, beh):
        self.r = r
        self.v = v
        self.state = 0
        self.beh = beh
    
    def move(self, g):
        color = g.grid.get(Cell(self.r), 0)
        self.v = self.v @ turn[self.beh[self.state][color][1]]
        g.change(self.r, self.beh[self.state][color][0])
        self.r = self.r + self.v
        self.state = self.beh[self.state][color][2]
    
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

def main(g):
    
    cycle = 0
    
    global beh
    
    screen = pygame.display.get_surface()
    background = pygame.Surface(screen.get_size()).convert()
    background.fill(palette[0])
    screen.blit(background, (0,0))
    
    clock = pygame.time.Clock()
    global speed_lim
    s_i = 3
    
    if len(beh_s) > 0: pass
    else:
        for i in range(color_n):
            for j in range(state_n):
                write_color = random.randint(0, color_n-1)
                turn = random.randint(0, 3)
                next_state = random.randint(0, state_n-1)
                beh[j][i] = [write_color, turn, next_state]
    
    beh = [[[1,0,1],[1,0,1]],[[1,1,1],[0,3,0]]]
    
    print(beh)
    
    for _ in range(ant_n):
        sr = [random.randint(-10, 10) for _ in range(2)]
        sv = random.choice([[0, -1],[-1, 0],[1, 0],[0, 1]])
        a = Ant(np.array(sr), np.array(sv), beh)
        ants.append(a)
        #print(a.to_str())
    
    t = time.clock()
    run = True
    
    while run:
        
        clock.tick(limits[s_i])
        
        input()        
        for i in range(len(input_arr)):
            if input_arr[i]:
                if i == 10: 
                    g.grid.clear()
                    surfs.clear()
                    print("cycle:      " + str(cycle))
                    print("cycle/s:    " + str(int(cycle/(time.clock()-t))))
                    print("time spend: " + str(datetime.timedelta(seconds=int(time.clock()-t))))
                    print()
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


if __name__ == "__main__":    
    pygame.init()
    pygame.display.set_caption("Langton's Ant")
    if fullscreen:
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        pygame.display.set_mode(screen_size)
    
    center = np.array(pygame.display.get_surface().get_size())/2
    g = Grid()
    
    while main(g):
        del ants[:]
    
    
    
    
