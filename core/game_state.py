# core/game_state.py

import config


class GameState:
    def __init__(self):
        self.running = True

        self.current_map_index = config.STARTING_MAP_INDEX
        self.gold = config.STARTING_GOLD
        self.base_hp = config.STARTING_BASE_HP
        self.wave = config.STARTING_WAVE

        self.selected_tower_type = None
        self.selected_tower = None
        self.placing_mode = False

        self.is_paused = False

        # ตอนเริ่มเกม ปิดไว้ก่อน
        self.show_grid = False
        self.show_debug_overlay = False
        self.show_cell_labels = False
        self.show_path_visual = False

        self.path_is_valid = False

        self.game_over = False
        self.victory = False

        self.auto_wave_timer = 0.0
        self.auto_wave_delay = 3.0

        self.enemies_alive = 0
        self.wave_active = False

        self.towers = []