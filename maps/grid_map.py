# maps/grid_map.py

import os
import pygame
import config
from maps.map_loader import load_map_json


class GridMap:
    def __init__(self, map_json_path):
        self.map_json_path = map_json_path
        self.map_data = load_map_json(map_json_path)

        if self.map_data is None:
            raise FileNotFoundError(f"Map JSON not found: {map_json_path}")

        self.map_name = self.map_data["map_name"]
        self.cols = self.map_data["cols"]
        self.rows = self.map_data["rows"]
        self.tile_size = self.map_data["tile_size"]
        self.image_path = self.map_data["image_path"]
        self.grid = self.map_data["grid"]

        self.background_image = self.load_background_image(self.image_path)

    def load_background_image(self, image_path):
        if not os.path.exists(image_path):
            surface = pygame.Surface((config.MAP_WIDTH, config.MAP_HEIGHT))
            surface.fill(config.MAP_BG_COLOR)
            return surface

        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (config.MAP_WIDTH, config.MAP_HEIGHT))
        return image

    def get_tile_name(self, tile_id):
        names = {
            config.EMPTY: "EMPTY",
            config.PATH: "PATH",
            config.BUILDABLE: "BUILDABLE",
            config.SPAWN: "SPAWN",
            config.BASE: "BASE",
            config.BLOCKED: "BLOCKED",
        }
        return names.get(tile_id, "UNKNOWN")

    def get_tile_at(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def get_cells_by_type(self, tile_type):
        cells = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == tile_type:
                    cells.append((row, col))
        return cells

    def get_first_cell_by_type(self, tile_type):
        cells = self.get_cells_by_type(tile_type)
        return cells[0] if cells else None

    def cell_to_pixel(self, row, col):
        x = config.MAP_X + col * self.tile_size
        y = config.MAP_Y + row * self.tile_size
        return x, y

    def pixel_to_cell(self, x, y):
        if not (config.MAP_X <= x < config.MAP_X + config.MAP_WIDTH):
            return None
        if not (config.MAP_Y <= y < config.MAP_Y + config.MAP_HEIGHT):
            return None

        col = (x - config.MAP_X) // self.tile_size
        row = (y - config.MAP_Y) // self.tile_size

        if 0 <= row < self.rows and 0 <= col < self.cols:
            return row, col
        return None

    def draw_background(self, screen):
        screen.blit(self.background_image, (config.MAP_X, config.MAP_Y))

    def draw_grid(self, screen, line_color=config.GRID_COLOR):
        for row in range(self.rows):
            for col in range(self.cols):
                x, y = self.cell_to_pixel(row, col)
                pygame.draw.rect(
                    screen,
                    line_color,
                    (x, y, self.tile_size, self.tile_size),
                    1
                )

    def draw_debug_overlay(self, screen):
        debug_colors = {
            config.EMPTY: (0, 0, 0, 0),
            config.PATH: (255, 215, 0, 75),
            config.BUILDABLE: (0, 200, 255, 75),
            config.SPAWN: (0, 255, 100, 115),
            config.BASE: (255, 80, 80, 115),
            config.BLOCKED: (120, 120, 120, 115),
        }

        for row in range(self.rows):
            for col in range(self.cols):
                tile_type = self.grid[row][col]
                color = debug_colors[tile_type]

                if tile_type != config.EMPTY:
                    x, y = self.cell_to_pixel(row, col)
                    overlay = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    overlay.fill(color)
                    screen.blit(overlay, (x, y))

    def draw_cell_labels(self, screen, font):
        for row in range(self.rows):
            for col in range(self.cols):
                x, y = self.cell_to_pixel(row, col)
                label_surface = font.render(f"{row},{col}", True, (175, 180, 185))
                screen.blit(label_surface, (x + 4, y + 4))