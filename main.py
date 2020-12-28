import pygame
import os
import sys
import random

pygame.init()
pygame.display.set_caption('PhonkRacing')
size = width, height = 800, 800
screen = pygame.display.set_mode(size)
fps = 60
running = True
game_running = False
clock = pygame.time.Clock()


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
    image = load_image("road.jpg")
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
        self.coins_cnt = 0
        with open("coins_count.txt", "r") as coins_count:
            self.coins_cnt = int(coins_count.read())

    def update(self, dx, angle):

        self.rect.x += dx
        self.distance += 1
        self.distance_counter.update(self.distance)
        self.image = pygame.transform.rotate(Car.image, angle)

        if self.rect.x + self.width >= width:
            self.rect.x = width - self.width
        if self.rect.x <= 0:
            self.rect.x = 0
        self.image = pygame.transform.rotate(Car.image, angle)
        collided_coin = pygame.sprite.spritecollideany(self, coins)
        if collided_coin and collided_coin.visible:
            self.coins_cnt += 1
            collided_coin.hide()
        coins_counter.update(self.coins_cnt)

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
        self.visible = True

    def update(self, *args):
        self.rect.y += self.coin_speed
        if self.rect.y >= height:
            self.rect.y = -width
            self.rect.x = random.randint(5, width - Coin.coin_width - 5)
            self.rect.y = random.randint(-height, 0)
            self.show()

    def hide(self):
        self.visible = False
        transparent_sprite = pygame.Surface((width, height))
        transparent_sprite = transparent_sprite.convert_alpha()
        transparent_sprite.fill((0, 0, 0, 0))
        self.image = transparent_sprite

    def show(self):
        self.visible = True
        self.image = Coin.image


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


class CoinsCounter:
    def __init__(self, coins_cnt):
        self.coins_cnt = str(coins_cnt)
        coin_ico = Coin.image
        coin_ico = pygame.transform.scale(coin_ico, (30, 30))
        font = pygame.font.Font("fonts/distance_counter_font.ttf", 60)
        text_coord = 0
        string_rendered = font.render(self.coins_cnt, 1, pygame.Color('#f4de7e'))
        rect = string_rendered.get_rect()
        text_coord += 10
        rect.top = text_coord
        rect.x = width - rect.right - 20
        text_coord += rect.height
        screen.blit(coin_ico, (rect.left - 35, rect.y + 30, 30, 30))
        screen.blit(string_rendered, rect)

    def update(self, coins_cnt):
        self.coins_cnt = coins_cnt
        self.__init__(coins_cnt)


def terminate():
    with open("coins_count.txt", "w") as coins_count:
        coins_count.write(coins_counter.coins_cnt)
    pygame.quit()
    sys.exit()


def show_intro():
    bg = pygame.transform.scale(load_image('bg.png'), (width, height))
    screen.blit(bg, (0, 0))
    fps = 60
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(fps)


class MenuButton(pygame.sprite.Sprite):
    def __init__(self, ico_name, functype, y_coord):
        super(MenuButton, self).__init__()
        self.btn_w = 125
        self.btn_h = 75
        self.functype = functype
        self.ico = pygame.transform.scale(load_image(ico_name), (self.btn_w, self.btn_h))
        self.image = self.ico
        self.i = ico_name.split(".")[0] + "_hovered.png"
        self.ico_hovered = pygame.transform.scale(load_image(ico_name.split(".")[0] + "_hovered.png"),
                                                  (self.btn_w, self.btn_h))
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect.x = width // 2 - self.btn_w // 2
        self.rect.y = y_coord


def new_game():
    car.distance = 0
    game()


def shop():
    pass


def main_menu():
    bg = pygame.transform.scale(load_image('menu_bg.png'), (width, height))
    screen.blit(bg, (0, 0))
    buttons_group = pygame.sprite.Group()

    functions = {
        "play": new_game,
        "quit": terminate,
        "continue": game,
        "shop": shop
    }
    with open("coins_count.txt", "r") as coins_count:
        coins_count = int(coins_count.read())
    dy = 100
    play_btn = MenuButton("play_btn.png", "play", dy)

    dy += 100
    if car.distance:
        continue_btn = MenuButton("continue_btn.png", "continue", dy)
        buttons_group.add(continue_btn)
        dy += 100
    shop_btn = MenuButton("shop_btn.png", "shop", dy)
    dy += 100
    quit_btn = MenuButton("quit_btn.png", "quit", dy)

    buttons_group.add(play_btn)

    buttons_group.add(shop_btn)
    buttons_group.add(quit_btn)

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()

        for sprite in buttons_group.sprites():
            if sprite.rect.collidepoint((mx, my)):
                sprite.image = sprite.ico_hovered
                if clicked:
                    functions[sprite.functype]()
                    return
            else:
                sprite.image = sprite.ico

        buttons_group.draw(screen)
        coins_counter.update(coins_count)
        clock.tick(fps)
        pygame.display.flip()


def game():
    game_running = True
    dx = angle = 0

    while game_running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RIGHT]:
                    dx = car.speed_x

                if keys[pygame.K_LEFT]:
                    dx = -car.speed_x

                if keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]:
                    dx = 0
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        with open("coins_count.txt", "w") as coins_count:
                            coins_count.write(coins_counter.coins_cnt)
                        main_menu()
                        return

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
        car.update(dx, angle)

        clock.tick(fps)
        pygame.display.flip()

    main_menu()


all_sprites = pygame.sprite.Group()
car = Car()
roads = [Road(0), Road(-height)]
coins = [Coin(), Coin(), Coin()]

[all_sprites.add(road) for road in roads]
[all_sprites.add(coin) for coin in coins]
all_sprites.add(car)
dist_counter = DistanceCounter(0)

with open("coins_count.txt", "r") as coins_count:
    coins_count = int(coins_count.read())
    coins_counter = CoinsCounter(coins_count)

if __name__ == '__main__':
    show_intro()
    main_menu()

# # Created by Sergey Yaksanov at 10.12.2020
# Copyright © 2020 Yakser. All rights reserved.
