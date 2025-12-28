import pygame
import os
import random
from pygame import mixer

pygame.init()
mixer.init()


# scaler
def scale_img(img, scale_factor):
    new_size = [img.get_width() * scale_factor, img.get_height() * scale_factor]
    return pygame.transform.scale(img, new_size)


# load images
elf_run_1 = scale_img(pygame.image.load(os.path.join("assets", "run1.png")), 2)
elf_run_2 = scale_img(pygame.image.load(os.path.join("assets", "run2.png")), 2)
elf_stand = scale_img(pygame.image.load(os.path.join("assets", "stand.png")), 2)
elf_imgs = [elf_run_1, elf_run_2, elf_stand]
# setup screen
FLOOR_HEIGHT = 60
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ELFY")

# setup clock
clock = pygame.time.Clock()
FPS = 60


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
    timer = 0
    # objects
    player = Elf(0, HEIGHT - elf_imgs[2].get_height() - FLOOR_HEIGHT, elf_imgs)

    # main game loop
    while run:
        for event in pygame.event.get():  # loop through all events in passed frame
            if event.type == pygame.QUIT:  # quit if x button pressed
                run = False
                pygame.quit()
                quit()

        # draw
        screen.fill("white")
        player.draw()
        # move
        player.move(pygame.key.get_pressed())
        # animate
        if timer > 1:
            player.animate(pygame.key.get_pressed())
            print("animate!")
            timer = 0
        # update
        pygame.display.update()
        clock.tick(FPS)
        timer += 0.13


# run whole game

if __name__ == "__main__":
    game()
