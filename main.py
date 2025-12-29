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

# const
GRAVITY = 0.4


# scaler
def scale_img(img, scale_factor):
    new_size = [img.get_width() * scale_factor, img.get_height() * scale_factor]
    return pygame.transform.scale(img, new_size)


# load images
elf_run_1 = scale_img(pygame.image.load(FOLDER_ASSETS / "run1.png"), 2.5)
elf_run_2 = scale_img(pygame.image.load(FOLDER_ASSETS / "run2.png"), 2.5)
elf_stand = scale_img(pygame.image.load(FOLDER_ASSETS / "stand.png"), 2.5)
elf_imgs = [elf_run_1, elf_run_2, elf_stand]

skier_1_img = scale_img(pygame.image.load(FOLDER_ASSETS / "ski1.png"), 1)
skier_2_img = scale_img(pygame.image.load(FOLDER_ASSETS / "ski2.png"), 1)
skier_3_img = scale_img(pygame.image.load(FOLDER_ASSETS / "ski3.png"), 1)
skiers_imgs = [skier_1_img, skier_2_img, skier_3_img]
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
        self.mask = pygame.mask.from_surface(self.img)
        self.mask_img = self.mask.to_surface()

    def draw(self):
        screen.blit(self.img, (self.x, self.y))

    def move(self, fall_speed):
        self.y += fall_speed
        self.mask = pygame.mask.from_surface(self.img)

    def present_collected(self, othermask, otherx, othery):
        if self.mask.overlap(othermask, (otherx - self.x, othery - self.y)):
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
        self.dy = 0
        self.imgs = imgs
        self.img = self.imgs[2]
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.mask = pygame.mask.from_surface(self.img)
        self.mask_img = self.mask.to_surface()
        self.speed = 5
        self.die = False

    def draw(self):
        screen.blit(self.img, (self.x, self.y))

    def move(self, keys):

        if not self.die:
            # keys
            if keys[pygame.K_RIGHT]:
                self.x += self.speed
            if keys[pygame.K_LEFT]:
                self.x -= self.speed
            if keys[pygame.K_UP] and self.y == HEIGHT - self.height:
                self.dy = 13

        self.y -= self.dy

        if self.y < HEIGHT - self.height:
            self.dy -= GRAVITY
        else:
            if not self.die:
                self.dy = 0
                self.y = HEIGHT - self.height
        # update mask
        self.mask = pygame.mask.from_surface(self.img)

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

    def die_animation(self):
        self.dy = 13
        self.die = True


class Skier:
    def __init__(self, y, img, side):

        self.y = y
        self.img = img
        self.side = side
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.speed = random.randint(5, 10)
        self.mask = pygame.mask.from_surface(self.img)
        self.mask_img = self.mask.to_surface()

        if side == 0:
            self.x = 0 - self.width
        else:
            self.x = WIDTH
            self.img = pygame.transform.flip(self.img, True, False)

    def draw(self):
        screen.blit(self.img, (self.x, self.y))

    def move(self):
        if self.side == 0:
            self.x += self.speed
        if self.side == 1:
            self.x -= self.speed

        # update rect
        self.mask = pygame.mask.from_surface(self.img)

    def is_offscreen(self):
        if self.side == 0 and self.x > WIDTH:
            return True
        if self.side == 1 and self.x < 0 - self.width:
            return True
        return False

    def hit_elf(self, othermask, otherx, othery, otherdie):
        if (
            self.mask.overlap(othermask, (otherx - self.x, othery - self.y))
            and not otherdie
        ):
            return True

        return False


def game():
    # variables
    run = True
    animate_timer = 0
    present_timer = 0
    score = 0
    fall_speed = 3
    present_spawn = 1
    difficulty_timer = 0
    die = False

    # objects
    player = Elf(0, HEIGHT - elf_imgs[2].get_height(), elf_imgs)
    presents = []
    skiers = []
    skier_random = 0

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
        if present_timer > present_spawn:
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
            present.move(fall_speed)

            # find if present need to be removed
            if present.is_present_over() or present.present_collected(
                player.mask, player.x, player.y
            ):
                delete_present_index.append(presents.index(present))

            # find if collected by elf
            if present.present_collected(player.mask, player.x, player.y):
                score += 1

        # remove all presents which have been collided
        for i in range(0, len(delete_present_index)):
            presents.remove(presents[delete_present_index[i]])

        # draw skiers

        for skier in skiers:
            skier.draw()
            skier.move()

            if skier.is_offscreen():
                skiers.remove(skier)
            if skier.hit_elf(player.mask, player.x, player.y, player.die):
                die = True
        # difficulty curb
        if difficulty_timer > 50:
            present_spawn -= 0.05
            fall_speed += 0.4
            difficulty_timer = 0

        # spawn skiers
        if random.randint(1, 200) == 1:
            skier_random = random.randint(0, 2)
            skiers.append(
                Skier(
                    HEIGHT - skiers_imgs[skier_random].get_height(),
                    skiers_imgs[skier_random],
                    random.randint(0, 1),
                )
            )

        # die animation
        if die:
            player.die_animation()
            die = False

        # game over

        if player.y > HEIGHT * 2:
            run = False

        # update
        pygame.display.update()
        clock.tick(FPS)
        animate_timer += 0.13
        present_timer += 0.013
        difficulty_timer += 0.10


# run whole game

if __name__ == "__main__":
    game()
