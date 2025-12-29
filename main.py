from pathlib import Path
import pygame
import os
import random
from pygame import mixer

pygame.init()
mixer.init()

FOLDER_ASSETS = Path("assets")

# setup font
font = pygame.font.SysFont("freesansbold", 50)
title_font = pygame.font.SysFont(None, 100)
medium_font = pygame.font.SysFont(None, 75)


# scaler
def scale_img(img, scale_factor):
    new_size = [img.get_width() * scale_factor, img.get_height() * scale_factor]
    return pygame.transform.scale(img, new_size)


# load images
elf_run_1 = scale_img(pygame.image.load(FOLDER_ASSETS / "run1.png"), 2.5)
elf_run_2 = scale_img(pygame.image.load(FOLDER_ASSETS / "run2.png"), 2.5)
elf_stand = scale_img(pygame.image.load(FOLDER_ASSETS / "stand.png"), 2.5)
elf_imgs = [elf_run_1, elf_run_2, elf_stand]

present_imgs = []
for i in range(1, 5):
    present_imgs.append(
        scale_img(pygame.image.load(FOLDER_ASSETS / f"present{i}.png"), 4)
    )
print(len(present_imgs))
print(present_imgs)
# setup screen
FLOOR_HEIGHT = 60
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ELFY")

# setup clock
clock = pygame.time.Clock()
FPS = 60


class Present:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 3

    def draw(self):
        screen.blit(self.img, (self.x, self.y))

    def move(self):
        self.y += self.speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def present_collected(self, otherrect):
        if pygame.Rect.colliderect(self.rect, otherrect):
            return True
        return False

    def is_present_over(self):
        if self.y > HEIGHT:
            return True
        return False


class Elf:
    def __init__(self, x, y, imgs):
        self.x = x
        self.y = y
        self.imgs = imgs
        self.img = self.imgs[2]
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 5

    def draw(self):
        screen.blit(self.img, (self.x, self.y))

    def move(self, keys):
        # keys
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_LEFT]:
            self.x -= self.speed

        # update rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def animate(self, keys):
        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]:
            if self.img == self.imgs[0]:
                self.img = self.imgs[1]
            elif self.img == self.imgs[1]:
                self.img = self.imgs[0]

            elif self.img == self.imgs[2]:
                self.img = self.imgs[0]
        else:
            self.img = self.imgs[2]


def game():
    # variables
    run = True
    animate_timer = 0
    present_timer = 0
    score = 0

    # objects
    player = Elf(0, HEIGHT - elf_imgs[2].get_height(), elf_imgs)
    presents = []

    # main game loop
    while run:
        for event in pygame.event.get():  # loop through all events in passed frame
            if event.type == pygame.QUIT:  # quit if x button pressed
                run = False
                pygame.quit()
                quit()

        # render text
        score_text = title_font.render(f"{score}", True, (0, 0, 0))

        # draw
        screen.fill("white")
        player.draw()
        screen.blit(score_text, (WIDTH / 2 - score_text.get_width() / 2, 50))

        # move
        player.move(pygame.key.get_pressed())

        # animate
        if animate_timer > 1:
            player.animate(pygame.key.get_pressed())
            animate_timer = 0

        # spawn presents
        if present_timer > 1:
            presents.append(
                Present(
                    random.randint(0, WIDTH - present_imgs[0].get_width()),
                    0 - present_imgs[0].get_height(),
                    present_imgs[random.randint(0, 3)],
                )
            )
            present_timer = 0

        # draw presents
        delete_present_index = []
        for present in presents:

            # draw present
            present.draw()
            present.move()

            # find if present need to be removed
            if present.is_present_over() or present.present_collected(player.rect):
                delete_present_index.append(presents.index(present))

            # find if collected by elf
            if present.present_collected(player.rect):
                score += 1

        # remove all presents which have been collided
        for i in range(0, len(delete_present_index)):
            presents.remove(presents[delete_present_index[i]])

        # update
        pygame.display.update()
        clock.tick(FPS)
        animate_timer += 0.13
        present_timer += 0.013


# run whole game

if __name__ == "__main__":
    game()
