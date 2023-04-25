import pygame
import random
from gym import Env
from gym.spaces import Discrete, Box
import numpy as np

pygame.init()

screen_width = 864
screen_height = 936

# game variables
pipe_gap = 150
scroll_speed = 2
dist_between_pipes = 300


class Bird(pygame.sprite.Sprite):

    def __init__(self, x, y, game):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/bird{num}.png").convert_alpha()
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.game = game
        self.clicked = False

    def update(self, move=None):

        if self.game.flying:
            # apply gravity
            self.vel += 0.5
            if self.vel > 15:
                self.vel = 15
            if self.vel < -35:
                self.vel = -35
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not self.game.game_over:
            # jump
            if move == 1 and not self.clicked:
                self.clicked = True
                if self.vel <= 0:
                    self.vel -= 15
                self.vel = -10
            if move == 0:
                self.clicked = False

            # handle the animation
            flap_cooldown = 5
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # point the bird at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):

    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png").convert_alpha()
        self.rect = self.image.get_rect()
        # position variable determines if the pipe is coming from the bottom or top
        # position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Game():
    def __init__(self):
        # define game variables
        self.ground_scroll = 0
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Flappy Bird')
        self.game_over = False
        self.last_pipe = dist_between_pipes
        self.score = 0
        self.pass_pipe = False
        self.pipe_group = pygame.sprite.Group()
        pipe_height = random.randint(-200, 200)
        btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
        top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
        self.pipe_group.add(btm_pipe)
        self.pipe_group.add(top_pipe)
        self.bird_group = pygame.sprite.Group()
        self.flappy = Bird(100, int(screen_height / 2), self)
        self.bird_group.add(self.flappy)
        self.flying = True

    def reset_game(self):
        self.ground_scroll = 0
        self.game_over = False
        self.last_pipe = dist_between_pipes
        self.score = 0
        self.pass_pipe = False
        self.pipe_group = pygame.sprite.Group()
        pipe_height = random.randint(-200, 200)
        btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
        top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
        self.pipe_group.add(btm_pipe)
        self.pipe_group.add(top_pipe)
        self.bird_group = pygame.sprite.Group()
        self.flappy = Bird(100, int(screen_height / 2), self)
        self.bird_group.add(self.flappy)
        self.flying = True

    def get_state(self):
        if len(self.pipe_group) > 0:
            bird_y_loc = self.flappy.rect.y
            x_dist_pipe_bird = self.pipe_group.sprites()[0].rect.left - self.flappy.rect.right
            bot_pipe_y_loc = self.pipe_group.sprites()[0].rect.top - bird_y_loc
            top_pipe_y_loc = self.pipe_group.sprites()[1].rect.bottom - bird_y_loc
            return np.array([x_dist_pipe_bird / 500, 10 * bot_pipe_y_loc / screen_height,
                             5 * top_pipe_y_loc / screen_height, self.flappy.vel / 35], dtype=np.float32)
        # shouldn't get here
        return None

    def play_step(self, move):

        self.bird_group.update(move)
        reward = 0.01
        # check the score
        if len(self.pipe_group) > 0:
            if self.bird_group.sprites()[0].rect.left > self.pipe_group.sprites()[0].rect.left \
                    and self.bird_group.sprites()[0].rect.right < self.pipe_group.sprites()[0].rect.right \
                    and not self.pass_pipe:
                self.pass_pipe = True
            if self.pass_pipe:
                if self.bird_group.sprites()[0].rect.left > self.pipe_group.sprites()[0].rect.right:
                    self.score += 1
                    reward = 1
                    self.pass_pipe = False

        # look for collision
        if pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False) \
                or self.flappy.rect.top < 0:
            self.game_over = True
        # once the bird has hit the ground it's game over and no longer flying
        if self.flappy.rect.bottom >= 768:
            self.game_over = True
            self.flying = False

        if self.flying and not self.game_over:
            # generate new pipes
            if self.last_pipe < 0:
                pipe_height = random.randint(-200, 200)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                self.pipe_group.add(btm_pipe)
                self.pipe_group.add(top_pipe)
                self.last_pipe = dist_between_pipes
        self.last_pipe -= scroll_speed
        self.pipe_group.update()

        if abs(self.ground_scroll) > 35 and not self.game_over:
            self.ground_scroll -= scroll_speed
            self.ground_scroll = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        if move == 1 and not self.flying and not self.game_over:
            self.flying = True
        if self.game_over:
            reward = -1
        return self.game_over, self.score, reward


class flappy_env(Env):

    def __init__(self):
        self.game = Game()
        self.observation_space = Box(low=np.array([-0.4, -2.0, -1.0, -1.0], dtype=np.float32),
                                     high=np.array([1.0, 2.0, 1.0, 0.5], dtype=np.float32))
        self.action_space = Discrete(2)

    def step(self, action):
        done, score, reward = self.game.play_step(action)
        state = self.game.get_state()
        info = {}
        return state, reward, done, info

    def render(self):
        pass

    def reset(self):
        self.game.reset_game()
        return self.game.get_state()
