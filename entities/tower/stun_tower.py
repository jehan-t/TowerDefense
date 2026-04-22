from utils.sprite_utils import slice_sheet_horizontal, slice_sheet_grid
from entities.projectile import Projectile
from .base_tower import BaseTower


class StunTower(BaseTower):
    def __init__(self, row, col, stats):
        super().__init__(row, col, "stun", stats)

        self.slow_factor = stats.get("slow_factor", 0.4)
        self.slow_duration = stats.get("slow_duration", 0.8)

        self.load_assets()

    def load_assets(self):
        base_path = "assets/images/towers/stun/base_sheet.png"
        weapon_path = "assets/images/towers/stun/weapon_sheet.png"
        projectile_path = "assets/images/towers/stun/projectile_sheet.png"

        try:
            self.base_frames = slice_sheet_horizontal(
                base_path,
                frame_count=2,
                scale=(32, 64)
            )
        except Exception:
            self.base_frames = None

        try:
            self.weapon_frames = slice_sheet_grid(
                weapon_path,
                columns=16,
                rows=2,
                scale=(42, 42)
            )
        except Exception:
            self.weapon_frames = None

        try:
            self.projectile_image = slice_sheet_grid(
                projectile_path,
                columns=5,
                rows=1,
                scale=(36, 36)
            )
        except Exception:
            self.projectile_image = None

    def update(self, dt, enemies, projectiles):
        self.cooldown -= dt

        targets = self.update_aim(enemies)
        self.update_weapon_animation(dt)

        if self.cooldown <= 0 and targets:
            target = targets[0]

            projectile = self.create_projectile(target, Projectile)
            projectile.slow_factor = self.slow_factor
            projectile.slow_duration = self.slow_duration

            projectiles.append(projectile)

            self.is_attacking = True
            self.cooldown = 1 / self.fire_rate