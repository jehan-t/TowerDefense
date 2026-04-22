# map_editor.py

import os
import pygame
import config
from maps.map_loader import load_map_json, save_map_json, create_empty_grid


class MapEditor:
    def __init__(self, map_json_path):
        pygame.init()
        pygame.display.set_caption("Map Editor")
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.text_font = pygame.font.SysFont("arial", 18)
        self.small_font = pygame.font.SysFont("arial", 16)

        self.map_json_path = map_json_path
        self.map_data = load_map_json(map_json_path)

        if self.map_data is None:
            raise FileNotFoundError(f"Map JSON not found: {map_json_path}")

        self.map_name = self.map_data["map_name"]
        self.image_path = self.map_data["image_path"]
        self.grid = self.map_data.get("grid", create_empty_grid())

        self.selected_tile_type = config.PATH
        self.running = True

        self.background_image = self.load_background_image(self.image_path)

    def load_background_image(self, image_path):
        if not os.path.exists(image_path):
            surface = pygame.Surface((config.MAP_WIDTH, config.MAP_HEIGHT))
            surface.fill((70, 70, 70))
            return surface

        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (config.MAP_WIDTH, config.MAP_HEIGHT))
        return image

    def get_tile_name(self, tile_id):
        names = {
            config.EMPTY: "EMPTY",
            config.PATH: "PATH",
            config.BUILDABLE: "BUILDABLE",
            config.SPAWN: "SPAWN",
            config.BASE: "BASE",
            config.BLOCKED: "BLOCKED",
        }
        return names.get(tile_id, "UNKNOWN")

    def get_mouse_cell(self):
        mx, my = pygame.mouse.get_pos()

        if not (config.MAP_X <= mx < config.MAP_X + config.MAP_WIDTH):
            return None
        if not (config.MAP_Y <= my < config.MAP_Y + config.MAP_HEIGHT):
            return None

        col = (mx - config.MAP_X) // config.TILE_SIZE
        row = (my - config.MAP_Y) // config.TILE_SIZE

        if 0 <= row < config.MAP_ROWS and 0 <= col < config.MAP_COLS:
            return row, col

        return None

    def paint_cell(self, row, col, tile_type):
        self.grid[row][col] = tile_type

    def clear_grid(self):
        self.grid = create_empty_grid()

    def count_tile_type(self, tile_type):
        return sum(row.count(tile_type) for row in self.grid)

    def save_current_map(self):
        save_map_json(
            filepath=self.map_json_path,
            map_name=self.map_name,
            image_path=self.image_path,
            grid=self.grid
        )
        print(f"[SAVED] {self.map_json_path}")

    def handle_keydown(self, event):
        if event.key == pygame.K_0:
            self.selected_tile_type = config.EMPTY
        elif event.key == pygame.K_1:
            self.selected_tile_type = config.PATH
        elif event.key == pygame.K_2:
            self.selected_tile_type = config.BUILDABLE
        elif event.key == pygame.K_3:
            self.selected_tile_type = config.SPAWN
        elif event.key == pygame.K_4:
            self.selected_tile_type = config.BASE
        elif event.key == pygame.K_5:
            self.selected_tile_type = config.BLOCKED

        elif event.key == pygame.K_s:
            self.save_current_map()

        elif event.key == pygame.K_c:
            self.clear_grid()
            print("[CLEARED] Grid reset")

        elif event.key == pygame.K_ESCAPE:
            self.running = False

    def handle_mouse_paint(self):
        cell = self.get_mouse_cell()
        if cell is None:
            return

        row, col = cell

        left_pressed = pygame.mouse.get_pressed()[0]
        right_pressed = pygame.mouse.get_pressed()[2]

        if left_pressed:
            self.paint_cell(row, col, self.selected_tile_type)
        elif right_pressed:
            self.paint_cell(row, col, config.EMPTY)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

    def draw_top_bar(self):
        pygame.draw.rect(
            self.screen,
            config.TOP_BAR_COLOR,
            (0, 0, config.SCREEN_WIDTH, config.TOP_BAR_HEIGHT)
        )

        pygame.draw.line(
            self.screen,
            config.TOP_BAR_BORDER_COLOR,
            (0, config.TOP_BAR_HEIGHT - 1),
            (config.SCREEN_WIDTH, config.TOP_BAR_HEIGHT - 1),
            2
        )

        title = self.font.render(f"Map Editor - {self.map_name}", True, config.TEXT_COLOR)
        self.screen.blit(title, (20, 16))

    def draw_map_area(self):
        self.screen.blit(self.background_image, (config.MAP_X, config.MAP_Y))

        for row in range(config.MAP_ROWS):
            for col in range(config.MAP_COLS):
                x = config.MAP_X + col * config.TILE_SIZE
                y = config.MAP_Y + row * config.TILE_SIZE

                tile_type = self.grid[row][col]
                overlay_color = config.EDITOR_COLORS[tile_type]

                if tile_type != config.EMPTY:
                    overlay = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE), pygame.SRCALPHA)
                    overlay.fill(overlay_color)
                    self.screen.blit(overlay, (x, y))

                pygame.draw.rect(
                    self.screen,
                    config.GRID_COLOR,
                    (x, y, config.TILE_SIZE, config.TILE_SIZE),
                    1
                )

    def draw_hover_highlight(self):
        cell = self.get_mouse_cell()
        if cell is None:
            return

        row, col = cell
        x = config.MAP_X + col * config.TILE_SIZE
        y = config.MAP_Y + row * config.TILE_SIZE

        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (x, y, config.TILE_SIZE, config.TILE_SIZE),
            3
        )

    def draw_side_panel(self):
        pygame.draw.rect(
            self.screen,
            config.SIDE_PANEL_COLOR,
            (config.PANEL_X, config.PANEL_Y, config.PANEL_WIDTH, config.PANEL_HEIGHT)
        )

        pygame.draw.line(
            self.screen,
            config.SIDE_PANEL_BORDER_COLOR,
            (config.PANEL_X, 0),
            (config.PANEL_X, config.SCREEN_HEIGHT),
            2
        )

        x = config.PANEL_X + 20
        y = 20

        title = self.font.render("Editor Panel", True, config.TEXT_COLOR)
        self.screen.blit(title, (x, y))

        y += 55
        subtitle = self.text_font.render("Tile Types", True, config.ACCENT_COLOR)
        self.screen.blit(subtitle, (x, y))

        tile_entries = [
            ("0 = EMPTY", config.EMPTY),
            ("1 = PATH", config.PATH),
            ("2 = BUILDABLE", config.BUILDABLE),
            ("3 = SPAWN", config.SPAWN),
            ("4 = BASE", config.BASE),
            ("5 = BLOCKED", config.BLOCKED),
        ]

        y += 35
        for label, tile_id in tile_entries:
            rgba = config.EDITOR_COLORS[tile_id]
            color_box = (rgba[0], rgba[1], rgba[2])

            pygame.draw.rect(self.screen, color_box, (x, y + 3, 24, 24))
            text = self.text_font.render(label, True, config.TEXT_COLOR)
            self.screen.blit(text, (x + 36, y))
            y += 34

        y += 10
        controls = self.text_font.render("Controls", True, config.ACCENT_COLOR)
        self.screen.blit(controls, (x, y))

        y += 35
        control_lines = [
            "Left Click  = Paint",
            "Right Click = Erase",
            "S = Save JSON",
            "C = Clear Grid",
            "ESC = Exit",
        ]

        for line in control_lines:
            text = self.small_font.render(line, True, config.SUBTEXT_COLOR)
            self.screen.blit(text, (x, y))
            y += 26

        y += 10
        current = self.text_font.render(
            f"Selected: {self.get_tile_name(self.selected_tile_type)}",
            True,
            config.TEXT_COLOR
        )
        self.screen.blit(current, (x, y))

        y += 45
        stats_title = self.text_font.render("Quick Stats", True, config.ACCENT_COLOR)
        self.screen.blit(stats_title, (x, y))

        y += 32
        stats_lines = [
            f"Spawn Count: {self.count_tile_type(config.SPAWN)}",
            f"Base Count: {self.count_tile_type(config.BASE)}",
            f"Path Count: {self.count_tile_type(config.PATH)}",
            f"Buildable Count: {self.count_tile_type(config.BUILDABLE)}",
            f"Blocked Count: {self.count_tile_type(config.BLOCKED)}",
        ]

        for line in stats_lines:
            text = self.small_font.render(line, True, config.TEXT_COLOR)
            self.screen.blit(text, (x, y))
            y += 24

        cell = self.get_mouse_cell()
        y += 20

        if cell is not None:
            row, col = cell
            hover_tile = self.grid[row][col]
            hover_text_1 = self.small_font.render(f"Hover Row: {row}", True, config.TEXT_COLOR)
            hover_text_2 = self.small_font.render(f"Hover Col: {col}", True, config.TEXT_COLOR)
            hover_text_3 = self.small_font.render(
                f"Hover Type: {self.get_tile_name(hover_tile)}",
                True,
                config.TEXT_COLOR
            )
            self.screen.blit(hover_text_1, (x, y))
            self.screen.blit(hover_text_2, (x, y + 24))
            self.screen.blit(hover_text_3, (x, y + 48))

    def draw(self):
        self.screen.fill(config.BG_COLOR)
        self.draw_top_bar()
        self.draw_map_area()
        self.draw_hover_highlight()
        self.draw_side_panel()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(config.FPS)
            self.handle_events()
            self.handle_mouse_paint()
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    # เปลี่ยนเป็น data/maps/map2.json ได้เมื่อต้องการแก้ map2
    editor = MapEditor("data/maps/map1.json")
    editor.run()