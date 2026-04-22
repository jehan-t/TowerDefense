# maps/map_loader.py

import json
import os
import config


def create_empty_grid():
    return [
        [config.EMPTY for _ in range(config.MAP_COLS)]
        for _ in range(config.MAP_ROWS)
    ]


def load_map_json(filepath):
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_map_json(filepath, map_name, image_path, grid):
    data = {
        "map_name": map_name,
        "cols": config.MAP_COLS,
        "rows": config.MAP_ROWS,
        "tile_size": config.TILE_SIZE,
        "image_path": image_path,
        "grid": grid
    }

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)