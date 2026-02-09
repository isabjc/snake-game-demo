import pygame
import random

class Food:
    def __init__(self, width, height, cell) -> None:
        self.width = width
        self.height = height
        self.cell = cell
        self.x = 0
        self.y = 0

    def respawn(self, snake_segments):
        max_x = (self.width // self.cell) - 1
        max_y = (self.height // self.cell) - 1
        
        while True:
            self.x = random.randint(0, max_x) * self.cell
            self.y = random.randint(0, max_y) * self.cell
            # Ensure the food does not spawn on the snake's body
            if all(seg.x != self.x or seg.y != self.y for seg in snake_segments):
                break

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.cell, self.cell))
