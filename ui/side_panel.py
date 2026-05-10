# ui/side_panel.py

import pygame
import config
from utils.button import Button


class SidePanel:
    def __init__(self, game_state):
        self.game_state = game_state

        self.title_font = pygame.font.SysFont("timesnewroman", 28, bold=True)
        self.subtitle_font = pygame.font.SysFont("arial", 14, bold=True)
        self.section_font = pygame.font.SysFont("arial", 20, bold=True)
        self.text_font = pygame.font.SysFont("arial", 16)
        self.small_font = pygame.font.SysFont("arial", 13, bold=True)
        self.button_font = pygame.font.SysFont("arial", 17, bold=True)

        self.padding_x = 18
        self.card_padding = 16
        self.card_gap = 18
        self.panel_inner_width = config.PANEL_WIDTH - self.padding_x * 2

        self.buttons = []
        self.create_buttons()

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def select_tower(self, tower_type):
        self.game_state.selected_tower_type = tower_type
        self.game_state.placing_mode = True
        self.game_state.selected_tower = None

    def upgrade_selected(self):
        self.game_state.request_upgrade_selected = True

    def sell_selected(self):
        tower = self.game_state.selected_tower
        if tower:
            self.game_state.gold += tower.get_sell_value()
            if hasattr(self.game_state, "towers") and tower in self.game_state.towers:
                self.game_state.towers.remove(tower)
            self.game_state.selected_tower = None

    def create_buttons(self):
        self.btn_basic = Button((0, 0, 100, 42), "Basic", lambda: self.select_tower("basic"), self.button_font)
        self.btn_stun = Button((0, 0, 100, 42), "Stun", lambda: self.select_tower("stun"), self.button_font)
        self.btn_sniper = Button((0, 0, 100, 42), "Sniper", lambda: self.select_tower("sniper"), self.button_font)
        self.btn_multi = Button((0, 0, 100, 42), "Multi", lambda: self.select_tower("multi"), self.button_font)

        self.btn_upgrade = Button(
            (0, 0, 100, 46),
            "Upgrade",
            self.upgrade_selected,
            self.button_font,
            bg=(42, 80, 146),
            hover=(62, 108, 190),
        )
        self.btn_sell = Button(
            (0, 0, 100, 46),
            "Sell",
            self.sell_selected,
            self.button_font,
            bg=(112, 50, 50),
            hover=(166, 70, 70),
        )

        self.buttons = [
            self.btn_basic,
            self.btn_stun,
            self.btn_sniper,
            self.btn_multi,
            self.btn_upgrade,
            self.btn_sell,
        ]

    def draw_panel_background(self, screen):
        pygame.draw.rect(
            screen,
            (8, 10, 15),
            (config.PANEL_X, config.PANEL_Y, config.PANEL_WIDTH, config.PANEL_HEIGHT)
        )

        pygame.draw.rect(
            screen,
            (12, 15, 22),
            (config.PANEL_X + 2, 0, config.PANEL_WIDTH - 2, config.SCREEN_HEIGHT)
        )

        pygame.draw.line(
            screen,
            (78, 90, 108),
            (config.PANEL_X, 0),
            (config.PANEL_X, config.SCREEN_HEIGHT),
            2
        )

        shade = pygame.Surface((config.PANEL_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 24))
        screen.blit(shade, (config.PANEL_X, 0))

        glow = pygame.Surface((config.PANEL_WIDTH, 110), pygame.SRCALPHA)
        pygame.draw.rect(glow, (72, 126, 255, 22), glow.get_rect(), border_radius=18)
        screen.blit(glow, (config.PANEL_X, 6))

    def draw_header(self, screen):
        x = config.PANEL_X + self.padding_x
        y = 18

        shadow = self.title_font.render("Arcane Console", True, (0, 0, 0))
        title = self.title_font.render("Arcane Console", True, (240, 243, 248))

        screen.blit(shadow, (x + 2, y + 2))
        screen.blit(title, (x, y))

        sub = self.subtitle_font.render(
            "Manage towers, upgrades, and tactical control",
            True,
            (176, 184, 198),
        )
        screen.blit(sub, (x, y + 34))

        pygame.draw.line(
            screen,
            (80, 94, 116),
            (config.PANEL_X + 14, 76),
            (config.PANEL_X + config.PANEL_WIDTH - 14, 76),
            1
        )

    def draw_card(self, screen, x, y, w, h, title):
        # shadow
        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 88), shadow.get_rect(), border_radius=16)
        screen.blit(shadow, (x, y + 6))

        # outer body
        pygame.draw.rect(screen, (12, 15, 22), (x, y, w, h), border_radius=16)

        # inner body
        pygame.draw.rect(screen, (24, 30, 40), (x + 2, y + 2, w - 4, h - 4), border_radius=16)

        # border
        pygame.draw.rect(screen, (86, 100, 122), (x, y, w, h), 2, border_radius=16)

        # title line
        pygame.draw.line(screen, (255, 255, 255, 24), (x + 18, y + 46), (x + w - 18, y + 46), 1)

        # glow band behind title
        title_glow = pygame.Surface((w - 20, 40), pygame.SRCALPHA)
        pygame.draw.rect(title_glow, (72, 126, 255, 18), title_glow.get_rect(), border_radius=12)
        screen.blit(title_glow, (x + 10, y + 8))

        # title
        title_shadow = self.section_font.render(title, True, (0, 0, 0))
        title_surface = self.section_font.render(title, True, (106, 160, 255))
        screen.blit(title_shadow, (x + 15, y + 13))
        screen.blit(title_surface, (x + 14, y + 12))

        # corner accents
        c = (106, 160, 255)
        s = 10
        pygame.draw.line(screen, c, (x + 10, y + 10), (x + 10 + s, y + 10), 2)
        pygame.draw.line(screen, c, (x + 10, y + 10), (x + 10, y + 10 + s), 2)
        pygame.draw.line(screen, c, (x + w - 10, y + 10), (x + w - 10 - s, y + 10), 2)
        pygame.draw.line(screen, c, (x + w - 10, y + 10), (x + w - 10, y + 10 + s), 2)

    def layout_two_column_buttons(self, left_button, right_button, x, y, total_width, height=42, gap=12):
        button_width = (total_width - gap) // 2
        left_button.rect = pygame.Rect(x, y, button_width, height)
        right_button.rect = pygame.Rect(x + button_width + gap, y, button_width, height)

    def draw_shop_card(self, screen, x, y):
        w = self.panel_inner_width
        h = 252
        self.draw_card(screen, x, y, w, h, "Tower Forge")

        content_x = x + self.card_padding
        content_w = w - self.card_padding * 2

        selected_type = self.game_state.selected_tower_type
        selected_type = str(selected_type).title() if selected_type is not None else "-"

        info_1 = self.small_font.render(f"Selected Type: {selected_type}", True, (176, 184, 198))
        info_2 = self.small_font.render("Hotkeys: 1 / 2 / 3 / 4", True, (176, 184, 198))
        info_3 = self.small_font.render("Choose a tower and place it on build cells", True, (176, 184, 198))

        screen.blit(info_1, (content_x, y + 60))
        screen.blit(info_2, (content_x, y + 84))
        screen.blit(info_3, (content_x, y + 108))

        row1_y = y + 140
        row2_y = y + 196

        self.layout_two_column_buttons(self.btn_basic, self.btn_stun, content_x, row1_y, content_w, 44, 12)
        self.layout_two_column_buttons(self.btn_sniper, self.btn_multi, content_x, row2_y, content_w, 44, 12)

        return y + h

    def draw_selected_card(self, screen, x, y):
        w = self.panel_inner_width
        h = 360
        self.draw_card(screen, x, y, w, h, "Selected Tower")

        content_x = x + self.card_padding
        content_w = w - self.card_padding * 2

        tower = self.game_state.selected_tower

        if tower is None:
            line1 = self.text_font.render("No tower selected", True, (240, 243, 248))
            line2 = self.small_font.render("Click a placed tower to inspect it", True, (176, 184, 198))
            screen.blit(line1, (content_x, y + 62))
            screen.blit(line2, (content_x, y + 90))

            btn_y = y + h - 62
            self.layout_two_column_buttons(self.btn_upgrade, self.btn_sell, content_x, btn_y, content_w, 46, 12)
            self.btn_upgrade.enabled = False
            self.btn_sell.enabled = False
            return y + h

        info_lines = [
            ("TYPE", str(tower.type).title()),
            ("LEVEL", tower.level),
            ("DAMAGE", int(tower.damage)),
            ("RANGE", int(tower.range)),
            ("FIRE RATE", f"{tower.fire_rate:.2f}"),
            ("SELL VALUE", tower.get_sell_value()),
        ]

        info_y = y + 62
        for label, value in info_lines:
            label_surface = self.small_font.render(label, True, (176, 184, 198))
            value_surface = self.text_font.render(str(value), True, (240, 243, 248))

            screen.blit(label_surface, (content_x, info_y))
            screen.blit(value_surface, (content_x + 160, info_y - 2))
            info_y += 32

        footer = self.small_font.render(
            "Upgrade is available once per tower",
            True,
            (176, 184, 198)
        )
        screen.blit(footer, (content_x, y + h - 98))

        btn_y = y + h - 62
        self.layout_two_column_buttons(self.btn_upgrade, self.btn_sell, content_x, btn_y, content_w, 46, 12)

        self.btn_upgrade.enabled = tower.level == 1 and self.game_state.gold >= 100
        self.btn_sell.enabled = True

        return y + h

    def draw_footer_note(self, screen):
        note = self.small_font.render(
            "Tip: Upgrade wisely before boss waves",
            True,
            (170, 178, 192),
        )
        note_rect = note.get_rect(
            bottomleft=(config.PANEL_X + self.padding_x, config.SCREEN_HEIGHT - config.BOTTOM_BAR_HEIGHT - 12)
        )
        screen.blit(note, note_rect)

    def draw(self, screen):
        self.draw_panel_background(screen)
        self.draw_header(screen)

        x = config.PANEL_X + self.padding_x
        shop_bottom = self.draw_shop_card(screen, x, 94)
        self.draw_selected_card(screen, x, shop_bottom + self.card_gap)
        self.draw_footer_note(screen)

        for btn in self.buttons:
            btn.draw(screen)