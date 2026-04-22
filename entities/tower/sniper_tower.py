from utils.sprite_utils import slice_sheet_horizontal, slice_sheet_grid
from entities.projectile import Projectile
from .base_tower import BaseTower


class SniperTower(BaseTower):
    def __init__(self, row, col, stats):
        super().__init__(row, col, "sniper", stats)
        self.load_assets()

    def load_assets(self):
        base_path = "assets/images/towers/sniper/base_sheet.png"
        weapon_path = "assets/images/towers/sniper/weapon_sheet.png"
        projectile_path = "assets/images/towers/sniper/projectile_sheet.png"

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
                columns=10,
                rows=1,
                scale=(42, 42)
            )
        except Exception:
            self.weapon_frames = None

        try:
            self.projectile_image = slice_sheet_grid(
                projectile_path,
                columns=6,
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

            projectile = self.create_projectile(
                target,
                Projectile,
                damage=self.damage * 2,
                speed=450
            )

            projectiles.append(projectile)

            self.is_attacking = True
            self.cooldown = 1 / (self.fire_rate * 0.6)