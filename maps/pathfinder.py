# maps/pathfinder.py

from collections import deque
import config


class Pathfinder:
    def __init__(self, grid_map):
        self.grid_map = grid_map

    def is_walkable(self, row, col):
        tile = self.grid_map.get_tile_at(row, col)
        return tile in (config.PATH, config.SPAWN, config.BASE)

    def get_neighbors(self, row, col):
        directions = [
            (-1, 0),  # up
            (1, 0),   # down
            (0, -1),  # left
            (0, 1),   # right
        ]

        neighbors = []
        for dr, dc in directions:
            nr = row + dr
            nc = col + dc

            if 0 <= nr < self.grid_map.rows and 0 <= nc < self.grid_map.cols:
                if self.is_walkable(nr, nc):
                    neighbors.append((nr, nc))

        return neighbors

    def find_path(self, start_cell, goal_cell):
        if start_cell is None or goal_cell is None:
            return []

        queue = deque([start_cell])
        visited = {start_cell}
        parent = {start_cell: None}

        while queue:
            current = queue.popleft()

            if current == goal_cell:
                break

            for neighbor in self.get_neighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        if goal_cell not in parent:
            return []

        path = []
        current = goal_cell
        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()
        return path