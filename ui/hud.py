# ui/hud.py

import pygame
import config


class HUD:
    def __init__(self, game_state):
        self.game_state = game_state

        self.title_font = pygame.font.SysFont("timesnewroman", 34, bold=True)
        self.subtitle_font = pygame.font.SysFont("arial", 16, bold=True)

        self.card_label_font = pygame.font.SysFont("arial", 12, bold=True)
        self.card_value_font = pygame.font.SysFont("arial", 21, bold=True)

        self.status_font = pygame.font.SysFont("arial", 14, bold=True)
        self.small_font = pygame.font.SysFont("arial", 13, bold=True)

        # แบ่งพื้นที่ header ชัดๆ
        self.left_zone_width = 430
        self.header_padding = 18
        self.card_gap = 12

    def draw_background(self, screen):
        pygame.draw.rect(
            screen,
            (10, 13, 19),
            (0, 0, config.SCREEN_WIDTH, config.TOP_BAR_HEIGHT)
        )

        pygame.draw.rect(
            screen,
            (16, 20, 28),
            (0, 0, config.SCREEN_WIDTH, 88)
        )
        pygame.draw.rect(
            screen,
            (8, 10, 15),
            (0, 88, config.SCREEN_WIDTH, config.TOP_BAR_HEIGHT - 88)
        )

        shade = pygame.Surface((config.SCREEN_WIDTH, config.TOP_BAR_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 28))
        screen.blit(shade, (0, 0))

        pygame.draw.line(
            screen,
            (255, 255, 255, 25),
            (0, 0),
            (config.SCREEN_WIDTH, 0),
            1
        )
        pygame.draw.line(
            screen,
            (76, 90, 112),
            (0, config.TOP_BAR_HEIGHT - 1),
            (config.SCREEN_WIDTH, config.TOP_BAR_HEIGHT - 1),
            2
        )

        # glow เฉพาะฝั่ง title
        glow = pygame.Surface((360, 120), pygame.SRCALPHA)
        pygame.draw.rect(glow, (70, 120, 255, 20), glow.get_rect(), border_radius=24)
        screen.blit(glow, (12, 8))

        # เส้นแบ่ง title zone กับ stat zone
        divider_x = self.left_zone_width
        pygame.draw.line(
            screen,
            (52, 60, 74),
            (divider_x, 12),
            (divider_x, config.TOP_BAR_HEIGHT - 14),
            1
        )

    def draw_title_block(self, screen):
        title_shadow = self.title_font.render("DUNGEON DEFENSE", True, (0, 0, 0))
        title = self.title_font.render("DUNGEON DEFENSE", True, (240, 243, 248))

        screen.blit(title_shadow, (31, 21))
        screen.blit(title, (26, 18))

        subtitle = self.subtitle_font.render(
            "Arcane command. Tactical defense. Endless pressure.",
            True,
            (180, 188, 200),
        )
        screen.blit(subtitle, (28, 60))

        pygame.draw.line(screen, (92, 152, 255), (28, 92), (340, 92), 2)

    def draw_card_frame(self, screen, x, y, w, h):
        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 80), shadow.get_rect(), border_radius=14)
        screen.blit(shadow, (x, y + 4))

        pygame.draw.rect(screen, (14, 18, 24), (x, y, w, h), border_radius=14)
        pygame.draw.rect(screen, (28, 34, 44), (x + 2, y + 2, w - 4, h - 4), border_radius=14)
        pygame.draw.rect(screen, (92, 108, 130), (x, y, w, h), 2, border_radius=14)

        pygame.draw.line(screen, (255, 255, 255, 26), (x + 14, y + 12), (x + w - 14, y + 12), 1)

        corner = 10
        color = (106, 160, 255)

        pygame.draw.line(screen, color, (x + 10, y + 10), (x + 10 + corner, y + 10), 2)
        pygame.draw.line(screen, color, (x + 10, y + 10), (x + 10, y + 10 + corner), 2)

        pygame.draw.line(screen, color, (x + w - 10, y + 10), (x + w - 10 - corner, y + 10), 2)
        pygame.draw.line(screen, color, (x + w - 10, y + 10), (x + w - 10, y + 10 + corner), 2)

    def draw_stat_card(self, screen, x, y, w, h, label, value, value_color=None):
        value_color = value_color or config.TEXT_COLOR
        self.draw_card_frame(screen, x, y, w, h)

        label_surface = self.card_label_font.render(label, True, (172, 180, 194))
        value_surface = self.card_value_font.render(str(value), True, value_color)

        screen.blit(label_surface, (x + 14, y + 15))
        screen.blit(value_surface, (x + 14, y + 37))

    def draw_top_stat_cards(self, screen):
        y = 12
        h = 78
        stat_zone_x = self.left_zone_width + self.header_padding
        stat_zone_w = config.MAP_WIDTH - stat_zone_x - self.header_padding

        cards = [
            ("GOLD", self.game_state.gold, (255, 205, 92)),
            ("CORE HP", self.game_state.base_hp, config.TEXT_COLOR),
            ("WAVE", self.game_state.wave, config.TEXT_COLOR),
            ("MAP", self.game_state.current_map_index, (106, 160, 255)),
        ]

        card_count = len(cards)
        total_gap = self.card_gap * (card_count - 1)
        w = (stat_zone_w - total_gap) // card_count

        # กันไม่ให้แคบหรือกว้างเกิน
        w = max(108, min(w, 132))

        total_cards_width = card_count * w + total_gap
        start_x = stat_zone_x + max(0, (stat_zone_w - total_cards_width) // 2)

        for i, (label, value, color) in enumerate(cards):
            x = start_x + i * (w + self.card_gap)
            self.draw_stat_card(screen, x, y, w, h, label, value, color)

    def draw_status_strip(self, screen):
        strip_y = 96
        stat_zone_x = self.left_zone_width + self.header_padding
        stat_zone_w = config.MAP_WIDTH - stat_zone_x - self.header_padding

        strip_x = stat_zone_x
        strip_w = stat_zone_w

        pygame.draw.rect(screen, (10, 12, 18), (strip_x, strip_y, strip_w, 18), border_radius=9)
        pygame.draw.rect(screen, (72, 86, 106), (strip_x, strip_y, strip_w, 18), 1, border_radius=9)

        path_ok = getattr(self.game_state, "path_is_valid", False)
        path_text = "PATH VALID" if path_ok else "PATH INVALID"
        path_color = config.SUCCESS_COLOR if path_ok else config.DANGER_COLOR

        wave_active = getattr(self.game_state, "wave_active", False)
        wave_text = "WAVE ACTIVE" if wave_active else "WAVE IDLE"
        wave_color = config.SUCCESS_COLOR if wave_active else config.SUBTEXT_COLOR

        enemies_alive = getattr(self.game_state, "enemies_alive", 0)

        parts = [
            (f"ENEMIES {enemies_alive}", config.TEXT_COLOR),
            ("•", config.SUBTEXT_COLOR),
            (wave_text, wave_color),
            ("•", config.SUBTEXT_COLOR),
            (path_text, path_color),
        ]

        x = strip_x + 12
        for text, color in parts:
            surf = self.status_font.render(text, True, color)
            screen.blit(surf, (x, strip_y + 1))
            x += surf.get_width() + 12

    def draw_end_status(self, screen):
        if self.game_state.game_over:
            status = self.small_font.render("THE DUNGEON HAS FALLEN", True, config.DANGER_COLOR)
            rect = status.get_rect(right=config.MAP_WIDTH - 18, top=98)
            screen.blit(status, rect)
        elif self.game_state.victory:
            status = self.small_font.render("VICTORY", True, config.SUCCESS_COLOR)
            rect = status.get_rect(right=config.MAP_WIDTH - 18, top=98)
            screen.blit(status, rect)

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_title_block(screen)
        self.draw_top_stat_cards(screen)
        self.draw_status_strip(screen)
        self.draw_end_status(screen)