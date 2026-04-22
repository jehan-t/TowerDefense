# core/asset_loader.py

import os
import pygame


class AssetLoader:
    _image_cache = {}
    _animation_cache = {}

    @staticmethod
    def _make_anim_key(anim_config):
        mode = anim_config.get("mode", "")
        path = anim_config.get("path", "")
        scale = tuple(anim_config.get("scale", [])) if anim_config.get("scale") else None
        frame_width = anim_config.get("frame_width")
        frame_height = anim_config.get("frame_height")
        return (mode, path, scale, frame_width, frame_height)

    @staticmethod
    def load_image(path, scale=None):
        key = (path, tuple(scale) if scale else None)

        if key in AssetLoader._image_cache:
            return AssetLoader._image_cache[key]

        if not os.path.exists(path):
            raise FileNotFoundError(f"Image not found: {path}")

        image = pygame.image.load(path).convert_alpha()

        if scale is not None:
            image = pygame.transform.scale(image, scale)

        AssetLoader._image_cache[key] = image
        return image

    @staticmethod
    def load_animation(anim_config):
        key = AssetLoader._make_anim_key(anim_config)

        if key in AssetLoader._animation_cache:
            return AssetLoader._animation_cache[key]

        mode = anim_config.get("mode")
        path = anim_config.get("path")
        scale = tuple(anim_config.get("scale", [])) if anim_config.get("scale") else None

        if mode == "folder":
            frames = AssetLoader._load_from_folder(path, scale)
        elif mode == "sheet":
            frame_width = anim_config["frame_width"]
            frame_height = anim_config["frame_height"]
            frames = AssetLoader._load_from_sheet(path, frame_width, frame_height, scale)
        else:
            raise ValueError(f"Unsupported animation mode: {mode}")

        AssetLoader._animation_cache[key] = frames
        return frames

    @staticmethod
    def _load_from_folder(folder_path, scale=None):
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        files = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith(".png")
        ]

        # สำคัญ: เรียงแบบ natural sort เพื่อกัน 10 มาก่อน 2
        def natural_sort_key(text):
            import re
            return [int(part) if part.isdigit() else part.lower()
                    for part in re.split(r"(\d+)", text)]

        files.sort(key=natural_sort_key)

        frames = []
        for filename in files:
            full_path = os.path.join(folder_path, filename)
            image = pygame.image.load(full_path).convert_alpha()

            if scale is not None:
                image = pygame.transform.scale(image, scale)

            frames.append(image)

        return frames

    @staticmethod
    def _load_from_sheet(image_path, frame_width, frame_height, scale=None):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Spritesheet not found: {image_path}")

        sheet = pygame.image.load(image_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()

        frames = []
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                frame = sheet.subsurface((x, y, frame_width, frame_height)).copy()

                if scale is not None:
                    frame = pygame.transform.scale(frame, scale)

                frames.append(frame)

        return frames