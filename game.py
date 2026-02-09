import pygame

from direction import Direction
from food import Food
from snake import Snake


class Game:
    def __init__(self) -> None:
        pygame.init()

        self.width = 800
        self.height = 700
        self.cell = 40

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game 🐍")

        # fonts (mononoki)
        self.font = pygame.font.Font("fonts/mononoki-Regular.ttf", 24)
        self.big_font = pygame.font.Font("fonts/mononoki-Bold.ttf", 56)

        # auto pilot
        self.auto_pilot = False

        # score
        self.score = 0

        # states: "menu", "playing", "game_over"
        self.state = "menu"

        # start button rectangle
        self.start_button = pygame.Rect(0, 0, 240, 80)
        self.start_button.center = (self.width // 2, self.height // 2 + 40)

        # game objects
        self.snake = Snake(self.cell)
        self.food = Food(self.width, self.height, self.cell)
        self.food.respawn(self.snake.segments)

    def reset_game(self):
        self.score = 0
        self.auto_pilot = False
        self.snake = Snake(self.cell)
        self.food = Food(self.width, self.height, self.cell)
        self.food.respawn(self.snake.segments)

    def run(self):
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # ---------- MENU INPUT ----------
                if self.state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.start_button.collidepoint(event.pos):
                            self.reset_game()
                            self.state = "playing"

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.state = "playing"

                # ---------- PLAYING INPUT ----------
                elif self.state == "playing":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.snake.try_set_direction(Direction.UP)
                        elif event.key == pygame.K_DOWN:
                                self.snake.try_set_direction(Direction.DOWN)
                        elif event.key == pygame.K_LEFT:
                            self.snake.try_set_direction(Direction.LEFT)
                        elif event.key == pygame.K_RIGHT:
                            self.snake.try_set_direction(Direction.RIGHT)
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "menu"
                        elif event.key == pygame.K_a:
                            self.auto_pilot = not self.auto_pilot

                # ---------- GAME OVER INPUT ----------
                elif self.state == "game_over":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.state = "menu"

            # ---------- UPDATE + DRAW ----------
            if self.state == "menu":
                self.draw_menu()

            elif self.state == "playing":
                try:
                    if self.auto_pilot:
                        self.snake.set_direction_autopilot(
                            self.food, self.width, self.height, self.cell
                        )

                    ate_food = self.snake.update(self.food, self.width, self.height)
                    if ate_food:
                        self.score += 1

                    self.draw()
                except Exception:
                    self.state = "game_over"

            elif self.state == "game_over":
                self.display_game_over()

            clock.tick(10)

        pygame.quit()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.food.draw(self.screen)
        self.snake.draw(self.screen)
        self.draw_hud()
        pygame.display.flip()

    def draw_hud(self):
        score_surface = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surface, (10, 10))

        mode = "AUTO (A to toggle)" if self.auto_pilot else "MANUAL (A to toggle)"
        mode_surface = self.font.render(mode, True, (200, 200, 200))
        self.screen.blit(mode_surface, (10, 40))

    def draw_menu(self):
        self.screen.fill((0, 0, 0))

        mouse_pos = pygame.mouse.get_pos()
        hovering = self.start_button.collidepoint(mouse_pos)

        if hovering:
            button_color = (0, 180, 0)      # green
            text_color = (255, 255, 255)    # white
        else:
            button_color = (255, 255, 255)  # white
            text_color = (0, 0, 0)          # black

        title = self.big_font.render("Snake Game 🐍", True, (255, 255, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 140))

        subtitle = self.font.render("Click Start or press Enter", True, (200, 200, 200))
        self.screen.blit(
            subtitle,
            (self.width // 2 - subtitle.get_width() // 2, 220),
        )

        hint = self.font.render("Press A in-game to toggle autopilot", True, (200, 200, 200))
        self.screen.blit(
            hint,
            (self.width // 2 - hint.get_width() // 2, 255),
        )

        pygame.draw.rect(self.screen, button_color, self.start_button, border_radius=14)

        button_text = self.font.render("Start", True, text_color)
        self.screen.blit(
            button_text,
            (
                self.start_button.centerx - button_text.get_width() // 2,
                self.start_button.centery - button_text.get_height() // 2,
            ),
        )

        pygame.display.flip()

    def display_game_over(self):
        self.screen.fill((0, 0, 0))

        text = self.font.render(
            "Game Over. Press SPACE to go to menu.", True, (255, 255, 255)
        )
        self.screen.blit(
            text,
            (self.width // 2 - text.get_width() // 2, self.height // 2 - 30),
        )

        score_text = self.font.render(
            f"Final Score: {self.score}", True, (200, 200, 200)
        )
        self.screen.blit(
            score_text,
            (self.width // 2 - score_text.get_width() // 2, self.height // 2 + 10),
        )

        pygame.display.flip()
