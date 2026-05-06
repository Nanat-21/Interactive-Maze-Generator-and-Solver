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

# Renderer
class Renderer:
    def __init__(self, screen, maze):
        self.screen = screen
        self.maze   = maze
        self.cs     = CELL_SIZE
        self.off_x  = 40   
        self.off_y  = 80   

    def cell_rect(self, r, c):
        R = self.maze.R
        x = self.off_x + c * self.cs
        y = self.off_y + (R - 1 - r) * self.cs
        return x, y, self.cs, self.cs

    def draw(self, mouse_rc=None, path=None, dead=None):
        maze = self.maze
        R, C = maze.R, maze.C
        cs   = self.cs
        scr  = self.screen

        # Cell fills
        for r in range(R):
            for c in range(C):
                x, y, w, h = self.cell_rect(r, c)
                col = BG
                if path and (r, c) in path: col = (80, 20, 20)
                if dead  and (r, c) in dead: col = (15, 35, 70)
                pygame.draw.rect(scr, col, (x, y, w, h))

        # Start / end highlights
        if maze.start:
            x, y, w, h = self.cell_rect(*maze.start)
            pygame.draw.rect(scr, (70, 50, 10), (x, y, w, h))
        if maze.end:
            x, y, w, h = self.cell_rect(*maze.end)
            pygame.draw.rect(scr, (70, 50, 10), (x, y, w, h))

        # Walls
        for r in range(R):
            for c in range(C):
                x, y, w, h = self.cell_rect(r, c)
                if maze.northWall[r][c]:
                    pygame.draw.line(scr, WALL_COL, (x, y + h), (x + w, y + h), WALL_WIDTH)
                if maze.northWall[r + 1][c]:
                    pygame.draw.line(scr, WALL_COL, (x, y), (x + w, y), WALL_WIDTH)
                if maze.eastWall[r][c]:
                    pygame.draw.line(scr, WALL_COL, (x, y), (x, y + h), WALL_WIDTH)
                if maze.eastWall[r][c + 1]:
                    pygame.draw.line(scr, WALL_COL, (x + w, y), (x + w, y + h), WALL_WIDTH)

        if mouse_rc and mouse_rc[0] >= 0:
            mr, mc = mouse_rc
            cx = self.off_x + mc * cs + cs // 2
            cy = self.off_y + (R - 1 - mr) * cs + cs // 2
            rad = max(3, cs // 4)
            pygame.draw.circle(scr, MOUSE_COL, (cx, cy), rad)

# Main application
def main():
    pygame.init()
    font      = pygame.font.SysFont('consolas', 14)
    font_big  = pygame.font.SysFont('consolas', 18, bold=True)

    maze       = None
    renderer   = None
    gen_iter   = None
    sol_iter   = None
    phase      = 'idle'         
    extra_mode = False
    speed_idx  = DEFAULT_SPEED_IDX
    mouse_rc   = None
    path_set   = set()
    dead_set   = set()
    status_msg = "Press G to generate a maze"
    last_step  = 0
    pct        = 0.0

    W = COLS * CELL_SIZE + 80
    H = ROWS * CELL_SIZE + 120
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Maze Generator & Solver")
    clock = pygame.time.Clock()

    def new_maze():
        nonlocal maze, renderer, gen_iter, sol_iter, phase
        nonlocal mouse_rc, path_set, dead_set, status_msg, pct
        maze      = Maze(ROWS, COLS)
        renderer  = Renderer(screen, maze)
        gen_iter  = generate_steps(maze, extra_walls=extra_mode)
        sol_iter  = None
        phase     = 'generating'
        mouse_rc  = None
        path_set  = set()
        dead_set  = set()
        status_msg = "Generating…"
        pct        = 0.0

    def draw_ui():
        screen.fill(BG)
        if renderer:
            renderer.draw(mouse_rc, path_set, dead_set)
        y_leg = H - 28
        items = [
            (MOUSE_COL, "mouse"),
            (PATH_COL,  "path"),
            (DEAD_COL,  "dead end"),
            (ENTRY_COL, "start/end"),
        ]
        lx = 40
        for col, label in items:
            pygame.draw.circle(screen, col, (lx + 6, y_leg + 7), 5)
            txt = font.render(label, True, DIM_COL)
            screen.blit(txt, (lx + 15, y_leg))
            lx += 90
        st = font.render(status_msg, True, TEXT_COL)
        screen.blit(st, (40, 14))
        spd_s = f"Speed: {speed_idx+1}/{len(SPEED_STEPS)}   Extra walls: {'ON' if extra_mode else 'OFF'}   [G]enerate [S]olve [R]eset [E]xtra [+/-]speed [ESC]quit"
        ht = font.render(spd_s, True, DIM_COL)
        screen.blit(ht, (40, 34))
        if phase == 'generating':
            bar_w = int((W - 80) * pct)
            pygame.draw.rect(screen, (40, 40, 50), (40, 56, W - 80, 8), border_radius=4)
            pygame.draw.rect(screen, MOUSE_COL,    (40, 56, bar_w,  8), border_radius=4)
        pygame.display.flip()

    running = True
    while running:
        clock.tick(FPS)
        now = time.time() * 1000  # ms

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_g:
                    new_maze()
                elif event.key == pygame.K_s:
                    if maze and maze.start and phase in ('idle', 'done'):
                        path_set.clear(); dead_set.clear()
                        sol_iter = solve_steps(maze)
                        phase = 'solving'
                        status_msg = "Solving…"
                        mouse_rc = None
                elif event.key == pygame.K_r:
                    if maze:
                        path_set.clear(); dead_set.clear()
                        mouse_rc = None
                        sol_iter = None
                        gen_iter = None
                        phase = 'idle'
                        status_msg = "Reset. Press S to solve or G to regenerate."
                elif event.key == pygame.K_e:
                    extra_mode = not extra_mode
                    status_msg = f"Extra-wall mode {'ON' if extra_mode else 'OFF'}. Press G to regenerate."
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    speed_idx = min(speed_idx + 1, len(SPEED_STEPS) - 1)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    speed_idx = max(speed_idx - 1, 0)

        # Animation step 
        delay = SPEED_STEPS[speed_idx]
        do_step = (now - last_step >= delay) if delay > 0 else True

        if do_step and phase == 'generating' and gen_iter:
            try:
                r, c, pct = next(gen_iter)
                if r < 0:  #
                    phase = 'done'
                    mouse_rc = None
                    status_msg = "Maze ready!  Press S to solve."
                else:
                    mouse_rc = (r, c)
                last_step = now
            except StopIteration:
                phase = 'done'
                mouse_rc = None
                status_msg = "Maze ready!  Press S to solve."

        if do_step and phase == 'solving' and sol_iter:
            try:
                mr, mc, ps, ds, done = next(sol_iter)
                path_set = set(ps)
                dead_set = set(ds)
                mouse_rc = (mr, mc) if mr >= 0 else None
                if done:
                    phase = 'done'
                    mouse_rc = None
                    status_msg = f"Solved!  Path: {len(path_set)} cells  |  Dead ends: {len(dead_set)}"
                last_step = now
            except StopIteration:
                phase = 'done'
                status_msg = "No path found."

        draw_ui()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()