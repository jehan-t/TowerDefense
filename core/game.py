# core/game.py

import json
import math
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

        # audio
        self.audio = AudioManager()
        self.audio.play_music()

        self.stats = StatsManager()

        # transition system
        self.transition_active = False
        self.transition_timer = 0.0
        self.transition_duration = 2.0
        self.transition_text = ""
        self.next_map_index = None
        self.transition_loaded = False

        # banners / warnings
        self.banner_text = ""
        self.banner_timer = 0.0
        self.banner_color = config.WARNING_COLOR

        self.victory_sound_played = False

        self.load_stage(self.game_state.current_map_index)

        self.wind_frames = []
        self.wind_index = 0
        self.wind_timer = 0.0
        self.wind_frame_duration = 0.07
        self.wind_alpha = 110
        self.wind_positions = [
            (200, 200),
            (500, 300),
            (800, 250),
            (300, 600),
            (700, 550),
        ]

        self.load_wind_effect()

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
        sheet = pygame.image.load("assets/effects/wind_sheet.png").convert_alpha()

        frame_width = 64
        frame_height = 32

        self.wind_frames = []

        for x in range(0, sheet.get_width(), frame_width):
            frame = sheet.subsurface((x, 0, frame_width, frame_height)).copy()
            frame.set_alpha(self.wind_alpha)
            frame = pygame.transform.scale(frame, (96, 48))
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
                "⚠ WARNING: BOSS APPROACHING ⚠",
                duration=2.6,
                color=(210, 48, 48)
            )
            self.audio.play("warning")

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

            return

        if self.game_state.game_over or self.game_state.victory:
            return

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

        for enemy in self.enemies:
            enemy.update(dt)

        for tower in self.towers:
            before = len(self.projectiles)
            tower.update(dt, self.enemies, self.projectiles)
            after = len(self.projectiles)

            if after > before:
                self.audio.play("shoot")

        for projectile in self.projectiles:
            projectile.update(dt)

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

                    enemy.attack_timer = 0

        for enemy in self.enemies:
            if enemy.is_dead and not enemy.reward_given:
                self.game_state.gold += enemy.reward
                enemy.reward_given = True
                self.audio.play("death")

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

    def draw_selected_tower(self):
        tower = self.game_state.selected_tower
        if not tower:
            return

        x, y = tower.get_center()
        pygame.draw.circle(self.screen, (255, 255, 0), (x, y), 22, 2)
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
        color = (80, 180, 255, 120) if can_place else (255, 80, 80, 120)

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

        # กลางเฉพาะพื้นที่เกม ไม่รวม side panel
        game_center_x = config.MAP_X + config.MAP_WIDTH // 2
        game_center_y = config.MAP_Y + config.MAP_HEIGHT // 2

        text = font.render(self.banner_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(game_center_x, game_center_y - 40))

        pulse = int(12 * abs(math.sin(pygame.time.get_ticks() * 0.012)))
        bg_rect = text_rect.inflate(66 + pulse, 34 + pulse)

        # dark overlay เฉพาะในส่วน map
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

    def draw(self):
        self.screen.fill(config.BG_COLOR)

        self.hud.draw(self.screen)
        self.draw_map()
        self.draw_wind_effect()
        self.draw_enemies()
        self.draw_towers()
        self.draw_tower_preview()
        self.draw_selected_tower()
        self.draw_projectiles()
        self.draw_path_visual()
        self.draw_base()
        self.draw_banner()
        self.draw_pause_overlay()
        self.side_panel.draw(self.screen)
        self.draw_bottom_guide_bar()
        self.draw_transition()

        pygame.display.flip()