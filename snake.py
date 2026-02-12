import pygame

from dataclasses import dataclass
from direction import Direction
from pathfinding import PathfindingStrategy, BFSStrategy


@dataclass
class Segment:
    x: int
    y: int


class Snake:
    def __init__(self, cell: int = 40, pathfinder: PathfindingStrategy | None = None) -> None:
        self.cell = cell
        self.direction = Direction.RIGHT
        self.segments = [
            Segment(40, 120),
            Segment(80, 120),
            Segment(120, 120),
        ]  # last element is head

        # Strategy (DIP): depend on abstraction, not concrete algorithm
        self.pathfinder: PathfindingStrategy = pathfinder if pathfinder else BFSStrategy()

    @property
    def head(self):
        return self.segments[-1]

    @head.setter
    def head(self, segment):
        self.segments[-1] = segment

    def draw(self, screen):
        for segment in self.segments:
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (segment.x, segment.y, self.cell, self.cell),
            )

    def set_pathfinding_strategy(self, strategy: PathfindingStrategy):
        self.pathfinder = strategy

    # --------- Player input: block 180 reversal ---------
    def try_set_direction(self, new_dir: Direction):
        if self._is_reverse(new_dir):
            return
        self.direction = new_dir

    def _is_reverse(self, new_dir):
        return (
            (self.direction == Direction.UP and new_dir == Direction.DOWN)
            or (self.direction == Direction.DOWN and new_dir == Direction.UP)
            or (self.direction == Direction.LEFT and new_dir == Direction.RIGHT)
            or (self.direction == Direction.RIGHT and new_dir == Direction.LEFT)
        )

    def set_direction_autopilot(self, food, width, height):
        cell = self.cell
        head = (self.head.x // cell, self.head.y // cell)
        goal = (food.x // cell, food.y // cell)

        cols = width // cell
        rows = height // cell

        body = [(s.x // cell, s.y // cell) for s in self.segments]

        # obstacles: body except head; allow tail cell to reduce dead-ends
        obstacles = set(body[:-1])
        if len(body) >= 2:
            obstacles.discard(body[0])

        path = self.pathfinder.find_path(head, goal, obstacles, cols, rows)
        if not path or len(path) < 2:
            # No path found; do nothing (snake continues current direction)
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

    # --------- Movement + collisions ---------
    def update(self, food, width, height):
        prev_positions = [(s.x, s.y) for s in self.segments]

        # Move body first (each segment takes the position of the next segment)
        for i in range(len(self.segments) - 1):
            self.segments[i].x, self.segments[i].y = prev_positions[i + 1]

        # Then move head
        if self.direction == Direction.RIGHT:
            self.head.x += self.cell
        elif self.direction == Direction.LEFT:
            self.head.x -= self.cell
        elif self.direction == Direction.UP:
            self.head.y -= self.cell
        elif self.direction == Direction.DOWN:
            self.head.y += self.cell

        # Wall collision
        if (
            self.head.x < 0
            or self.head.x >= width
            or self.head.y < 0
            or self.head.y >= height
        ):
            raise Exception("Game Over!")

        # Self collision
        if any(seg.x == self.head.x and seg.y == self.head.y for seg in self.segments[:-1]):
            raise Exception("Game Over!")

        # Food collision
        if self.head.x == food.x and self.head.y == food.y:
            tail_x, tail_y = prev_positions[0]
            self.segments.insert(0, Segment(tail_x, tail_y))

            food.respawn(self.segments)
            return True

        return False

