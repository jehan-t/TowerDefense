# scenes/start_scene.py

import os
import sys
import math
import subprocess
import pygame
import config
from scenes.game_scene import GameScene


class StartScene:
    def __init__(self, scene_manager, screen):
        self.scene_manager = scene_manager
        self.screen = screen

        self.title_font = pygame.font.SysFont("timesnewroman", 78, bold=True)
        self.subtitle_font = pygame.font.SysFont("arial", 22, bold=True)
        self.button_font = pygame.font.SysFont("arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("arial", 16, bold=True)
        self.version_font = pygame.font.SysFont("arial", 14)

        self.start_button = pygame.Rect(0, 0, 330, 72)
        self.stats_button = pygame.Rect(0, 0, 330, 72)
        self.quit_button = pygame.Rect(0, 0, 330, 72)

        self.time_acc = 0.0
        self.bg_image = None

        self.load_assets()
        self.layout_buttons()

    def load_assets(self):
        bg_path = "assets/images/ui/start_bg.png"
        if os.path.exists(bg_path):
            image = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.scale(
                image,
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
            )

    def layout_buttons(self):
        center_x = config.SCREEN_WIDTH // 2
        self.start_button.center = (center_x, config.SCREEN_HEIGHT // 2 + 58)
        self.stats_button.center = (center_x, config.SCREEN_HEIGHT // 2 + 152)
        self.quit_button.center = (center_x, config.SCREEN_HEIGHT // 2 + 246)

    def start_game(self):
        self.scene_manager.set_scene(GameScene(self.scene_manager, self.screen))

    def open_stats_dashboard(self):
        try:
            subprocess.Popen(
                [sys.executable, "-m", "analytics_ui.app"],
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
        except Exception as e:
            print(f"[WARN] Failed to open stats dashboard: {e}")

    def quit_game(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.start_game()
                elif event.key == pygame.K_s:
                    self.open_stats_dashboard()
                elif event.key == pygame.K_ESCAPE:
                    self.quit_game()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.start_button.collidepoint(event.pos):
                        self.start_game()
                    elif self.stats_button.collidepoint(event.pos):
                        self.open_stats_dashboard()
                    elif self.quit_button.collidepoint(event.pos):
                        self.quit_game()

    def update(self, dt):
        self.time_acc += dt

    def draw_background(self):
        if self.bg_image is not None:
            self.screen.blit(self.bg_image, (0, 0))
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            self.screen.blit(overlay, (0, 0))
        else:
            self.screen.fill((7, 8, 12))

            top = pygame.Rect(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT // 2)
            bottom = pygame.Rect(0, config.SCREEN_HEIGHT // 2, config.SCREEN_WIDTH, config.SCREEN_HEIGHT // 2)

            pygame.draw.rect(self.screen, (13, 15, 22), top)
            pygame.draw.rect(self.screen, (7, 8, 12), bottom)

            blue_glow = pygame.Surface((720, 720), pygame.SRCALPHA)
            pygame.draw.circle(blue_glow, (65, 110, 255, 24), (360, 360), 360)
            self.screen.blit(blue_glow, (-220, -180))

            red_glow = pygame.Surface((640, 640), pygame.SRCALPHA)
            pygame.draw.circle(red_glow, (145, 32, 48, 18), (320, 320), 320)
            self.screen.blit(red_glow, (config.SCREEN_WIDTH - 420, -100))

            center_glow = pygame.Surface((520, 520), pygame.SRCALPHA)
            pygame.draw.circle(center_glow, (110, 170, 255, 14), (260, 260), 260)
            self.screen.blit(center_glow, (config.SCREEN_WIDTH // 2 - 260, 120))

        vignette = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (0, 0, 0, 80), (0, 0, config.SCREEN_WIDTH, 90))
        pygame.draw.rect(vignette, (0, 0, 0, 95), (0, config.SCREEN_HEIGHT - 120, config.SCREEN_WIDTH, 120))
        pygame.draw.rect(vignette, (0, 0, 0, 60), (0, 0, 90, config.SCREEN_HEIGHT))
        pygame.draw.rect(vignette, (0, 0, 0, 60), (config.SCREEN_WIDTH - 90, 0, 90, config.SCREEN_HEIGHT))
        self.screen.blit(vignette, (0, 0))

    def draw_frame(self):
        outer = pygame.Rect(96, 88, config.SCREEN_WIDTH - 192, config.SCREEN_HEIGHT - 176)
        inner = outer.inflate(-18, -18)

        pygame.draw.rect(self.screen, (22, 25, 34), outer, border_radius=26)
        pygame.draw.rect(self.screen, (0, 0, 0), outer, 3, border_radius=26)
        pygame.draw.rect(self.screen, (52, 64, 84), inner, 2, border_radius=22)

        marks = [
            (outer.left + 18, outer.top + 18),
            (outer.right - 18, outer.top + 18),
            (outer.left + 18, outer.bottom - 18),
            (outer.right - 18, outer.bottom - 18),
        ]
        for mx, my in marks:
            pygame.draw.circle(self.screen, (90, 145, 255), (mx, my), 4)

    def draw_title_block(self):
        center_x = config.SCREEN_WIDTH // 2
        pulse = 1.0 + 0.01 * math.sin(self.time_acc * 2.0)

        title_surface = self.title_font.render("TOWER DEFENSE", True, (236, 240, 248))
        title_surface = pygame.transform.smoothscale(
            title_surface,
            (
                int(title_surface.get_width() * pulse),
                int(title_surface.get_height() * pulse),
            )
        )
        title_rect = title_surface.get_rect(center=(center_x, 198))

        glow = pygame.Surface((title_rect.width + 180, title_rect.height + 70), pygame.SRCALPHA)
        pygame.draw.rect(glow, (80, 135, 255, 34), glow.get_rect(), border_radius=40)
        self.screen.blit(glow, (title_rect.x - 90, title_rect.y - 35))

        shadow = title_surface.copy()
        shadow.fill((0, 0, 0, 175), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(shadow, (title_rect.x + 4, title_rect.y + 4))
        self.screen.blit(title_surface, title_rect)

        subtitle = self.subtitle_font.render(
            "DESCEND. DEFEND. DOMINATE THE DUNGEON.",
            True,
            (188, 196, 210),
        )
        subtitle_rect = subtitle.get_rect(center=(center_x, 268))
        self.screen.blit(subtitle, subtitle_rect)

        line_width = 500
        line_x = center_x - line_width // 2
        line_y = 304
        pygame.draw.line(self.screen, (92, 152, 255), (line_x, line_y), (line_x + line_width, line_y), 2)

    def draw_button(self, rect, text, primary=False, secondary=False):
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        if primary:
            fill = (32, 68, 130) if not hovered else (54, 98, 184)
            glow_color = (70, 120, 255, 65)
        elif secondary:
            fill = (48, 56, 86) if not hovered else (72, 86, 126)
            glow_color = (110, 145, 255, 42)
        else:
            fill = (34, 38, 48) if not hovered else (52, 58, 72)
            glow_color = (170, 176, 190, 32)

        draw_rect = rect.copy()
        if hovered:
            draw_rect.inflate_ip(8, 4)
            draw_rect.y -= 2

        glow = pygame.Surface((draw_rect.width + 26, draw_rect.height + 26), pygame.SRCALPHA)
        pygame.draw.rect(glow, glow_color, glow.get_rect(), border_radius=22)
        self.screen.blit(glow, (draw_rect.x - 13, draw_rect.y - 13))

        shadow = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 95), shadow.get_rect(), border_radius=18)
        self.screen.blit(shadow, (draw_rect.x, draw_rect.y + 6))

        surface = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, fill, surface.get_rect(), border_radius=18)
        pygame.draw.rect(surface, (218, 223, 232), surface.get_rect(), 2, border_radius=18)
        pygame.draw.line(surface, (255, 255, 255, 50), (18, 12), (draw_rect.width - 18, 12), 2)
        self.screen.blit(surface, draw_rect.topleft)

        text_surf = self.button_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=draw_rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_footer(self):
        footer = self.small_font.render("ENTER = START   •   S = STATS   •   ESC = QUIT", True, (185, 192, 205))
        self.screen.blit(footer, (28, config.SCREEN_HEIGHT - 30))

        mid = self.version_font.render("Analytics Dashboard available from menu", True, (120, 145, 180))
        mid_rect = mid.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 25))
        self.screen.blit(mid, mid_rect)

        version = self.version_font.render("Dungeon Build Prototype v0.1", True, (142, 148, 160))
        version_rect = version.get_rect(bottomright=(config.SCREEN_WIDTH - 18, config.SCREEN_HEIGHT - 10))
        self.screen.blit(version, version_rect)

    def draw(self, screen):
        self.draw_background()
        self.draw_frame()
        self.draw_title_block()
        self.draw_button(self.start_button, "Start Game", primary=True)
        self.draw_button(self.stats_button, "Stats Dashboard", secondary=True)
        self.draw_button(self.quit_button, "Quit", primary=False)
        self.draw_footer()