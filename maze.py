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

# Generator (stack-based DFS "mouse")
def generate_steps(maze, extra_walls=False):
    R, C = maze.R, maze.C
    sr, sc = random.randint(0, R - 1), random.randint(0, C - 1)
    maze.visited[sr][sc] = True
    stack = [(sr, sc)]
    total = R * C
    visited_count = 1

    DIRS = [('N',  1, 0), ('S', -1, 0), ('E', 0,  1), ('W', 0, -1)]

    while stack:
        r, c = stack[-1]
        neighbours = []
        for d, dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and not maze.visited[nr][nc]:
                neighbours.append((d, nr, nc))

        if not neighbours:
            stack.pop()
        else:
            random.shuffle(neighbours)
            d, nr, nc = neighbours[0]
            if   d == 'N': maze.remove_north_wall(r, c)
            elif d == 'S': maze.remove_south_wall(r, c)
            elif d == 'E': maze.remove_east_wall(r, c)
            elif d == 'W': maze.remove_west_wall(r, c)
            maze.visited[nr][nc] = True
            visited_count += 1
            stack.append((nr, nc))
            yield (r, c, visited_count / total)

    if extra_walls:
        n_extra = max(1, (R * C) // 20)
        for _ in range(n_extra):
            r  = random.randint(0, R - 1)
            c  = random.randint(0, C - 1)
            dr, dc, d = random.choice([(1,0,'N'),(-1,0,'S'),(0,1,'E'),(0,-1,'W')])
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                if   d == 'N': maze.remove_north_wall(r, c)
                elif d == 'S': maze.remove_south_wall(r, c)
                elif d == 'E': maze.remove_east_wall(r, c)
                elif d == 'W': maze.remove_west_wall(r, c)

    maze.choose_start_end()
    yield (-1, -1, 1.0)   

# Solver (backtracking mouse)
def solve_steps(maze):
    sr, sc = maze.start
    er, ec = maze.end
    stack  = [(sr, sc)]
    path   = {(sr, sc)}
    dead   = set()

    DIRS = [('N',  1, 0), ('S', -1, 0), ('E', 0,  1), ('W', 0, -1)]

    while stack:
        r, c = stack[-1]
        if (r, c) == (er, ec):
            yield (r, c, frozenset(path), frozenset(dead), True)
            return

        moves = []
        for d, dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if maze.can_go(r, c, d) and (nr, nc) not in dead and (nr, nc) not in path:
                moves.append((nr, nc))

        if not moves:
            dead.add((r, c))
            path.discard((r, c))
            stack.pop()
        else:
            random.shuffle(moves)
            nr, nc = moves[0]
            path.add((nr, nc))
            stack.append((nr, nc))

        yield (r, c, frozenset(path), frozenset(dead), False)

    yield (-1, -1, frozenset(path), frozenset(dead), False)
