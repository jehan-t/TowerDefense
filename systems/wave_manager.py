# systems/wave_manager.py

import json
from entities.enemy import Enemy


class WaveManager:
    def __init__(self, path, map_enemy_file, wave_file):
        self.path = path

        with open(map_enemy_file, "r", encoding="utf-8") as f:
            self.enemy_stats = json.load(f)

        with open(wave_file, "r", encoding="utf-8") as f:
            self.waves = json.load(f)

        self.current_wave = 0
        self.wave_active = False

        self.spawn_queue = []
        self.timer = 0

    def has_more_waves(self):
        return self.current_wave < len(self.waves)

    def start_wave(self):
        if self.wave_active:
            return False

        if not self.has_more_waves():
            return False

        wave_data = self.waves[self.current_wave]
        self.spawn_queue = []

        for group in wave_data["enemies"]:
            for _ in range(group["count"]):
                self.spawn_queue.append((group["type"], group["delay"]))

        self.wave_active = True
        self.timer = 0
        return True

    def update(self, dt, enemy_list):
        if not self.wave_active:
            return

        if not self.spawn_queue:
            self.wave_active = False
            self.current_wave += 1
            return

        self.timer += dt

        enemy_type, delay = self.spawn_queue[0]

        if self.timer >= delay:
            self.timer = 0

            stats = self.enemy_stats[enemy_type]
            enemy = Enemy(self.path, enemy_type, stats)
            enemy_list.append(enemy)

            self.spawn_queue.pop(0)