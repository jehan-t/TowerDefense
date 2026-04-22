# entities/projectile.py

import pygame
import math


class Projectile:
    def __init__(self, x, y, target, speed=300, damage=20, image=None, color=(255, 120, 50)):
        self.x = x
        self.y = y

        self.target = target
        self.speed = speed
        self.damage = damage

        self.hit = False

        self.image = image
        self.color = color

        self.slow_factor = None
        self.slow_duration = None

        # รูปต้นฉบับชี้ขึ้นบน
        self.angle = 0

        self.frames = []
        self.anim_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.06

        if isinstance(image, list):
            self.frames = [frame for frame in image if frame is not None]
        elif image is not None:
            self.frames = [image]

    def update(self, dt):
        if self.hit or self.target is None:
            return

        tx, ty = self.target.x, self.target.y

        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist < 8:
            self.target.take_damage(self.damage)

            if self.slow_factor is not None:
                self.target.apply_slow(self.slow_factor, self.slow_duration)

            self.hit = True
            return

        dir_x = dx / dist
        dir_y = dy / dist

        self.x += dir_x * self.speed * dt
        self.y += dir_y * self.speed * dt

        # รูป projectile ตั้งต้นชี้ขึ้นบน
        self.angle = -math.degrees(math.atan2(dy, dx)) - 90

        # animation
        if len(self.frames) > 1:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_index = (self.anim_index + 1) % len(self.frames)

    def draw(self, screen):
        if self.frames:
            img = self.frames[self.anim_index]

            # หมุนตามทิศบิน
            rotated = pygame.transform.rotate(img, self.angle)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 4)