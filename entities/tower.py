# entities/tower.py

import os
import json
import math
import pygame
import config
from utils.sprite_utils import load_image, slice_sheet_horizontal, slice_sheet_grid


class Tower:
    def __init__(self, row, col, tower_type="basic"):
        self.row = row
        self.col = col
        self.type = tower_type

        with open("data/towers/tower_stats.json", "r", encoding="utf-8") as f:
            stats = json.load(f)[tower_type]

        self.range = stats["range"]
        self.damage = stats["damage"]
        self.fire_rate = stats["fire_rate"]
        self.color = tuple(stats["color"])

        self.slow_factor = stats.get("slow_factor", None)
        self.slow_duration = stats.get("slow_duration", None)
        self.max_targets = stats.get("max_targets", 1)

        self.level = 1
        self.cooldown = 0

        self.last_angle = 0
        self.current_target = None

        # Asset fields
        self.base_frames = None
        self.weapon_image = None
        self.projectile_image = None

        self.load_assets()

    def load_assets(self):
        """
        ตอนนี้ implement asset จริงให้ basic tower ก่อน
        tower type อื่น fallback เป็นวงกลมไปก่อน
        """
        if self.type != "basic":
            return

        base_path = "assets/images/towers/basic/base_sheet.png"
        weapon_path = "assets/images/towers/basic/weapon_sheet.png"
        projectile_path = "assets/images/towers/basic/projectile_sheet.png"

        # Base: ใช้ 2 เฟรม ซ้าย=lv1 ขวา=lv2
        try:
            self.base_frames = slice_sheet_horizontal(base_path, frame_count=2, scale=(32, 64))
        except Exception:
            self.base_frames = None

        # Weapon: ตอนนี้ใช้เฟรมแรกของ sheet ก่อน
        try:
            weapon_frames = slice_sheet_grid(weapon_path, columns=6, rows=1, scale=(64, 64))
            self.weapon_image = weapon_frames[0] if weapon_frames else None
        except Exception:
            self.weapon_image = None

        # Projectile: ตอนนี้ใช้เฟรมแรกของ sheet ก่อน
        try:
            projectile_frames = slice_sheet_grid(projectile_path, columns=3, rows=1, scale=(18, 18))
            self.projectile_image = projectile_frames[0] if projectile_frames else None
        except Exception:
            self.projectile_image = None

    def get_center(self):
        x = config.MAP_X + self.col * config.TILE_SIZE + config.TILE_SIZE // 2
        y = config.MAP_Y + self.row * config.TILE_SIZE + config.TILE_SIZE // 2
        return x, y

    def get_targets(self, enemies):
        cx, cy = self.get_center()

        targets = []
        for enemy in enemies:
            if enemy.is_dead:
                continue

            dx = enemy.x - cx
            dy = enemy.y - cy
            dist = math.hypot(dx, dy)

            if dist <= self.range:
                targets.append((dist, enemy))

        targets.sort(key=lambda item: item[0])
        return [enemy for _, enemy in targets[:self.max_targets]]

    def update(self, dt, enemies, projectiles):
        self.cooldown -= dt

        targets = self.get_targets(enemies)
        self.current_target = targets[0] if targets else None

        if self.current_target is not None:
            cx, cy = self.get_center()
            dx = self.current_target.x - cx
            dy = self.current_target.y - cy

            # pygame rotate ใช้มุมทวน/ตามแกนภาพ เลยต้องปรับนิด
            self.last_angle = -math.degrees(math.atan2(dy, dx)) - 90

        if self.cooldown <= 0:
            if targets:
                for target in targets:
                    self.shoot(target, projectiles)

                self.cooldown = 1 / self.fire_rate

    def shoot(self, target, projectiles):
        cx, cy = self.get_center()

        from entities.projectile import Projectile

        projectile = Projectile(
            cx,
            cy,
            target,
            damage=self.damage,
            image=self.projectile_image,
            color=self.color
        )

        projectile.slow_factor = self.slow_factor
        projectile.slow_duration = self.slow_duration

        projectiles.append(projectile)

    def upgrade(self):
        if self.level == 1:
            self.level = 2
            self.damage *= 1.5
            self.range *= 1.2
            self.fire_rate *= 1.2

    def get_sell_value(self):
        return 70

    def draw_base(self, screen):
        x, y = self.get_center()

        if self.base_frames:
            index = 0 if self.level == 1 else 1
            frame = self.base_frames[index]
            rect = frame.get_rect(center=(x, y))
            screen.blit(frame, rect)
        else:
            pygame.draw.circle(screen, self.color, (x, y), 16)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 16, 2)

    def draw_weapon(self, screen):
        if self.weapon_image is None:
            return

        x, y = self.get_center()

        rotated = pygame.transform.rotate(self.weapon_image, self.last_angle)
        rect = rotated.get_rect(center=(x, y - 4))
        screen.blit(rotated, rect)

    def draw_level_text(self, screen):
        x, y = self.get_center()
        font = pygame.font.SysFont("arial", 14, bold=True)
        text = font.render(str(self.level), True, (255, 255, 255))
        screen.blit(text, (x - 4, y + 10))

    def draw(self, screen):
        self.draw_base(screen)

        # ถ้าไม่มี weapon image และไม่ใช่ basic tower ให้ fallback เป็นวงกลมเดิม
        if self.weapon_image is None and self.base_frames is None:
            x, y = self.get_center()
            pygame.draw.circle(screen, self.color, (x, y), 16)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 16, 2)

        self.draw_weapon(screen)
        self.draw_level_text(screen)

    def draw_range(self, screen):
        x, y = self.get_center()
        pygame.draw.circle(screen, self.color, (x, y), int(self.range), 1)