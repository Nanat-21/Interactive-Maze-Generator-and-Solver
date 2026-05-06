import pygame
import random
import sys
import time

# Configuration
ROWS = 20
COLS = 30
CELL_SIZE = 28
WALL_WIDTH = 2
FPS = 60

# Colors
BG          = (18,  18,  22)
WALL_COL    = (220, 220, 225)
MOUSE_COL   = (34,  197,  94)   
PATH_COL    = (239,  68,  68)   
DEAD_COL    = (59,  130, 246)   
ENTRY_COL   = (245, 158,  11)   
TEXT_COL    = (200, 200, 210)
DIM_COL     = (100, 100, 115)

SPEED_STEPS = [200, 80, 30, 10, 3, 1, 0]   
DEFAULT_SPEED_IDX = 3

# Maze State
class Maze:
    def __init__(self, rows, cols):
        self.R = rows
        self.C = cols
        # northWall[r][c]: row 0 is phantom below the maze
        self.northWall = [[1] * cols for _ in range(rows + 1)]
        # eastWall[r][c]: col 0 is left edge; col C is right edge
        self.eastWall  = [[1] * (cols + 1) for _ in range(rows)]
        self.visited   = [[False] * cols for _ in range(rows)]
        self.start     = None   # (row, col)
        self.end       = None   # (row, col)

    def remove_north_wall(self, r, c):  self.northWall[r + 1][c] = 0
    def remove_south_wall(self, r, c):  self.northWall[r][c]     = 0
    def remove_east_wall(self, r, c):   self.eastWall[r][c + 1]  = 0
    def remove_west_wall(self, r, c):   self.eastWall[r][c]      = 0

    def can_go(self, r, c, direction):
        if direction == 'N': return r < self.R - 1 and self.northWall[r + 1][c] == 0
        if direction == 'S': return r > 0           and self.northWall[r][c]     == 0
        if direction == 'E': return c < self.C - 1  and self.eastWall[r][c + 1]  == 0
        if direction == 'W': return c > 0           and self.eastWall[r][c]      == 0
        return False

    def choose_start_end(self):
        sr = random.randint(0, self.R - 1)
        er = random.randint(0, self.R - 1)
        self.eastWall[sr][0] = 0      
        self.eastWall[er][self.C] = 0 
        self.start = (sr, 0)
        self.end   = (er, self.C - 1)
