# utils/animation.py

import pygame
import os


class Animation:
    def __init__(self, frames, frame_duration=0.1, loop=True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop

        self.timer = 0
        self.index = 0
        self.finished = False

    def update(self, dt):
        if self.finished or not self.frames:
            return

        self.timer += dt

        if self.timer >= self.frame_duration:
            self.timer = 0
            self.index += 1

            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1
                    self.finished = True

    def get_frame(self):
        if not self.frames:
            return None
        return self.frames[self.index]


def load_from_folder(folder_path, scale=None):
    frames = []

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    for file_name in sorted(os.listdir(folder_path)):
        if file_name.lower().endswith(".png"):
            full_path = os.path.join(folder_path, file_name)
            img = pygame.image.load(full_path).convert_alpha()

            if scale is not None:
                img = pygame.transform.scale(img, scale)

            frames.append(img)

    if not frames:
        raise ValueError(f"No PNG frames found in folder: {folder_path}")

    return frames


def load_from_spritesheet(image_path, frame_width, frame_height, scale=None):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Spritesheet not found: {image_path}")

    image = pygame.image.load(image_path).convert_alpha()
    sheet_width, sheet_height = image.get_size()

    frames = []

    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            frame = image.subsurface((x, y, frame_width, frame_height)).copy()

            if scale is not None:
                frame = pygame.transform.scale(frame, scale)

            frames.append(frame)

    if not frames:
        raise ValueError(f"No frames extracted from spritesheet: {image_path}")

    return frames