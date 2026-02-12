from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from typing import Dict, Iterable, List, Optional, Set, Tuple


GridPos = Tuple[int, int]


class PathfindingStrategy(ABC):
    """Strategy interface (abstraction)."""

    name: str = "BASE"

    @abstractmethod
    def find_path(
        self,
        start: GridPos,
        goal: GridPos,
        obstacles: Set[GridPos],
        cols: int,
        rows: int,
    ) -> Optional[List[GridPos]]:
        """Return a list of grid cells from start..goal (inclusive), or None if no path."""
        raise NotImplementedError

    def _neighbors(self, x: int, y: int, cols: int, rows: int, obstacles: Set[GridPos]) -> Iterable[GridPos]:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in obstacles:
                yield (nx, ny)

    def _reconstruct(self, parent: Dict[GridPos, Optional[GridPos]], goal: GridPos) -> List[GridPos]:
        cur: Optional[GridPos] = goal
        path: List[GridPos] = []
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path


class BFSStrategy(PathfindingStrategy):
    name = "BFS"

    def find_path(self, start, goal, obstacles, cols, rows):
        q = deque([start])
        parent: Dict[GridPos, Optional[GridPos]] = {start: None}

        while q:
            cur = q.popleft()
            if cur == goal:
                return self._reconstruct(parent, goal)

            x, y = cur
            for nb in self._neighbors(x, y, cols, rows, obstacles):
                if nb not in parent:
                    parent[nb] = cur
                    q.append(nb)

        return None


class DFSStrategy(PathfindingStrategy):
    name = "DFS"

    def find_path(self, start, goal, obstacles, cols, rows):
        stack = [start]
        parent: Dict[GridPos, Optional[GridPos]] = {start: None}

        while stack:
            cur = stack.pop()
            if cur == goal:
                return self._reconstruct(parent, goal)

            x, y = cur
            for nb in self._neighbors(x, y, cols, rows, obstacles):
                if nb not in parent:
                    parent[nb] = cur
                    stack.append(nb)

        return None
