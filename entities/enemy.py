import pygame
import math
import random
import config
from core.asset_loader import AssetLoader


class Enemy:
    def __init__(self, path, enemy_type, stats):
        self.path = path
        self.type = enemy_type

        self.max_hp = stats["hp"]
        self.current_hp = self.max_hp

        self.base_speed = stats["speed"]
        self.color = tuple(stats["color"])

        self.reward = stats.get("reward", 0)
        self.reward_given = False

        self.slow_timer = 0
        self.slow_factor = 1.0

        self.current_index = 0
        self.reached_goal = False

        self.lane_offset = random.randint(-10, 10)

        self.x, self.y = self.get_spawn_position()

        self.is_dead = False
        self.death_started = False
        self.death_finished = False

        self.state = "walk"

        # animation frames
        self.walk_frames = []
        self.death_frames = []
        self.attack_frames = []

        self.anim_index = 0
        self.anim_timer = 0.0

        # หันซ้าย/ขวาเท่านั้น
        self.facing_right = True
        self.last_move_dir_x = 1

        # animation speed
        self.walk_anim_speed = 0.10
        self.attack_anim_speed = 0.08
        self.death_anim_speed = 0.05

        animations = stats.get("animations", {})

        if "walk" in animations:
            self.walk_frames = AssetLoader.load_animation(animations["walk"])

        if "death" in animations:
            self.death_frames = AssetLoader.load_animation(animations["death"])

        if "attack" in animations:
            self.attack_frames = AssetLoader.load_animation(animations["attack"])

    def get_pixel_center(self, cell):
        row, col = cell
        x = config.MAP_X + col * config.TILE_SIZE + config.TILE_SIZE // 2
        y = config.MAP_Y + row * config.TILE_SIZE + config.TILE_SIZE // 2
        return float(x), float(y)

    def get_spawn_position(self):
        x, y = self.get_pixel_center(self.path[0])

        # ถ้ามี path อย่างน้อย 2 จุด ให้ขยับจาก spawn ไปตามทิศทางเล็กน้อย
        if len(self.path) >= 2:
            next_x, next_y = self.get_pixel_center(self.path[1])

            dx = next_x - x
            dy = next_y - y
            dist = math.hypot(dx, dy)

            if dist > 0:
                dir_x = dx / dist
                dir_y = dy / dist

                # ขยับออกจากจุด spawn เล็กน้อย เพื่อลดการกองกันตอนเกิด
                spawn_offset = random.randint(6,12)
                x -= dir_x * spawn_offset
                y -= dir_y * spawn_offset

        return x, y
    def get_current_frames(self):
        if self.state == "death":
            return self.death_frames
        elif self.state == "attack":
            return self.attack_frames if self.attack_frames else self.walk_frames
        return self.walk_frames

    def set_state(self, new_state):
        if self.state == new_state:
            return
        self.state = new_state
        self.anim_index = 0
        self.anim_timer = 0.0

    def update_animation(self, dt):
        frames = self.get_current_frames()
        if not frames:
            return

        if self.state == "death":
            speed = self.death_anim_speed
        elif self.state == "attack":
            speed = self.attack_anim_speed
        else:
            speed = self.walk_anim_speed

        if self.state == "death":
            if self.death_finished:
                return

            self.anim_timer += dt
            if self.anim_timer >= speed:
                self.anim_timer = 0
                self.anim_index += 1

                if self.anim_index >= len(frames):
                    self.anim_index = len(frames) - 1
                    self.death_finished = True
            return

        self.anim_timer += dt
        if self.anim_timer >= speed:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(frames)

    def update(self, dt):
        if self.is_dead:
            self.set_state("death")
            self.update_animation(dt)
            return

        if self.reached_goal:
            self.set_state("attack")
            self.update_animation(dt)
            return

        self.set_state("walk")
        self.update_animation(dt)

        # movement
        if self.current_index >= len(self.path) - 2:
            self.reached_goal = True
            return

        row, col = self.path[self.current_index]
        next_row, next_col = self.path[self.current_index + 1]

        target_x = config.MAP_X + next_col * config.TILE_SIZE + config.TILE_SIZE // 2
        target_y = config.MAP_Y + next_row * config.TILE_SIZE + config.TILE_SIZE // 2

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < 6:
            self.x = target_x
            self.y = target_y
            self.current_index += 1
            return

        dir_x = dx / dist
        dir_y = dy / dist

        # หันซ้าย/ขวาเท่านั้น
        # หันซ้าย/ขวาเฉพาะตอนเดินแนวนอนชัดเจน
        # กัน fast enemy สะบัดหน้ากลับไปมาเวลาถึงจุดเลี้ยว
        if abs(dir_x) > 0.25:
            self.last_move_dir_x = 1 if dir_x > 0 else -1
            self.facing_right = self.last_move_dir_x > 0

        speed = self.base_speed * self.slow_factor

        self.x += dir_x * speed * dt
        self.y += dir_y * speed * dt

        if self.slow_timer > 0:
            self.slow_timer -= dt
        else:
            self.slow_factor = 1.0

    def take_damage(self, amount):
        if self.is_dead or self.death_started:
            return

        self.current_hp -= amount

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_dead = True
            self.death_started = True
            self.set_state("death")

    def apply_slow(self, factor, duration):
        self.slow_factor = factor
        self.slow_timer = duration

    def draw_hp_bar(self, screen):
        bar_width = 32
        bar_height = 6
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 26

        pygame.draw.rect(
            screen,
            (60, 60, 60),
            (bar_x, bar_y, bar_width, bar_height)
        )

        hp_ratio = self.current_hp / self.max_hp if self.max_hp > 0 else 0
        fill_width = int(bar_width * hp_ratio)

        pygame.draw.rect(
            screen,
            (80, 220, 120),
            (bar_x, bar_y, fill_width, bar_height)
        )

    def draw(self, screen):
        frames = self.get_current_frames()

        if frames:
            safe_index = min(self.anim_index, len(frames) - 1)
            frame = frames[safe_index]

            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)

            rect = frame.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(frame, rect)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 14)

        # แสดงหลอด HP เฉพาะตอนยังไม่ตาย
        if not self.is_dead:
            self.draw_hp_bar(screen)