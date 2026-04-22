from utils.sprite_utils import slice_sheet_horizontal, slice_sheet_grid
from entities.projectile import Projectile
from .base_tower import BaseTower


class BasicTower(BaseTower):
    def __init__(self, row, col, stats):
        super().__init__(row, col, "basic", stats)
        self.load_assets()

    def load_assets(self):
        base_path = "assets/images/towers/basic/base_sheet.png"
        weapon_path = "assets/images/towers/basic/weapon_sheet.png"
        projectile_path = "assets/images/towers/basic/projectile_sheet.png"

        # Base: 2 เฟรม (level 1 / level 2)
        try:
            self.base_frames = slice_sheet_horizontal(
                base_path,
                frame_count=2,
                scale=(32, 64)
            )
        except Exception:
            self.base_frames = None

        # Weapon: ใช้ animation frames
        try:
            self.weapon_frames = slice_sheet_grid(
                weapon_path,
                columns=6,
                rows=1,
                scale=(60, 60)
            )
        except Exception:
            self.weapon_frames = None

        # Projectile: ใช้ animation frames
        try:
            self.projectile_image = slice_sheet_grid(
                projectile_path,
                columns=3,
                rows=1,
                scale=(18, 18)
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
            projectiles.append(projectile)

            self.is_attacking = True
            self.cooldown = 1 / self.fire_rate