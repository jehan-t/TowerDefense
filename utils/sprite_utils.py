# utils/sprite_utils.py

import os
import pygame


def load_image(path, scale=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")

    image = pygame.image.load(path).convert_alpha()

    if scale is not None:
        image = pygame.transform.scale(image, scale)

    return image


def slice_sheet_horizontal(path, frame_count, scale=None):
    """
    ตัดภาพแนวนอนออกเป็นหลายเฟรมขนาดเท่ากัน
    เช่น base_sheet 2 ช่องซ้าย-ขวา
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")

    sheet = pygame.image.load(path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()

    frame_width = sheet_width // frame_count
    frames = []

    for i in range(frame_count):
        frame = sheet.subsurface((i * frame_width, 0, frame_width, sheet_height)).copy()

        if scale is not None:
            frame = pygame.transform.scale(frame, scale)

        frames.append(frame)

    return frames


def slice_sheet_grid(path, columns, rows, scale=None):
    """
    ตัดภาพเป็น grid
    ใช้ได้กับ weapon_sheet หรือ projectile_sheet ถ้าต้องการหลายเฟรม
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")

    sheet = pygame.image.load(path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()

    frame_width = sheet_width // columns
    frame_height = sheet_height // rows

    frames = []

    for row in range(rows):
        for col in range(columns):
            frame = sheet.subsurface(
                (col * frame_width, row * frame_height, frame_width, frame_height)
            ).copy()

            if scale is not None:
                frame = pygame.transform.scale(frame, scale)

            frames.append(frame)

    return frames