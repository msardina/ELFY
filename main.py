from pathlib import Path
import pygame
import os
import random
from pygame import mixer

pygame.init()
mixer.init()
pygame.joystick.init()


# setup joysticks
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
print(joysticks)

FOLDER_ASSETS = Path("assets")
FOLDER_SOUNDS = Path("sfx")

# setup font
font = pygame.font.SysFont("freesansbold", 50)
title_font = pygame.font.SysFont(None, 100)
medium_font = pygame.font.SysFont(None, 75)

# const
GRAVITY = 0.4

# music
game_music = pygame.mixer.Sound(FOLDER_SOUNDS / "background.wav")
game_music.set_volume(0.6)
game_music.play()
speed_sfx = pygame.mixer.Sound(FOLDER_SOUNDS / "speed.wav")
speed_sfx.set_volume(2)
hit_sfx = pygame.mixer.Sound(FOLDER_SOUNDS / "hit.wav")
collect_sfx = pygame.mixer.Sound(FOLDER_SOUNDS / "collect.wav")


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
elf_title = scale_img(pygame.image.load(FOLDER_ASSETS / "title.png"), 1)
arrows = scale_img(pygame.image.load(FOLDER_ASSETS / "arrows.png"), 1)
begin_img = scale_img(pygame.image.load(FOLDER_ASSETS / "begin.png"), 1)

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

    def move(self, keys, a_button, side_button):

        if not self.die:
            # keys
            if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
                self.x += self.speed
            if keys[pygame.K_LEFT] and self.x > 0:
                self.x -= self.speed
            if keys[pygame.K_UP] and self.y == HEIGHT - self.height:
                self.dy = 13

            # joysticks
            if a_button and self.y == HEIGHT - self.height:
                self.dy = 13

            if side_button == -1 and self.x > 0:
                self.x -= self.speed
            if side_button == 1 and self.x < WIDTH - self.width:
                self.x += self.speed

        self.y -= self.dy

        if self.y < HEIGHT - self.height:
            self.dy -= GRAVITY
        else:
            if not self.die:
                self.dy = 0
                self.y = HEIGHT - self.height
        # update mask
        self.mask = pygame.mask.from_surface(self.img)

    def animate(self):
        if self.img == self.imgs[0]:
            self.img = self.imgs[1]
        elif self.img == self.imgs[1]:
            self.img = self.imgs[0]

        elif self.img == self.imgs[2]:
            self.img = self.imgs[0]

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


def title():
    # variables
    title = True
    begin = False
    elf_begin_y = 450
    elf_begin_dy = 0
    elf_num = 0
    animate_timer = 0
    begin_x = WIDTH

    while title:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                title = False
                pygame.quit()
                quit()

        # draw
        screen.fill("white")

        if not begin:
            screen.blit(elf_title, (WIDTH / 2 - elf_title.get_width() / 2, 100))
            screen.blit(arrows, (WIDTH / 2 - arrows.get_width() / 2, 410))
            screen.blit(begin_img, (begin_x, HEIGHT - begin_img.get_height() - 5))
        screen.blit(
            elf_imgs[elf_num], (WIDTH / 2 - elf_imgs[2].get_width() / 2, elf_begin_y)
        )

        # keys
        keys = pygame.key.get_pressed()

        # START ANIMATION
        if keys[pygame.K_RETURN]:
            begin = True
        if len(joysticks) > 0 and pygame.joystick.Joystick(0).get_button(1):
            begin = True
        if begin:
            elf_begin_y += elf_begin_dy
            elf_begin_dy += GRAVITY
        if elf_begin_y > HEIGHT - elf_imgs[2].get_height():
            title = False

        if animate_timer > 1:
            if elf_num == 0:
                elf_num = 1
            elif elf_num == 1:
                elf_num = 0
            animate_timer = 0

        # begin text
        begin_x -= 3

        if begin_x < WIDTH * -1:
            begin_x = WIDTH

        # update
        clock.tick(FPS)
        pygame.display.update()
        animate_timer += 0.13


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
    side_button = False
    a_button = False

    # music
    collect_sfx.play()

    # objects
    player = Elf(
        WIDTH / 2 - elf_imgs[2].get_width() / 2,
        HEIGHT - elf_imgs[2].get_height(),
        elf_imgs,
    )
    presents = []
    skiers = []
    skier_random = 0

    # main game loop

    while run:
        a_button = False
        for event in pygame.event.get():  # loop through all events in passed frame
            if event.type == pygame.QUIT:  # quit if x button pressed
                run = False
                pygame.quit()
                quit()
            if len(joysticks) > 0:
                if event.type == pygame.JOYBUTTONDOWN:
                    if pygame.joystick.Joystick(0).get_button(1):
                        a_button = True
        if len(joysticks) > 0:
            side_button = round(pygame.joystick.Joystick(0).get_axis(0))

        # render text
        score_text = title_font.render(f"{score}", True, (0, 0, 0))

        # draw
        screen.fill("white")
        player.draw()
        screen.blit(score_text, (WIDTH / 2 - score_text.get_width() / 2, 50))

        # move
        player.move(pygame.key.get_pressed(), a_button, side_button)

        # animate
        if animate_timer > 1:
            player.animate()
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
                collect_sfx.play()

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
                hit_sfx.play()
        # difficulty curb
        if difficulty_timer > 50:
            present_spawn -= 0.05
            fall_speed += 0.4
            difficulty_timer = 0

        # spawn skiers
        if random.randint(1, 200) == 1:
            speed_sfx.play()
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

    while True:
        title()
        game()
