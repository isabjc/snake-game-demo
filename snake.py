from dataclasses import dataclass
from collections import deque
from direction import Direction
import pygame


@dataclass
class Segment:
    x: int
    y: int


class Snake:
    def __init__(self, cell: int = 40) -> None:
        self.cell = cell
        self.direction = Direction.RIGHT
        self.segments = [
            Segment(40, 120),
            Segment(80, 120),
            Segment(120, 120),
        ]  # last element is the head

    def draw(self, screen):
        for segment in self.segments:
            pygame.draw.rect(
                screen, (255, 255, 255), (segment.x, segment.y, self.cell, self.cell)
            )

    def get_head(self):
        return self.segments[-1]

    def set_head(self, segment):
        self.segments[-1] = segment

    head = property(get_head, set_head)

    # ---------------- AUTOPILOT (BFS) ----------------
    def set_direction_autopilot(self, food, width, height, cell):
        head = (self.head.x // cell, self.head.y // cell)
        goal = (food.x // cell, food.y // cell)

        cols = width // cell
        rows = height // cell

        body = [(s.x // cell, s.y // cell) for s in self.segments]

        # Obstacles: body except head; allow tail cell (it moves away) to reduce dead-ends
        obstacles = set(body[:-1])
        if len(body) >= 2:
            obstacles.discard(body[0])  # allow tail

        path = self._bfs_path(head, goal, obstacles, cols, rows)
        if not path or len(path) < 2:
            self.direction = self._safe_fallback_direction(obstacles, cols, rows, cell)
            return

        nxt = path[1]
        dx = nxt[0] - head[0]
        dy = nxt[1] - head[1]

        desired = None
        if dx == 1:
            desired = Direction.RIGHT
        elif dx == -1:
            desired = Direction.LEFT
        elif dy == 1:
            desired = Direction.DOWN
        elif dy == -1:
            desired = Direction.UP

        if desired is not None and not self._is_reverse(desired):
            self.direction = desired

    def _bfs_path(self, start, goal, obstacles, cols, rows):
        q = deque([start])
        parent = {start: None}

        def neighbors(xy):
            x, y = xy
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in obstacles:
                    yield (nx, ny)

        while q:
            cur = q.popleft()
            if cur == goal:
                # Reconstruct path
                path = []
                while cur is not None:
                    path.append(cur)
                    cur = parent[cur]
                path.reverse()
                return path

            for nb in neighbors(cur):
                if nb not in parent:
                    parent[nb] = cur
                    q.append(nb)

        return None

    def _is_reverse(self, new_dir):
        return (
            (self.direction == Direction.UP and new_dir == Direction.DOWN)
            or (self.direction == Direction.DOWN and new_dir == Direction.UP)
            or (self.direction == Direction.LEFT and new_dir == Direction.RIGHT)
            or (self.direction == Direction.RIGHT and new_dir == Direction.LEFT)
        )

    def _safe_fallback_direction(self, obstacles, cols, rows, cell):
        hx = self.head.x // cell
        hy = self.head.y // cell

        options = [
            (Direction.UP, (hx, hy - 1)),
            (Direction.DOWN, (hx, hy + 1)),
            (Direction.LEFT, (hx - 1, hy)),
            (Direction.RIGHT, (hx + 1, hy)),
        ]

        for d, (nx, ny) in options:
            if self._is_reverse(d):
                continue
            if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in obstacles:
                return d

        return self.direction
    
    def try_set_direction(self, new_dir):
    # Ignore 180 reversals, so the head doesn't collide with the next segment if the player quickly taps opposite direction
        if (
            (self.direction == Direction.UP and new_dir == Direction.DOWN)
            or (self.direction == Direction.DOWN and new_dir == Direction.UP)
            or (self.direction == Direction.LEFT and new_dir == Direction.RIGHT)
            or (self.direction == Direction.RIGHT and new_dir == Direction.LEFT)
        ):
            return
        self.direction = new_dir


    # ---------------- GAME UPDATE ----------------
    def update(self, food, width, height):
        # Save old positions (prevents dataclass value-equality self-collision bugs)
        prev_positions = [(s.x, s.y) for s in self.segments]

        # Move head
        if self.direction == Direction.RIGHT:
            self.head.x += self.cell
        elif self.direction == Direction.LEFT:
            self.head.x -= self.cell
        elif self.direction == Direction.UP:
            self.head.y -= self.cell
        elif self.direction == Direction.DOWN:
            self.head.y += self.cell

        # Move body forward using previous positions
        for i in range(len(self.segments) - 1):
            self.segments[i].x, self.segments[i].y = prev_positions[i + 1]

        # Wall collision
        if (
            self.head.x < 0
            or self.head.x >= width
            or self.head.y < 0
            or self.head.y >= height
        ):
            raise Exception("Game Over!")

        # Self collision (compare coordinates explicitly)
        if any(
            seg.x == self.head.x and seg.y == self.head.y for seg in self.segments[:-1]
        ):
            raise Exception("Game Over!")

        # Food collision
        if self.head.x == food.x and self.head.y == food.y:
            # Grow: add a new segment at the old tail position so growth looks smooth
            tail_x, tail_y = prev_positions[0]
            self.segments.insert(0, Segment(tail_x, tail_y))

            food.respawn(self.segments)
            return True

        return False
