# core/app.py

import pygame
import config
from core.scene_manager import SceneManager
from scenes.start_scene import StartScene


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.WINDOW_TITLE)

        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        self.running = True

        self.scene_manager = SceneManager()
        self.scene_manager.set_scene(StartScene(self.scene_manager, self.screen))

    def run(self):
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.scene_manager.handle_events(events)
            self.scene_manager.update(dt)
            self.scene_manager.draw(self.screen)

            pygame.display.flip()

        pygame.quit()