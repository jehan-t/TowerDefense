# utils/button.py

import pygame


class Button:
    def __init__(
        self,
        rect,
        text,
        onclick,
        font,
        bg=(56, 72, 96),
        hover=(78, 102, 140),
        text_color=(255, 255, 255),
        border_color=(220, 220, 220),
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.onclick = onclick
        self.font = font

        self.bg = bg
        self.hover = hover
        self.text_color = text_color
        self.border_color = border_color

        self.enabled = True

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.enabled and self.rect.collidepoint(mouse_pos)

        fill = self.hover if hovered else self.bg
        if not self.enabled:
            fill = (70, 70, 70)

        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        shadow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 70), shadow.get_rect(), border_radius=10)
        screen.blit(shadow, shadow_rect.topleft)

        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, fill, surf.get_rect(), border_radius=10)
        pygame.draw.rect(surf, self.border_color, surf.get_rect(), 2, border_radius=10)
        screen.blit(surf, self.rect.topleft)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if not self.enabled:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if callable(self.onclick):
                    self.onclick()