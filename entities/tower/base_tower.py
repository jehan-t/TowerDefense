import math
import pygame
import config


class BaseTower:
    def __init__(self, row, col, tower_type, stats):
        self.row = row
        self.col = col
        self.type = tower_type

        self.level = 1

        self.range = stats["range"]
        self.damage = stats["damage"]
        self.fire_rate = stats["fire_rate"]
        self.color = tuple(stats["color"])

        self.cooldown = 0.0

        self.current_target = None
        self.last_angle = 0
        self.weapon_offset_y = -6

        # attack state
        self.is_attacking = False

        # animation
        self.weapon_frames = None
        self.weapon_anim_index = 0
        self.weapon_anim_timer = 0.0
        self.weapon_anim_speed = 0.08

        # assets
        self.base_frames = None
        self.projectile_image = None

    def get_center(self):
        x = config.MAP_X + self.col * config.TILE_SIZE + config.TILE_SIZE // 2
        y = config.MAP_Y + self.row * config.TILE_SIZE + config.TILE_SIZE // 2
        return x, y

    def get_targets(self, enemies):
        cx, cy = self.get_center()
        targets = []

        for enemy in enemies:
            if getattr(enemy, "is_dead", False):
                continue

            dx = enemy.x - cx
            dy = enemy.y - cy
            dist = math.hypot(dx, dy)

            if dist <= self.range:
                targets.append((dist, enemy))

        targets.sort(key=lambda item: item[0])
        return [enemy for _, enemy in targets]

    def update_weapon_animation(self, dt):
        if not self.weapon_frames:
            return

        if not self.is_attacking:
            self.weapon_anim_index = 0
            self.weapon_anim_timer = 0.0
            return

        self.weapon_anim_timer += dt

        if self.weapon_anim_timer >= self.weapon_anim_speed:
            self.weapon_anim_timer = 0.0
            self.weapon_anim_index += 1

            if self.weapon_anim_index >= len(self.weapon_frames):
                self.weapon_anim_index = 0
                self.is_attacking = False

    def update_aim(self, enemies):
        targets = self.get_targets(enemies)
        self.current_target = targets[0] if targets else None

        if self.current_target is not None:
            cx, cy = self.get_center()
            dx = self.current_target.x - cx
            dy = self.current_target.y - cy

            # ภาพตั้งต้นชี้ขึ้นบน
            self.last_angle = -math.degrees(math.atan2(dy, dx)) - 90

        return targets

    def update(self, dt, enemies, projectiles):
        self.update_weapon_animation(dt)
        raise NotImplementedError

    def upgrade(self):
        if self.level == 1:
            self.level = 2
            self.damage *= 1.5
            self.range *= 1.2
            self.fire_rate *= 1.2

    def get_sell_value(self):
        return 70

    def create_projectile(self, target, projectile_cls, damage=None, speed=300):
        cx, cy = self.get_center()
        return projectile_cls(
            cx,
            cy,
            target,
            speed=speed,
            damage=self.damage if damage is None else damage,
            image=self.projectile_image,
            color=self.color,
        )

    def draw_base(self, screen):
        x, y = self.get_center()

        if self.base_frames:
            index = 0 if self.level == 1 else 1
            index = min(index, len(self.base_frames) - 1)
            frame = self.base_frames[index]
            rect = frame.get_rect(center=(x, y))
            screen.blit(frame, rect)
        else:
            pygame.draw.circle(screen, self.color, (x, y), 16)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 16, 2)

    def draw_weapon(self, screen):
        if not self.weapon_frames:
            return

        x, y = self.get_center()

        frame = self.weapon_frames[self.weapon_anim_index]
        rotated = pygame.transform.rotate(frame, self.last_angle)
        rect = rotated.get_rect(center=(x, y + self.weapon_offset_y))
        screen.blit(rotated, rect)

    def draw_level_text(self, screen):
        x, y = self.get_center()
        font = pygame.font.SysFont("arial", 14, bold=True)
        text = font.render(str(self.level), True, (255, 255, 255))
        screen.blit(text, (x - 4, y + 10))

    def draw(self, screen):
        self.draw_base(screen)

        # ถ้าไม่มีทั้ง base frame และ weapon frame ให้ fallback เป็นวงกลม
        if not self.base_frames and not self.weapon_frames:
            x, y = self.get_center()
            pygame.draw.circle(screen, self.color, (x, y), 16)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 16, 2)

        self.draw_weapon(screen)
        self.draw_level_text(screen)

    def draw_range(self, screen):
        x, y = self.get_center()
        pygame.draw.circle(screen, self.color, (x, y), int(self.range), 1)