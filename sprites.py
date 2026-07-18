import pygame
import random
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load your avatar
        try:
            self.image = pygame.image.load("assets/images/player_default.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 120))
        except:
            self.image = pygame.Surface((60, 100))
            self.image.fill((0, 255, 0))
            
        self.rect = self.image.get_rect()
        self.lane = 1
        self.rect.center = (LANES[self.lane], HEIGHT - 100)
        
        # Vertical movement (Jumping)
        self.vel_y = 0
        self.is_jumping = False
        self.ground_y = HEIGHT - 100

    def update(self):
        # Lane switching logic
        target_x = LANES[self.lane]
        self.rect.centerx += (target_x - self.rect.centerx) * 0.2

        # Gravity/Jumping logic
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom > self.ground_y + 60: # Keep feet on ground
            self.rect.bottom = self.ground_y + 60
            self.vel_y = 0
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.vel_y = JUMP_STRENGTH
            self.is_jumping = True

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((70, 50))
        self.image.fill((200, 0, 0)) # Red obstacles (Bugs)
        self.rect = self.image.get_rect()
        self.rect.center = (random.choice(LANES), -50)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        pygame.draw.circle(self.image, GOLD, (15, 15), 15)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (random.choice(LANES), -50)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()