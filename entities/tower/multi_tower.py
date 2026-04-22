from utils.sprite_utils import slice_sheet_horizontal, slice_sheet_grid
from entities.projectile import Projectile
from .base_tower import BaseTower


class MultiTower(BaseTower):
    def __init__(self, row, col, stats):
        super().__init__(row, col, "multi", stats)

        self.max_targets = stats.get("max_targets", 3)
        self.load_assets()

    def load_assets(self):
        base_path = "assets/images/towers/multi/base_sheet.png"
        weapon_path = "assets/images/towers/multi/weapon_sheet.png"
        projectile_path = "assets/images/towers/multi/projectile_sheet.png"

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
                columns=7,
                rows=1,
                scale=(42, 42)
            )
        except Exception:
            self.weapon_frames = None

        try:
            self.projectile_image = slice_sheet_grid(
                projectile_path,
                columns=8,
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
            for target in targets[:self.max_targets]:
                projectile = self.create_projectile(target, Projectile)
                projectiles.append(projectile)

            self.is_attacking = True
            self.cooldown = 1 / self.fire_rate