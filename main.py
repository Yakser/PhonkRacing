import pygame
import os
import sys

pygame.init()
pygame.display.set_caption('PhonkRacing')
size = width, height = 800, 800
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    try:
        fullname = os.path.join('sprites', name)
        # если файл не существует, то выходим
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)

        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image
    except:
        print("Произошла ошибка!")
        sys.exit()


class Road(pygame.sprite.Sprite):
    image = load_image("road.png")
    image = pygame.transform.scale(image, (width, width))
    height = image.get_height()

    def __init__(self, pos_y, *group):
        super().__init__(*group)
        self.image = Road.image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = height // 2 - self.width // 2
        self.rect.y = pos_y
        self.pos_y = pos_y
        self.road_speed = 10

    def update(self):
        self.rect.y += self.road_speed
        if self.rect.y >= height:
            self.rect.y = -width


class Car(pygame.sprite.Sprite):
    image = load_image("car.png")
    image = pygame.transform.scale(image, (9 * 15, 16 * 15))  # 16x9

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Car.image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = height // 2 - self.width // 2
        self.rect.y = width - self.height // 2 - 150
        self.speed_x = 7
        self.speed_y = 5

    def update(self, dx, dy):

        self.rect.x += dx
        self.rect.y += dy
        angle = 0
        if dx > 0:
            angle = -5
        elif dx < 0:
            angle = 5
        self.image = pygame.transform.rotate(Car.image, angle)
        if self.rect.x + self.width >= width:
            self.rect.x = width - self.width
        if self.rect.x <= 0:
            self.rect.x = 0
        if self.rect.y + self.height >= height:
            self.rect.y = height - self.height
        if self.rect.y <= 0:
            self.rect.y = 0


if __name__ == '__main__':

    running = True
    fps = 60
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()

    car = Car()
    roads = [Road(0), Road(-height)]

    [all_sprites.add(road) for road in roads]
    all_sprites.add(car)

    dx, dy = 0, 0

    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RIGHT]:
                    dx += car.speed_x

                if keys[pygame.K_LEFT]:
                    dx += -car.speed_x

            if event.type == pygame.KEYUP:
                keys = pygame.key.get_pressed()
                if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
                    dx = 0
                if not (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
                    dy = 0

        car.update(dx, dy)
        [road.update() for road in roads]

        all_sprites.draw(screen)

        clock.tick(fps)
        pygame.display.flip()

    pygame.quit()

# # Created by Sergey Yaksanov at 10.12.2020
# Copyright © 2020 Yakser. All rights reserved.
