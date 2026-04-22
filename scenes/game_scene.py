# scenes/game_scene.py

from core.game import Game


class GameScene:
    def __init__(self, scene_manager, screen):
        self.scene_manager = scene_manager

        # ใช้ Game เดิมของนาย
        self.game = Game()

        # บังคับให้ Game ใช้ screen เดียวกับ app หลัก
        self.game.screen = screen

    def handle_events(self, events):
        for event in events:
            self.game.side_panel.handle_event(event)

            if event.type == event.__class__.__module__:
                pass

        # ส่ง events เข้า game แบบเดิม
        import pygame

        for event in events:
            if event.type == pygame.QUIT:
                self.game.game_state.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.game_state.running = False

                elif event.key == pygame.K_p:
                    self.game.game_state.is_paused = not self.game.game_state.is_paused

                elif event.key == pygame.K_g:
                    self.game.game_state.show_grid = not self.game.game_state.show_grid

                elif event.key == pygame.K_o:
                    self.game.game_state.show_debug_overlay = (
                        not self.game.game_state.show_debug_overlay
                    )

                elif event.key == pygame.K_l:
                    self.game.game_state.show_cell_labels = (
                        not self.game.game_state.show_cell_labels
                    )

                elif event.key == pygame.K_k:
                    self.game.game_state.show_path_visual = (
                        not self.game.game_state.show_path_visual
                    )

                elif event.key == pygame.K_SPACE:
                    if (
                        self.game.path_is_valid
                        and not self.game.game_state.game_over
                        and not self.game.game_state.victory
                    ):
                        self.game.wave_manager.start_wave()

                elif event.key == pygame.K_r:
                    from scenes.game_scene import GameScene
                    self.scene_manager.set_scene(GameScene(self.scene_manager, self.game.screen))

                elif event.key == pygame.K_1:
                    self.game.game_state.selected_tower_type = "basic"
                    self.game.game_state.placing_mode = True
                    self.game.game_state.selected_tower = None

                elif event.key == pygame.K_2:
                    self.game.game_state.selected_tower_type = "stun"
                    self.game.game_state.placing_mode = True
                    self.game.game_state.selected_tower = None

                elif event.key == pygame.K_3:
                    self.game.game_state.selected_tower_type = "sniper"
                    self.game.game_state.placing_mode = True
                    self.game.game_state.selected_tower = None

                elif event.key == pygame.K_4:
                    self.game.game_state.selected_tower_type = "multi"
                    self.game.game_state.placing_mode = True
                    self.game.game_state.selected_tower = None

                elif event.key == pygame.K_q:
                    self.game.game_state.placing_mode = False

                elif event.key == pygame.K_u:
                    tower = self.game.game_state.selected_tower
                    if (
                        tower
                        and tower.level == 1
                        and self.game.game_state.gold >= self.game.upgrade_cost
                    ):
                        tower.upgrade()
                        self.game.game_state.gold -= self.game.upgrade_cost

                elif event.key == pygame.K_x:
                    tower = self.game.game_state.selected_tower
                    if tower:
                        self.game.game_state.gold += tower.get_sell_value()
                        if tower in self.game.towers:
                            self.game.towers.remove(tower)
                        self.game.game_state.selected_tower = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    cell = self.game.current_map.pixel_to_cell(mx, my)

                    if cell is None:
                        continue

                    row, col = cell

                    if self.game.game_state.placing_mode:
                        self.game.place_tower(row, col)
                    else:
                        self.game.game_state.selected_tower = None
                        for tower in self.game.towers:
                            if tower.row == row and tower.col == col:
                                self.game.game_state.selected_tower = tower
                                break

        # ถ้าในเกมกด ESC แล้ว game_state.running=False ให้กลับหน้า start
        if not self.game.game_state.running:
            from scenes.start_scene import StartScene
            self.scene_manager.set_scene(StartScene(self.scene_manager, self.game.screen))

    def update(self, dt):
        self.game.update(dt)

    def draw(self, screen):
        self.game.draw()