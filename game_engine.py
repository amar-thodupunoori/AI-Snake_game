import random
import pygame
import numpy as np
from collections import namedtuple

pygame.init()
font = pygame.font.Font('assets/arial.ttf', 25)
Point = namedtuple('Point', ('x', 'y'))

WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
BLOCK_SIZE = 20


class SnakeGame():
    def __init__(self, w=640, h=480, num_obstacles=10):
        pygame.display.set_caption("Snake")
        self.w, self.h = w, h
        self.display = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()
        self.reset(num_obstacles)

    def reset(self, num_obstacles):
        self.direction = "r"
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head]
        self.score = 0
        self.food = None
        self.obstacles = []
        self.frame_iteration = 0

        # Place obstacles randomly on the board
        for i in range(num_obstacles):
            # Choose random position for top-left corner of rectangle
            x = random.randint(0, (self.w - 4 * BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.h - 4 * BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            
            # Choose random dimensions for rectangle
            w = random.randint(1, 10) * BLOCK_SIZE
            h = random.randint(1, 1) * BLOCK_SIZE
            
            # Add all points in rectangle to obstacles list
            for r in range(x, x+w, BLOCK_SIZE):
                for c in range(y, y+h, BLOCK_SIZE):
                    self.obstacles.append(Point(r, c))

        self.place_food()

    def place_food(self):
        while True:
            x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            self.food = Point(x, y)

            if self.food not in self.snake and self.food not in self.obstacles:
                break

    def play(self, action, speed, episode):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.move(action)
        self.snake.insert(0, self.head)
        self.frame_iteration += 1

        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            reward = -10
            game_over = True
            return reward, game_over

        if self.head == self.food:
            reward = 100
            self.score += 1
            self.place_food()
        else:
            self.snake.pop()

        self.update_ui(episode)
        self.clock.tick(speed)

        return reward, game_over

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head

        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True

        if pt in self.snake[1:] or pt in self.obstacles:
            return True

        return False

    def update_ui(self, episode):
        self.display.fill(BLACK)
        for p in self.obstacles:
            pygame.draw.rect(self.display, WHITE, pygame.Rect(
                p.x, p.y, BLOCK_SIZE, BLOCK_SIZE))
        for p in self.snake:
            pygame.draw.rect(self.display, BLUE, pygame.Rect(
                p.x, p.y, BLOCK_SIZE, BLOCK_SIZE))

        if self.food:
            pygame.draw.rect(self.display, RED, pygame.Rect(
                self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        self.draw_score(episode)
        pygame.display.flip()

    def draw_score(self, episode):
        text = font.render("Score: " + str(self.score) + " | Episode: " + str(episode), True, WHITE)
        self.display.blit(text, [0, 0])


    def move(self, action):
        clock_wise = ["r", "d", "l", "u"]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            new_idx = (idx + 1) % 4
            new_dir = clock_wise[new_idx]
        else:
            new_idx = (idx - 1) % 4
            new_dir = clock_wise[new_idx]

        self.direction = new_dir
        x = self.head.x
        y = self.head.y

        if self.direction == "r":
            x += BLOCK_SIZE
        elif self.direction == "l":
            x -= BLOCK_SIZE
        elif self.direction == "d":
            y += BLOCK_SIZE
        elif self.direction == "u":
            y -= BLOCK_SIZE

        self.head = Point(x, y)
