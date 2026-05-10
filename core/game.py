# core/game.py

import json
import math
import random
import pygame
import config
from core.game_state import GameState
from ui.hud import HUD
from ui.side_panel import SidePanel
from maps.grid_map import GridMap
from maps.pathfinder import Pathfinder
from entities.base import Base
from systems.wave_manager import WaveManager
from entities.tower import create_tower
from core.asset_loader import AssetLoader
from core.audio_manager import AudioManager
from stats.stats_manager import StatsManager


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.WINDOW_TITLE)
        
        
        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.clock = pygame.time.Clock()

        self.game_state = GameState()
        self.hud = HUD(self.game_state)
        self.side_panel = SidePanel(self.game_state)

        self.grid_font = pygame.font.SysFont("arial", 14)
        self.info_font = pygame.font.SysFont("arial", 18)
        self.title_font = pygame.font.SysFont("arial", 24, bold=True)
        self.path_font = pygame.font.SysFont("arial", 16, bold=True)

        self.tower_cost = 100
        self.upgrade_cost = 100

        with open("data/towers/tower_stats.json", "r", encoding="utf-8") as f:
            self.tower_stats = json.load(f)

        self.audio = AudioManager()
        self.audio.play_music()

        self.stats = StatsManager()

        self.transition_active = False
        self.transition_timer = 0.0
        self.transition_duration = 2.0
        self.transition_text = ""
        self.next_map_index = None
        self.transition_loaded = False

        self.banner_text = ""
        self.banner_timer = 0.0
        self.banner_color = config.WARNING_COLOR

        self.victory_sound_played = False
        self.pending_boss_wave_start = False

        self.load_stage(self.game_state.current_map_index)

        self.wind_frames = []
        self.wind_index = 0
        self.wind_timer = 0.0
        self.wind_frame_duration = 0.07
        self.wind_alpha = 95
        self.wind_positions = [
            (170, 190),
            (470, 300),
            (760, 245),
            (270, 590),
            (660, 540),
        ]
        self.load_wind_effect()

        # visual effects
        self.effects = []
        self.projectile_trails = []
        self.screen_flash_timer = 0.0
        self.screen_flash_duration = 0.0
        self.screen_flash_color = (255, 255, 255)
        
        self.end_effect_started = False
        self.end_effect_timer = 0.0

    # =========================================================
    # Stage / Assets
    # =========================================================
    def load_stage(self, map_index):
        self.game_state.current_map_index = map_index

        map_json_path = f"data/maps/map{map_index}.json"
        enemy_json_path = f"data/enemies/map{map_index}_enemies.json"
        wave_json_path = f"data/waves/map{map_index}_waves.json"

        self.current_map = GridMap(map_json_path)

        self.spawn_cell = self.current_map.get_first_cell_by_type(config.SPAWN)
        self.base_cell = self.current_map.get_first_cell_by_type(config.BASE)

        self.base = None
        if self.base_cell is not None:
            self.base = Base(
                row=self.base_cell[0],
                col=self.base_cell[1],
                max_hp=config.STARTING_BASE_HP,
            )

        self.pathfinder = Pathfinder(self.current_map)
        self.enemy_path = self.pathfinder.find_path(self.spawn_cell, self.base_cell)
        self.path_is_valid = len(self.enemy_path) > 0
        self.game_state.path_is_valid = self.path_is_valid

        self.enemies = []
        self.projectiles = []
        self.towers = []
        self.game_state.towers = self.towers

        self.game_state.selected_tower = None
        self.game_state.selected_tower_type = None
        self.game_state.placing_mode = False

        self.game_state.base_hp = config.STARTING_BASE_HP
        self.game_state.wave = 1
        self.game_state.auto_wave_timer = 0.0
        self.game_state.game_over = False
        self.game_state.victory = False
        self.game_state.enemies_alive = 0
        self.game_state.wave_active = False

        self.wave_manager = WaveManager(
            self.enemy_path,
            enemy_json_path,
            wave_json_path,
        )

        self.preload_enemy_assets(enemy_json_path)
        self.stage_cleared = False

    def load_wind_effect(self):
        try:
            sheet = pygame.image.load("assets/effects/wind_sheet.png").convert_alpha()
        except Exception as e:
            print(f"[WARN] wind effect not loaded: {e}")
            return

        frame_width = 64
        frame_height = 32
        self.wind_frames = []

        for x in range(0, sheet.get_width(), frame_width):
            frame = sheet.subsurface((x, 0, frame_width, frame_height)).copy()
            frame = pygame.transform.smoothscale(frame, (112, 56))
            frame.set_alpha(self.wind_alpha)
            self.wind_frames.append(frame)

    def update_wind_effect(self, dt):
        if not self.wind_frames:
            return

        self.wind_timer += dt
        if self.wind_timer >= self.wind_frame_duration:
            self.wind_timer = 0.0
            self.wind_index = (self.wind_index + 1) % len(self.wind_frames)

    def draw_wind_effect(self):
        if not self.wind_frames:
            return

        frame = self.wind_frames[self.wind_index]
        for pos in self.wind_positions:
            self.screen.blit(frame, pos)

    def preload_enemy_assets(self, enemy_json_path):
        try:
            with open(enemy_json_path, "r", encoding="utf-8") as f:
                enemy_data = json.load(f)

            for enemy_type, stats in enemy_data.items():
                animations = stats.get("animations", {})
                for anim_name, anim_config in animations.items():
                    try:
                        AssetLoader.load_animation(anim_config)
                    except Exception as e:
                        print(f"[WARN] Failed to preload {enemy_type}:{anim_name} -> {e}")
        except Exception as e:
            print(f"[WARN] Failed to preload enemy assets from {enemy_json_path} -> {e}")

    # =========================================================
    # Premium Effects
    # =========================================================
    
    def start_end_effect(self, victory=True):
        if self.end_effect_started:
            return

        self.end_effect_started = True
        self.end_effect_timer = 0.0

        game_center_x = config.MAP_X + config.MAP_WIDTH // 2
        game_center_y = config.MAP_Y + config.MAP_HEIGHT // 2

        if victory:
            self.add_screen_flash((80, 220, 120), 0.25)
            self.add_soft_ring(game_center_x, game_center_y, color=(80, 220, 120), duration=1.2, max_radius=320, width=6)

            for _ in range(5):
                self.add_spark_burst(
                    game_center_x + random.randint(-180, 180),
                    game_center_y + random.randint(-120, 120),
                    color=(120, 255, 160),
                    duration=1.0,
                    count=26,
                    power=1.4,
                )
        else:
            self.add_screen_flash((255, 60, 60), 0.25)
            self.add_soft_ring(game_center_x, game_center_y, color=(255, 60, 60), duration=1.0, max_radius=280, width=6)

            for _ in range(5):
                self.add_spark_burst(
                    game_center_x + random.randint(-180, 180),
                    game_center_y + random.randint(-120, 120),
                    color=(255, 80, 70),
                    duration=0.9,
                    count=24,
                    power=1.2,
                )

    def add_soft_ring(self, x, y, color=(120, 180, 255), duration=0.35, max_radius=60, width=3):
        self.effects.append({
            "type": "soft_ring",
            "x": float(x),
            "y": float(y),
            "timer": 0.0,
            "duration": duration,
            "max_radius": max_radius,
            "color": color,
            "width": width,
        })

    def add_orb_glow(self, x, y, color=(120, 180, 255), duration=0.22, radius=28):
        self.effects.append({
            "type": "orb",
            "x": float(x),
            "y": float(y),
            "timer": 0.0,
            "duration": duration,
            "radius": radius,
            "color": color,
        })

    def add_spark_burst(self, x, y, color=(255, 170, 80), duration=0.42, count=18, power=1.0):
        particles = []

        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(90, 210) * power
            particles.append({
                "x": float(x),
                "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": random.uniform(2.0, 4.5),
                "drag": random.uniform(0.86, 0.93),
            })

        self.effects.append({
            "type": "sparks",
            "timer": 0.0,
            "duration": duration,
            "color": color,
            "particles": particles,
        })

    def add_enemy_death_effect(self, x, y, enemy_type="normal"):
        if enemy_type == "boss":
            color = (255, 70, 90)
            ring_color = (255, 50, 70)
            count = 34
            max_radius = 110
            duration = 0.7
            power = 1.35
            self.add_screen_flash((255, 60, 70), 0.16)
        elif enemy_type == "tank":
            color = (180, 130, 255)
            ring_color = (145, 110, 255)
            count = 22
            max_radius = 78
            duration = 0.55
            power = 1.0
        elif enemy_type == "fast":
            color = (90, 220, 255)
            ring_color = (80, 180, 255)
            count = 18
            max_radius = 64
            duration = 0.45
            power = 1.15
        else:
            color = (255, 180, 85)
            ring_color = (255, 120, 70)
            count = 18
            max_radius = 66
            duration = 0.48
            power = 1.0

        self.add_orb_glow(x, y, color=color, duration=duration * 0.55, radius=34)
        self.add_soft_ring(x, y, color=ring_color, duration=duration, max_radius=max_radius, width=4)
        self.add_spark_burst(x, y, color=color, duration=duration, count=count, power=power)

    def add_tower_shoot_effect(self, tower):
        try:
            x, y = tower.get_center()
        except Exception:
            return

        self.add_orb_glow(x, y - 6, color=(90, 170, 255), duration=0.14, radius=18)
        self.add_soft_ring(x, y - 6, color=(90, 170, 255), duration=0.24, max_radius=32, width=2)

    def add_base_hit_effect(self):
        self.add_screen_flash((255, 60, 60), 0.12)

        if self.base_cell is None:
            return

        br, bc = self.base_cell
        bx = config.MAP_X + bc * config.TILE_SIZE + config.TILE_SIZE // 2
        by = config.MAP_Y + br * config.TILE_SIZE + config.TILE_SIZE // 2

        self.add_orb_glow(bx, by, color=(255, 90, 70), duration=0.18, radius=42)
        self.add_soft_ring(bx, by, color=(255, 60, 60), duration=0.38, max_radius=72, width=4)

    def add_screen_flash(self, color=(255, 255, 255), duration=0.12):
        self.screen_flash_color = color
        self.screen_flash_timer = duration
        self.screen_flash_duration = duration

    def add_tower_upgrade_effect(self, tower):
        try:
            x, y = tower.get_center()
        except Exception:
            return

        # golden core glow
        self.add_orb_glow(
            x,
            y,
            color=(255, 220, 90),
            duration=0.45,
            radius=52
        )

        # outer upgrade shockwave
        self.add_soft_ring(
            x,
            y,
            color=(255, 220, 90),
            duration=0.75,
            max_radius=110,
            width=5
        )

        # blue magic ring
        self.add_soft_ring(
            x,
            y,
            color=(90, 170, 255),
            duration=0.55,
            max_radius=78,
            width=3
        )

        # spark burst
        self.add_spark_burst(
            x,
            y,
            color=(255, 230, 120),
            duration=0.75,
            count=32,
            power=1.35
        )

        # small screen flash
        self.add_screen_flash(
            color=(255, 220, 90),
            duration=0.10
        )
    def update_effects(self, dt):
        alive = []

        for effect in self.effects:
            effect["timer"] += dt

            if effect["type"] == "sparks":
                for p in effect["particles"]:
                    p["x"] += p["vx"] * dt
                    p["y"] += p["vy"] * dt
                    p["vx"] *= p["drag"]
                    p["vy"] *= p["drag"]
                    p["vy"] += 45 * dt

            if effect["timer"] < effect["duration"]:
                alive.append(effect)

        self.effects = alive

        for trail in self.projectile_trails:
            trail["timer"] += dt
        self.projectile_trails = [
            t for t in self.projectile_trails
            if t["timer"] < t["duration"]
        ]

        if self.screen_flash_timer > 0:
            self.screen_flash_timer -= dt
            if self.screen_flash_timer < 0:
                self.screen_flash_timer = 0

    def capture_projectile_trails(self):
        for projectile in self.projectiles:
            if getattr(projectile, "hit", False):
                continue

            color = getattr(projectile, "trail_color", None)

            if color is None:
                # fallback จากสี projectile เดิม
                color = getattr(projectile, "color", (90, 170, 255))

            self.projectile_trails.append({
                "x": float(projectile.x),
                "y": float(projectile.y),
                "timer": 0.0,
                "duration": 0.18,
                "color": color,
            })
    def get_tower_trail_color(self, tower_type):
        colors = {
            "basic": (90, 170, 255),     # blue
            "stun": (170, 100, 255),     # purple
            "sniper": (255, 210, 90),    # gold
            "multi": (90, 255, 160),     # green
        }
        return colors.get(tower_type, (90, 170, 255))
    
    
    def draw_effects(self):
        # projectile trails
        for trail in self.projectile_trails:
            progress = trail["timer"] / trail["duration"]
            alpha = int(150 * (1 - progress))
            radius = max(2, int(9 * (1 - progress)))

            surf = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(
                surf,
                (*trail["color"], alpha),
                (radius + 4, radius + 4),
                radius,
            )
            self.screen.blit(surf, (trail["x"] - radius - 4, trail["y"] - radius - 4))

        for effect in self.effects:
            progress = min(1.0, effect["timer"] / effect["duration"])
            ease_out = 1 - (1 - progress) * (1 - progress)

            if effect["type"] == "orb":
                radius = int(effect["radius"] * (1 - progress * 0.25))
                alpha = int(130 * (1 - progress))

                if radius <= 0:
                    continue

                surf = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
                pygame.draw.circle(
                    surf,
                    (*effect["color"], alpha),
                    (radius + 4, radius + 4),
                    radius,
                )
                pygame.draw.circle(
                    surf,
                    (*effect["color"], min(255, alpha + 40)),
                    (radius + 4, radius + 4),
                    max(2, radius // 3),
                )
                self.screen.blit(surf, (effect["x"] - radius - 4, effect["y"] - radius - 4))

            elif effect["type"] == "soft_ring":
                radius = int(effect["max_radius"] * ease_out)
                alpha = int(190 * (1 - progress))

                if radius <= 3:
                    continue

                size = radius * 2 + 16
                surf = pygame.Surface((size, size), pygame.SRCALPHA)

                pygame.draw.circle(
                    surf,
                    (*effect["color"], max(0, alpha // 3)),
                    (size // 2, size // 2),
                    radius + 4,
                    max(1, effect["width"] + 3),
                )
                pygame.draw.circle(
                    surf,
                    (*effect["color"], max(0, alpha)),
                    (size // 2, size // 2),
                    radius,
                    effect["width"],
                )

                self.screen.blit(surf, (effect["x"] - size // 2, effect["y"] - size // 2))

            elif effect["type"] == "sparks":
                alpha = int(220 * (1 - progress))
                for p in effect["particles"]:
                    size = max(1, int(p["size"] * (1 - progress * 0.5)))
                    surf = pygame.Surface((18, 18), pygame.SRCALPHA)
                    pygame.draw.circle(
                        surf,
                        (*effect["color"], alpha),
                        (9, 9),
                        size,
                    )
                    pygame.draw.circle(
                        surf,
                        (255, 255, 255, max(0, alpha // 2)),
                        (9, 9),
                        max(1, size // 2),
                    )
                    self.screen.blit(surf, (p["x"] - 9, p["y"] - 9))

        if self.screen_flash_timer > 0 and self.screen_flash_duration > 0:
            progress = self.screen_flash_timer / self.screen_flash_duration
            alpha = int(90 * progress)
            flash = pygame.Surface((config.MAP_WIDTH, config.MAP_HEIGHT), pygame.SRCALPHA)
            flash.fill((*self.screen_flash_color, alpha))
            self.screen.blit(flash, (config.MAP_X, config.MAP_Y))

    def draw_cinematic_lighting(self):
        overlay = pygame.Surface((config.MAP_WIDTH, config.MAP_HEIGHT), pygame.SRCALPHA)

        # soft ambient glows
        pygame.draw.circle(overlay, (80, 145, 255, 24), (160, 120), 250)
        pygame.draw.circle(
            overlay,
            (255, 80, 90, 16),
            (config.MAP_WIDTH - 150, config.MAP_HEIGHT - 120),
            270,
        )

        # smooth vignette, no hard rectangle
        steps = 28
        max_alpha = 72

        for i in range(steps):
            t = i / max(1, steps - 1)
            alpha = int(max_alpha * (1 - t) ** 2)
            thickness = 4

            pygame.draw.rect(overlay, (0, 0, 0, alpha), (0, i * thickness, config.MAP_WIDTH, thickness))
            pygame.draw.rect(overlay, (0, 0, 0, alpha), (0, config.MAP_HEIGHT - (i + 1) * thickness, config.MAP_WIDTH, thickness))
            pygame.draw.rect(overlay, (0, 0, 0, alpha), (i * thickness, 0, thickness, config.MAP_HEIGHT))
            pygame.draw.rect(overlay, (0, 0, 0, alpha), (config.MAP_WIDTH - (i + 1) * thickness, 0, thickness, config.MAP_HEIGHT))

        self.screen.blit(overlay, (config.MAP_X, config.MAP_Y))

    # =========================================================
    # Gameplay
    # =========================================================
    def show_banner(self, text, duration=2.0, color=None):
        self.banner_text = text
        self.banner_timer = duration
        self.banner_color = color if color is not None else config.WARNING_COLOR

    def wave_has_boss(self, wave_index):
        if wave_index < 0 or wave_index >= len(self.wave_manager.waves):
            return False

        wave_data = self.wave_manager.waves[wave_index]
        for group in wave_data.get("enemies", []):
            if group.get("type") == "boss":
                return True
        return False

    def start_next_wave(self):
        if not self.path_is_valid:
            return

        if self.game_state.game_over or self.game_state.victory:
            return

        if self.wave_manager.wave_active:
            return

        if not self.wave_manager.has_more_waves():
            return

        upcoming_wave_index = self.wave_manager.current_wave
        if self.wave_has_boss(upcoming_wave_index):
            self.show_banner(
                "! WARNING: BOSS APPROACHING !",
                duration=2.6,
                color=(210, 48, 48)
            )
            self.audio.play("warning")
            self.add_screen_flash((255, 40, 50), 0.18)
            self.pending_boss_wave_start = True
            return

        self.wave_manager.start_wave()

    def next_stage(self):
        pygame.mixer.music.fadeout(500)
        next_map_index = self.game_state.current_map_index + 1

        self.transition_active = True
        self.transition_timer = 0.0
        self.transition_loaded = False

        if next_map_index <= 2:
            self.transition_text = f"STAGE {next_map_index}"
            self.next_map_index = next_map_index
        else:
            self.transition_text = "VICTORY"
            self.next_map_index = None
            self.audio.play("victory")
            self.victory_sound_played = True

    def can_place_tower(self, row, col):
        tile = self.current_map.get_tile_at(row, col)

        if tile != config.BUILDABLE:
            return False

        for tower in self.towers:
            if tower.row == row and tower.col == col:
                return False

        return True

    def place_tower(self, row, col):
        if not self.can_place_tower(row, col):
            return

        if self.game_state.gold < self.tower_cost:
            return

        tower_type = self.game_state.selected_tower_type
        if tower_type is None:
            return

        if tower_type not in self.tower_stats:
            return

        stats = self.tower_stats[tower_type]
        tower = create_tower(row, col, tower_type, stats)

        self.towers.append(tower)
        self.game_state.gold -= self.tower_cost

        cx, cy = tower.get_center()
        self.add_orb_glow(cx, cy, color=(90, 170, 255), duration=0.25, radius=34)
        self.add_soft_ring(cx, cy, color=(90, 170, 255), duration=0.38, max_radius=58, width=3)

        self.stats.record_tower_placed(
            tower_type=tower_type,
            row=row,
            col=col,
            map_id=self.game_state.current_map_index,
            wave=self.game_state.wave,
        )
        self.stats.save_all()

    def run(self):
        while self.game_state.running:
            dt = self.clock.tick(config.FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

        self.stats.finalize_all_waves(
            self.game_state.current_map_index,
            len(self.wave_manager.waves)
        )
        self.stats.save_all()

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            self.side_panel.handle_event(event)

            if event.type == pygame.QUIT:
                self.game_state.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state.running = False

                elif event.key == pygame.K_p:
                    self.game_state.is_paused = not self.game_state.is_paused

                elif event.key == pygame.K_g:
                    self.game_state.show_grid = not self.game_state.show_grid

                elif event.key == pygame.K_o:
                    self.game_state.show_debug_overlay = (
                        not self.game_state.show_debug_overlay
                    )

                elif event.key == pygame.K_l:
                    self.game_state.show_cell_labels = (
                        not self.game_state.show_cell_labels
                    )

                elif event.key == pygame.K_k:
                    self.game_state.show_path_visual = (
                        not self.game_state.show_path_visual
                    )

                elif event.key == pygame.K_SPACE:
                    self.start_next_wave()

                elif event.key == pygame.K_r:
                    self.stats.finalize_all_waves(
                        self.game_state.current_map_index,
                        len(self.wave_manager.waves)
                    )
                    self.stats.save_all()
                    self.__init__()

                elif event.key == pygame.K_1:
                    self.game_state.selected_tower_type = "basic"
                    self.game_state.placing_mode = True
                    self.game_state.selected_tower = None

                elif event.key == pygame.K_2:
                    self.game_state.selected_tower_type = "stun"
                    self.game_state.placing_mode = True
                    self.game_state.selected_tower = None

                elif event.key == pygame.K_3:
                    self.game_state.selected_tower_type = "sniper"
                    self.game_state.placing_mode = True
                    self.game_state.selected_tower = None

                elif event.key == pygame.K_4:
                    self.game_state.selected_tower_type = "multi"
                    self.game_state.placing_mode = True
                    self.game_state.selected_tower = None

                elif event.key == pygame.K_q:
                    self.game_state.placing_mode = False

                elif event.key == pygame.K_u:
                    tower = self.game_state.selected_tower
                    if (
                        tower
                        and tower.level == 1
                        and self.game_state.gold >= self.upgrade_cost
                    ):
                        tower.upgrade()
                        self.game_state.gold -= self.upgrade_cost
                        self.add_tower_upgrade_effect(tower)

                elif event.key == pygame.K_x:
                    tower = self.game_state.selected_tower
                    if tower:
                        self.game_state.gold += tower.get_sell_value()
                        if tower in self.towers:
                            self.towers.remove(tower)
                        self.game_state.selected_tower = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    cell = self.current_map.pixel_to_cell(mx, my)

                    if cell is None:
                        continue

                    row, col = cell

                    if self.game_state.placing_mode:
                        self.place_tower(row, col)
                    else:
                        self.game_state.selected_tower = None
                        for tower in self.towers:
                            if tower.row == row and tower.col == col:
                                self.game_state.selected_tower = tower
                                break

    def update(self, dt):
        if self.game_state.is_paused:
            return

        self.stats.update_time(dt)

        if self.banner_timer > 0:
            self.banner_timer -= dt
            if self.banner_timer <= 0:
                self.banner_timer = 0
                self.banner_text = ""

                if self.pending_boss_wave_start:
                    self.pending_boss_wave_start = False
                    if not self.wave_manager.wave_active and self.wave_manager.has_more_waves():
                        self.wave_manager.start_wave()

        if self.transition_active:
            self.transition_timer += dt
            progress = self.transition_timer / self.transition_duration

            if (
                self.next_map_index is not None
                and not self.transition_loaded
                and progress >= 0.5
            ):
                self.load_stage(self.next_map_index)
                self.audio.play_music()
                self.transition_loaded = True

            if self.transition_timer >= self.transition_duration:
                self.transition_active = False

                if self.next_map_index is None:
                    self.game_state.victory = True
                    self.start_end_effect(victory=True)

            self.update_effects(dt)
            return

        if self.game_state.game_over or self.game_state.victory:
            self.update_effects(dt)
            return
    
        if getattr(self.game_state, "request_upgrade_selected", False):
            self.game_state.request_upgrade_selected = False

            tower = self.game_state.selected_tower
            if (
                tower
                and tower.level == 1
                and self.game_state.gold >= self.upgrade_cost
            ):
                tower.upgrade()
                self.game_state.gold -= self.upgrade_cost
                self.add_tower_upgrade_effect(tower)

        self.game_state.wave = min(
            self.wave_manager.current_wave + 1, len(self.wave_manager.waves)
        )

        if (
            self.path_is_valid
            and not self.wave_manager.wave_active
            and len(self.enemies) == 0
            and self.wave_manager.has_more_waves()
        ):
            self.game_state.auto_wave_timer += dt

            if self.game_state.auto_wave_timer >= self.game_state.auto_wave_delay:
                self.start_next_wave()
                self.game_state.auto_wave_timer = 0.0
        else:
            self.game_state.auto_wave_timer = 0.0

        if self.path_is_valid:
            before_enemy_ids = {id(enemy) for enemy in self.enemies}
            self.wave_manager.update(dt, self.enemies)

            for enemy in self.enemies:
                if id(enemy) not in before_enemy_ids:
                    self.stats.record_enemy_spawn(
                        enemy=enemy,
                        map_id=self.game_state.current_map_index,
                        wave=self.game_state.wave,
                    )
                    self.add_orb_glow(enemy.x, enemy.y, color=(120, 180, 255), duration=0.18, radius=28)

        for enemy in self.enemies:
            enemy.update(dt)

        for tower in self.towers:
            before = len(self.projectiles)
            tower.update(dt, self.enemies, self.projectiles)
            after = len(self.projectiles)

            if after > before:
                self.audio.play("shoot")
                self.add_tower_shoot_effect(tower)
                trail_color = self.get_tower_trail_color(getattr(tower, "type", ""))

                for projectile in self.projectiles[before:after]:
                    projectile.trail_color = trail_color

        for projectile in self.projectiles:
            projectile.update(dt)

        self.capture_projectile_trails()
        self.projectiles = [p for p in self.projectiles if not p.hit]

        for enemy in self.enemies:
            if enemy.reached_goal and not enemy.is_dead:
                if not hasattr(enemy, "attack_timer"):
                    enemy.attack_timer = 0

                enemy.attack_timer += dt

                if enemy.attack_timer >= 0.6:
                    if self.base:
                        self.base.take_damage(10)
                        self.game_state.base_hp = self.base.current_hp
                        self.add_base_hit_effect()

                    enemy.attack_timer = 0

        for enemy in self.enemies:
            if enemy.is_dead and not enemy.reward_given:
                self.game_state.gold += enemy.reward
                enemy.reward_given = True
                self.audio.play("death")

                self.add_enemy_death_effect(enemy.x, enemy.y, enemy.type)

                death_cell = self.current_map.pixel_to_cell(int(enemy.x), int(enemy.y))
                if death_cell is not None:
                    death_row, death_col = death_cell
                else:
                    death_row, death_col = -1, -1

                self.stats.record_enemy_death(
                    enemy=enemy,
                    row=death_row,
                    col=death_col,
                    map_id=self.game_state.current_map_index,
                    wave=self.game_state.wave,
                )
                self.stats.save_all()

        self.enemies = [
            enemy
            for enemy in self.enemies
            if not (enemy.is_dead and enemy.death_finished)
        ]

        self.update_wind_effect(dt)
        self.update_effects(dt)

        self.game_state.enemies_alive = len(
            [
                enemy
                for enemy in self.enemies
                if not enemy.is_dead and not enemy.reached_goal
            ]
        )
        self.game_state.wave_active = self.wave_manager.wave_active

        if self.base and self.base.is_destroyed():
            self.game_state.base_hp = 0
            self.game_state.game_over = True
            self.start_end_effect(victory=False)

        if not self.wave_manager.wave_active and len(self.enemies) == 0:
            self.stats.finalize_wave_if_needed(
                wave=self.game_state.wave,
                map_id=self.game_state.current_map_index,
            )
            self.stats.save_all()

        stage_cleared_now = (
            not self.wave_manager.wave_active
            and self.wave_manager.current_wave >= len(self.wave_manager.waves)
            and len(self.enemies) == 0
        )

        if stage_cleared_now and not self.stage_cleared:
            self.stage_cleared = True
            self.next_stage()

    # =========================================================
    # Draw
    # =========================================================
    def draw_selected_tower(self):
        tower = self.game_state.selected_tower
        if not tower:
            return

        x, y = tower.get_center()

        glow = pygame.Surface((96, 96), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 90, 60), (48, 48), 42)
        pygame.draw.circle(glow, (255, 245, 160, 120), (48, 48), 25, 2)
        self.screen.blit(glow, (x - 48, y - 48))

        pygame.draw.circle(self.screen, (255, 230, 80), (x, y), 25, 2)
        tower.draw_range(self.screen)

    def draw_towers(self):
        for tower in self.towers:
            tower.draw(self.screen)

    def draw_tower_preview(self):
        if not self.game_state.placing_mode:
            return

        cell = self.current_map.pixel_to_cell(*pygame.mouse.get_pos())
        if cell is None:
            return

        row, col = cell
        x, y = self.current_map.cell_to_pixel(row, col)

        can_place = self.can_place_tower(row, col)
        color = (80, 180, 255, 110) if can_place else (255, 80, 80, 110)

        overlay = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE), pygame.SRCALPHA)
        overlay.fill(color)
        self.screen.blit(overlay, (x, y))

        cx = x + config.TILE_SIZE // 2
        cy = y + config.TILE_SIZE // 2

        preview_range = 120
        selected_type = self.game_state.selected_tower_type

        if selected_type == "stun":
            preview_range = 100
        elif selected_type == "sniper":
            preview_range = 220
        elif selected_type == "multi":
            preview_range = 110

        pygame.draw.circle(self.screen, (80, 180, 255), (cx, cy), int(preview_range), 1)

    def draw_transition(self):
        if not self.transition_active:
            return

        progress = self.transition_timer / self.transition_duration

        if progress < 0.5:
            alpha = int(progress * 2 * 255)
        else:
            alpha = int((1 - progress) * 2 * 255)

        overlay = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

        color = (255, 255, 255)
        if self.transition_text == "VICTORY":
            color = (80, 220, 120)
        elif "STAGE" in self.transition_text:
            color = (110, 170, 255)

        scale = 1.0 + 0.08 * (1.0 - min(progress, 1.0))
        big_font = pygame.font.SysFont("arial", max(24, int(60 * scale)), bold=True)
        text_surface = big_font.render(self.transition_text, True, color)
        rect = text_surface.get_rect(
            center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        )

        glow = pygame.Surface((text_surface.get_width() + 40, text_surface.get_height() + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*color, 50), glow.get_rect(), border_radius=20)
        self.screen.blit(glow, (rect.x - 20, rect.y - 20))

        shadow = big_font.render(self.transition_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(rect.centerx + 3, rect.centery + 3))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(text_surface, rect)

    def draw_banner(self):
        if self.banner_timer <= 0 or not self.banner_text:
            return

        font = pygame.font.SysFont("arial", 38, bold=True)

        game_center_x = config.MAP_X + config.MAP_WIDTH // 2
        game_center_y = config.MAP_Y + config.MAP_HEIGHT // 2

        text = font.render(self.banner_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(game_center_x, game_center_y - 40))

        pulse = int(12 * abs(math.sin(pygame.time.get_ticks() * 0.012)))
        bg_rect = text_rect.inflate(66 + pulse, 34 + pulse)

        dark = pygame.Surface((config.MAP_WIDTH, config.MAP_HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 110))
        self.screen.blit(dark, (config.MAP_X, config.MAP_Y))

        glow = pygame.Surface((bg_rect.width + 34, bg_rect.height + 34), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 0, 0, 78), glow.get_rect(), border_radius=26)
        self.screen.blit(glow, (bg_rect.x - 17, bg_rect.y - 17))

        pygame.draw.rect(self.screen, (8, 8, 10), bg_rect, border_radius=20)
        pygame.draw.rect(self.screen, self.banner_color, bg_rect, 3, border_radius=20)

        shadow = font.render(self.banner_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(text, text_rect)

    def draw_projectiles(self):
        for projectile in self.projectiles:
            projectile.draw(self.screen)

    def draw_enemies(self):
        for enemy in self.enemies:
            enemy.draw(self.screen)

    def draw_map(self):
        self.current_map.draw_background(self.screen)

        if self.game_state.show_debug_overlay:
            self.current_map.draw_debug_overlay(self.screen)

        if self.game_state.show_grid:
            self.current_map.draw_grid(self.screen)

        if self.game_state.show_cell_labels:
            self.current_map.draw_cell_labels(self.screen, self.grid_font)

    def draw_path_visual(self):
        if not self.game_state.show_path_visual:
            return

        if not self.enemy_path:
            return

        for index, (row, col) in enumerate(self.enemy_path):
            x, y = self.current_map.cell_to_pixel(row, col)

            center_x = x + config.TILE_SIZE // 2
            center_y = y + config.TILE_SIZE // 2
            pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), 10)

            label = self.path_font.render(str(index), True, (20, 20, 20))
            label_rect = label.get_rect(center=(center_x, center_y))
            self.screen.blit(label, label_rect)

            if index < len(self.enemy_path) - 1:
                next_row, next_col = self.enemy_path[index + 1]
                next_x, next_y = self.current_map.cell_to_pixel(next_row, next_col)

                pygame.draw.line(
                    self.screen,
                    (255, 255, 255),
                    (center_x, center_y),
                    (next_x + config.TILE_SIZE // 2, next_y + config.TILE_SIZE // 2),
                    4,
                )

    def draw_base(self):
        if self.base is not None:
            if self.base_cell is not None:
                row, col = self.base_cell
                x = config.MAP_X + col * config.TILE_SIZE + config.TILE_SIZE // 2
                y = config.MAP_Y + row * config.TILE_SIZE + config.TILE_SIZE // 2

                glow = pygame.Surface((140, 140), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 190, 80, 36), (70, 70), 62)
                pygame.draw.circle(glow, (255, 90, 80, 24), (70, 70), 42)
                self.screen.blit(glow, (x - 70, y - 70))

            self.base.draw(self.screen, config.TILE_SIZE)

    def draw_pause_overlay(self):
        overlay_needed = (
            self.game_state.is_paused
            or self.game_state.game_over
            or self.game_state.victory
        )

        if not overlay_needed:
            return

        overlay = pygame.Surface((config.MAP_WIDTH, config.MAP_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (config.MAP_X, config.MAP_Y))

        font_big = pygame.font.SysFont("arial", 44, bold=True)
        font_small = pygame.font.SysFont("arial", 22)

        if self.game_state.game_over:
            title_text = "THE DUNGEON HAS FALLEN"
            title_color = (255, 80, 80)
            hint_text = "Press R to Restart"
        elif self.game_state.victory:
            title_text = "VICTORY"
            title_color = (80, 220, 120)
            hint_text = "Press R to Play Again"
        else:
            title_text = "PAUSED"
            title_color = (255, 255, 255)
            hint_text = "Press P to Resume"

        title = font_big.render(title_text, True, title_color)
        hint = font_small.render(hint_text, True, (255, 255, 255))

        title_rect = title.get_rect(
            center=(
                config.MAP_X + config.MAP_WIDTH // 2,
                config.MAP_Y + config.MAP_HEIGHT // 2 - 20,
            )
        )
        hint_rect = hint.get_rect(
            center=(
                config.MAP_X + config.MAP_WIDTH // 2,
                config.MAP_Y + config.MAP_HEIGHT // 2 + 30,
            )
        )

        shadow = font_big.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(title_rect.centerx + 3, title_rect.centery + 3))

        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        self.screen.blit(hint, hint_rect)

    def draw_bottom_guide_bar(self):
        y = config.TOP_BAR_HEIGHT + config.MAP_HEIGHT

        pygame.draw.rect(
            self.screen,
            (8, 10, 15),
            (0, y, config.SCREEN_WIDTH, config.BOTTOM_BAR_HEIGHT),
        )

        pygame.draw.rect(
            self.screen,
            (12, 15, 22),
            (0, y + 2, config.SCREEN_WIDTH, config.BOTTOM_BAR_HEIGHT - 2),
        )

        pygame.draw.line(
            self.screen,
            (74, 88, 108),
            (0, y),
            (config.SCREEN_WIDTH, y),
            1,
        )

        left_font = pygame.font.SysFont("arial", 15, bold=True)
        right_font = pygame.font.SysFont("arial", 15)

        left_surface = left_font.render("CONTROL STRIP", True, (106, 160, 255))
        self.screen.blit(left_surface, (18, y + 17))

        guide_text = (
            "SPACE Wave   |   R Restart   |   Q Cancel   |   "
            "P Pause   |   G Grid   |   O Overlay   |   K Path   |   L Labels   |   ESC Menu"
        )
        guide_surface = right_font.render(guide_text, True, (220, 220, 220))
        self.screen.blit(guide_surface, (150, y + 17))

    def draw_boss_aura(self):
        tick = pygame.time.get_ticks() * 0.006

        for enemy in self.enemies:
            if getattr(enemy, "type", "") != "boss":
                continue
            if getattr(enemy, "is_dead", False):
                continue

            pulse = int(8 * abs(math.sin(tick)))
            radius = 46 + pulse

            aura = pygame.Surface((radius * 2 + 20, radius * 2 + 20), pygame.SRCALPHA)

            pygame.draw.circle(
                aura,
                (255, 40, 60, 55),
                (radius + 10, radius + 10),
                radius
            )

            pygame.draw.circle(
                aura,
                (255, 80, 90, 130),
                (radius + 10, radius + 10),
                radius,
                3
            )

            self.screen.blit(
                aura,
                (enemy.x - radius - 10, enemy.y - radius - 10)
            )
    def draw(self):
        self.screen.fill(config.BG_COLOR)

        self.hud.draw(self.screen)

        self.draw_map()
        self.draw_cinematic_lighting()
        self.draw_wind_effect()

        self.draw_boss_aura()
        self.draw_enemies()
        self.draw_towers()
        self.draw_tower_preview()
        self.draw_selected_tower()
        self.draw_projectiles()
        self.draw_effects()
        self.draw_path_visual()
        self.draw_base()

        self.draw_banner()
        self.draw_pause_overlay()
        self.side_panel.draw(self.screen)
        self.draw_bottom_guide_bar()
        self.draw_transition()

        pygame.display.flip()