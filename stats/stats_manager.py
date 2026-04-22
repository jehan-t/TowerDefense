# stats/stats_manager.py

import os
import csv
import time


class StatsManager:
    def __init__(self, output_dir="data/stats"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.session_id = int(time.time())
        self.session_elapsed = 0.0

        self.enemy_spawn_lookup = {}
        self.kills_per_wave_counter = {}
        self.towers_placed_per_wave_counter = {}

        self.tower_usage_rows = []
        self.enemy_defeat_rows = []
        self.enemy_death_position_rows = []
        self.tower_position_rows = []
        self.enemy_survival_rows = []
        self.wave_summary_rows = []

    def update_time(self, dt):
        self.session_elapsed += dt

    def record_tower_placed(self, tower_type, row, col, map_id, wave):
        row_data = {
            "session_id": self.session_id,
            "time": round(self.session_elapsed, 3),
            "tower_type": tower_type,
            "row": row,
            "col": col,
            "map_id": map_id,
            "wave": wave,
        }

        self.tower_usage_rows.append(row_data)
        self.tower_position_rows.append(row_data.copy())

        self.towers_placed_per_wave_counter[wave] = (
            self.towers_placed_per_wave_counter.get(wave, 0) + 1
        )

    def record_enemy_spawn(self, enemy, map_id, wave):
        self.enemy_spawn_lookup[id(enemy)] = {
            "enemy_type": enemy.type,
            "spawn_time": self.session_elapsed,
            "map_id": map_id,
            "wave": wave,
        }

    def record_enemy_death(self, enemy, row, col, map_id, wave):
        enemy_id = id(enemy)
        spawn_data = self.enemy_spawn_lookup.get(enemy_id)

        spawn_time = self.session_elapsed
        enemy_type = enemy.type

        if spawn_data is not None:
            spawn_time = spawn_data["spawn_time"]
            enemy_type = spawn_data["enemy_type"]

        death_time = self.session_elapsed
        survival_time = death_time - spawn_time

        self.enemy_defeat_rows.append({
            "session_id": self.session_id,
            "time": round(death_time, 3),
            "enemy_type": enemy_type,
            "map_id": map_id,
            "wave": wave,
        })

        self.enemy_death_position_rows.append({
            "session_id": self.session_id,
            "time": round(death_time, 3),
            "enemy_type": enemy_type,
            "row": row,
            "col": col,
            "map_id": map_id,
            "wave": wave,
        })

        self.enemy_survival_rows.append({
            "session_id": self.session_id,
            "enemy_type": enemy_type,
            "map_id": map_id,
            "wave": wave,
            "spawn_time": round(spawn_time, 3),
            "death_time": round(death_time, 3),
            "survival_time": round(survival_time, 3),
        })

        self.kills_per_wave_counter[wave] = (
            self.kills_per_wave_counter.get(wave, 0) + 1
        )

        if enemy_id in self.enemy_spawn_lookup:
            del self.enemy_spawn_lookup[enemy_id]

    def finalize_wave_if_needed(self, wave, map_id):
        existing = [
            row for row in self.wave_summary_rows
            if row["wave"] == wave and row["map_id"] == map_id and row["session_id"] == self.session_id
        ]
        if existing:
            return

        self.wave_summary_rows.append({
            "session_id": self.session_id,
            "map_id": map_id,
            "wave": wave,
            "enemies_killed": self.kills_per_wave_counter.get(wave, 0),
            "towers_placed": self.towers_placed_per_wave_counter.get(wave, 0),
        })

    def finalize_all_waves(self, map_id, total_wave_count):
        for wave in range(1, total_wave_count + 1):
            self.finalize_wave_if_needed(wave, map_id)

    def _append_or_create_csv(self, filename, fieldnames, rows):
        if not rows:
            return

        path = os.path.join(self.output_dir, filename)
        file_exists = os.path.exists(path)

        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerows(rows)

    def save_all(self):
        self._append_or_create_csv(
            "tower_usage.csv",
            ["session_id", "time", "tower_type", "row", "col", "map_id", "wave"],
            self.tower_usage_rows,
        )

        self._append_or_create_csv(
            "enemy_defeats.csv",
            ["session_id", "time", "enemy_type", "map_id", "wave"],
            self.enemy_defeat_rows,
        )

        self._append_or_create_csv(
            "enemy_death_positions.csv",
            ["session_id", "time", "enemy_type", "row", "col", "map_id", "wave"],
            self.enemy_death_position_rows,
        )

        self._append_or_create_csv(
            "tower_positions.csv",
            ["session_id", "time", "tower_type", "row", "col", "map_id", "wave"],
            self.tower_position_rows,
        )

        self._append_or_create_csv(
            "enemy_survival.csv",
            ["session_id", "enemy_type", "map_id", "wave", "spawn_time", "death_time", "survival_time"],
            self.enemy_survival_rows,
        )

        self._append_or_create_csv(
            "wave_summary.csv",
            ["session_id", "map_id", "wave", "enemies_killed", "towers_placed"],
            self.wave_summary_rows,
        )

        # clear after flush
        self.tower_usage_rows.clear()
        self.enemy_defeat_rows.clear()
        self.enemy_death_position_rows.clear()
        self.tower_position_rows.clear()
        self.enemy_survival_rows.clear()
        self.wave_summary_rows.clear()