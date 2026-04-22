# entities/base.py

import os
import pygame
import config


class Base:
    def __init__(self, row, col, max_hp=100):
        self.row = row
        self.col = col
        self.max_hp = max_hp
        self.current_hp = max_hp

        self.image = None
        self.load_assets()

    def load_assets(self):
        image_path = "assets/images/base/base.png"

        if os.path.exists(image_path):
            img = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(
                img,
                (config.TILE_SIZE, config.TILE_SIZE)
            )

    def take_damage(self, amount):
        
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0

    def is_destroyed(self):
        return self.current_hp <= 0

    def get_pixel_pos(self):
        x = config.MAP_X + self.col * config.TILE_SIZE
        y = config.MAP_Y + self.row * config.TILE_SIZE
        return x, y

    def draw_hp_bar(self, screen):
        x, y = self.get_pixel_pos()

        bar_width = config.TILE_SIZE
        bar_height = 6
        bar_x = x
        bar_y = y - 10

        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        hp_ratio = self.current_hp / self.max_hp if self.max_hp > 0 else 0
        fill_width = int(bar_width * hp_ratio)

        pygame.draw.rect(screen, (80, 220, 120), (bar_x, bar_y, fill_width, bar_height))

    def draw(self, screen, tile_size):
        x, y = self.get_pixel_pos()

        if self.image is not None:
            screen.blit(self.image, (x, y))
        else:
            pygame.draw.rect(screen, (180, 60, 60), (x, y, tile_size, tile_size))
            pygame.draw.rect(screen, (255, 255, 255), (x, y, tile_size, tile_size), 2)

        self.draw_hp_bar(screen)