import pygame
import os
import sys
import random

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
        self.distance = 0
        self.distance_counter = DistanceCounter(0)

    def update(self, dx, dy, angle):

        self.rect.x += dx
        self.distance += 1
        self.distance_counter.update(self.distance)
        self.image = pygame.transform.rotate(Car.image, angle)

        if self.rect.x + self.width >= width:
            self.rect.x = width - self.width
        if self.rect.x <= 0:
            self.rect.x = 0
        self.image = pygame.transform.rotate(Car.image, angle)

    def reset(self):
        self.__init__()

    def get_distance(self):
        return self.distance


class Coin(pygame.sprite.Sprite):
    image = load_image("coin.png")

    image = pygame.transform.scale(image, (75, 75))
    coin_width = image.get_width()

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Coin.image
        self.coin_speed = 10
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, width - Coin.coin_width)
        self.rect.y = random.randint(-height, height - Coin.coin_width)

    def update(self, *args):
        self.rect.y += self.coin_speed
        if self.rect.y >= height:
            self.rect.y = -width
            self.rect.x = random.randint(5, width - Coin.coin_width - 5)
            self.rect.y = random.randint(-height, 0)


class DistanceCounter:
    def __init__(self, num):
        self.num = str(num)

        font = pygame.font.Font("fonts/distance_counter_font.ttf", 60)
        text_coord = 50
        string_rendered = font.render(self.num, 1, pygame.Color('white'))
        rect = string_rendered.get_rect()
        text_coord += 10
        rect.top = text_coord
        rect.x = width - rect.right - 20
        text_coord += rect.height
        screen.blit(string_rendered, rect)

    def update(self, dist):
        self.num = str(dist // fps * 5)
        self.__init__(self.num)


if __name__ == '__main__':

    running = True
    fps = 60
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()

    car = Car()

    roads = [Road(0), Road(-height)]

    coins = [Coin(), Coin(), Coin()]

    [all_sprites.add(road) for road in roads]
    [all_sprites.add(coin) for coin in coins]
    all_sprites.add(car)
    dist_counter = DistanceCounter(0)

    dx, dy, angle = 0, 0, 0

    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RIGHT]:
                    dx = car.speed_x

                if keys[pygame.K_LEFT]:
                    dx = -car.speed_x

                if keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]:
                    dx = 0

            if event.type == pygame.KEYUP:
                keys = pygame.key.get_pressed()
                if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
                    dx = 0
        if dx > 0:
            angle -= 1
        elif dx < 0:
            angle += 1
        else:
            if angle > 0:
                angle -= 1
            elif angle < 0:
                angle += 1

        if angle < 0:
            angle = max(-5, angle)
        elif angle > 0:
            angle = min(5, angle)

        [road.update() for road in roads]
        [coin.update() for coin in coins]
        all_sprites.draw(screen)
        car.update(dx, dy, angle)

        clock.tick(fps)
        pygame.display.flip()

    pygame.quit()

# # Created by Sergey Yaksanov at 10.12.2020
# Copyright © 2020 Yakser. All rights reserved.
