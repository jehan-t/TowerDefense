# core/scene_manager.py

class SceneManager:
    def __init__(self):
        self.current_scene = None

    def set_scene(self, scene):
        self.current_scene = scene

    def handle_events(self, events):
        if self.current_scene:
            self.current_scene.handle_events(events)

    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, screen):
        if self.current_scene:
            self.current_scene.draw(screen)