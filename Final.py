import pygame
import neat
import time
import os
import random

pygame.init()
clock = pygame.time.Clock()
fps = 60

# Screen size and caption
WIN_WIDTH = 550
WIN_HEIGHT = 800
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Loading images
BG_IMG = pygame.transform.scale(pygame.image.load("C:/Users/dishi/OneDrive/Desktop/Python Projects/Flappy Bird/bg.png"), (550, 700))
BASE_IMG = pygame.transform.scale2x(pygame.image.load("C:/Users/dishi/OneDrive/Desktop/Python Projects/Flappy Bird/base.png"))
PIPE_IMG = pygame.transform.scale(pygame.image.load("C:/Users/dishi/OneDrive/Desktop/Python Projects/Flappy Bird/pipe.png"), (45, 900))
BUTTON_IMG = pygame.image.load("C:/Users/dishi/OneDrive/Desktop/Python Projects/Flappy Bird/restart.png")

# Define game variables
base_scroll = 0
scroll_speed = 3
flying = False
game_over = False
pipe_frequency = 1200  # in milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency  # measure time when last pipe was created ie as soon as game started
score = 0
pass_pipe = False


# Define score font and color
font = pygame.font.SysFont('Bauhaus 93', 40)
white = (255, 255, 255)
# Score display
def draw_text(text, font, color, x, y): 
    img = font.render(text, True, color)
    win.blit(img, (x, y))


# Reseting game upon clicking restart
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(WIN_HEIGHT/2 - 40)
    score = 0
    return score


# Drawing bird
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.transform.scale(pygame.image.load(f"C:/Users/dishi/OneDrive/Desktop/Python Projects/Flappy Bird/bird{num}.png"), (40, 30))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True:
            # Gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 690:
                self.rect.y += int(self.vel)
            if self.rect.top < 50 and pygame.mouse.get_pressed()[0] == 1:    # added this code myself, so that bird doesnt go out of frame at top
                self.rect.top = 50
                self.image = pygame.transform.rotate(self.images[self.index], 0)
                    

        if game_over == False:
            # Jumping
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:  # [0] is for left click
                self.clicked = False

            # Handle the animation
            self.counter += 1
            flap_cooldown = 4

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], -self.vel)

        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


# Drawing pipe
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = PIPE_IMG
        self.rect = self.image.get_rect()
        # position 1 is from top, -1 is from bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)  # flip along y axis
            self.rect.bottomleft = [x, y]
        if position == -1:
            self.rect.topleft = [x, y]

    def update(self): 
        if game_over == False:
            self.rect.x -= scroll_speed
            if self.rect.right < 0:  # to destroy pipes so they dont keep scrolling out of frame
                self.kill()


# Drawing restart button
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    def draw(self):
        action = False
        # Get mouse position
        pos = pygame.mouse.get_pos()
        # Check if mouse is over button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] ==1:
                action = True
        # Draw button
        win.blit(self.image, (self.rect.x, self.rect.y))
        # returning action
        return action


# Making groups
bird_group = pygame.sprite.Group()  # like a python list almost
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(WIN_HEIGHT/2 - 40))
bird_group.add(flappy)  # appends flappy to bird_group


# Creating restart button instance
button = Button(WIN_WIDTH/3 + 25, WIN_HEIGHT/2 - 75, BUTTON_IMG)


# Main loop
run = True
while run:
    
    clock.tick(fps)
    
    # Draw background
    win.blit(BG_IMG, (0, 0))

    bird_group.draw(win)
    bird_group.update()

    pipe_group.draw(win)
    pipe_group.update()
    
    # draw the ground
    win.blit(BASE_IMG, (base_scroll, 690))

    # check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(f"Score:{score}", font, white, WIN_WIDTH/3 + 20, 20)         
    
    
    # look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):  # false for not deleting objects
            game_over = True

    # check if bird has hit ground
    if flappy.rect.bottom >= 690:
        game_over = True
        flying = False

    if game_over == False and flying == True:

        # Generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_gap = random.randint(150, 300)
            pipe_height = random.randint(-100, 100)
            bottom_pipe = Pipe(WIN_WIDTH, int(WIN_HEIGHT/2) + pipe_gap/2 + pipe_height, -1)
            pipe_group.add(bottom_pipe)
            top_pipe = Pipe(WIN_WIDTH, int(WIN_HEIGHT/2) - pipe_gap/2 + pipe_height, 1)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # Draw and scroll the ground
        base_scroll -= scroll_speed
        if abs(base_scroll) > 45:  # 45 is dist b/w 2 diagonal marks
            base_scroll = 0

    # Check for game over and reset
    if game_over == True:
        font_game_over = pygame.font.SysFont('Bauhaus 93', 60)
        red = (200, 0, 0)
        def game_over_display(text, font_game_over, color, x, y): 
            img = font_game_over.render(text, True, color)
            win.blit(img, (x, y))
        game_over_display("Game Over", font_game_over, red, WIN_WIDTH/3-40, WIN_HEIGHT/3)
        if button.draw() == True:
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
    pygame.display.update()

pygame.quit()
quit()