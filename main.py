import pygame
import os
import sys
import random
import csv

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


def get_scores():
    with open('scores.csv', 'r', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        return [int(row[0]) for row in reader]


def write_score(score):
    scores = get_scores()
    with open('scores.csv', 'w', newline='') as csvfile:
        writer = csv.writer(
            csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for nscore in (sorted(scores + [score], reverse=True))[:3]:
            writer.writerow([nscore])


def blit_text(text, color, size, ycoord, xcoord=None):
    font = pygame.font.Font("fonts/distance_counter_font.ttf", size)
    string_rendered = font.render(text, 1, pygame.Color(color))
    rect = string_rendered.get_rect()
    rect.top = ycoord
    rect.x = width // 2 - rect.width // 2
    if xcoord:
        rect.x = xcoord
    screen.blit(string_rendered, rect)


class Image(pygame.sprite.Sprite):
    def __init__(self, pos, filename, size, *group):
        super().__init__(*group)
        self.image = load_image(filename)
        self.image = pygame.transform.scale(self.image, size)
        self.width, self.height = size
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos


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


class Traffic(pygame.sprite.Sprite):
    image = pygame.transform.scale(
        load_image(f"traffic{random.choice(['1', '2', '3', '4', '5'])}.png"), (9 * 15, 16 * 15))  # 16x9
    traffic_width = image.get_width()

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Traffic.image
        self.speed = 7
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([40, 235, 440, 640])
        self.rect.y = random.randint(-height * 5, - height * 2)
        self.mask = pygame.mask.from_surface(self.image)
        while pygame.sprite.spritecollideany(self, traffics_group):
            if pygame.sprite.spritecollideany(self, traffics_group) == self:
                break
            self.rect.x = random.choice([40, 235, 440, 640])
            self.rect.y = random.randint(-height * 5, - height * 2)

        self.visible = True

    def update(self, *args):
        self.rect.y += self.speed
        if self.rect.y >= height:
            self.rect.y = -width * 3
            self.rect.x = random.choice([40, 235, 440, 640])
            self.rect.y = random.randint(-height * 3, - height)
            self.show()

    def hide(self):
        self.visible = False
        transparent_sprite = pygame.Surface((width, height))
        transparent_sprite = transparent_sprite.convert_alpha()
        transparent_sprite.fill((0, 0, 0, 0))
        self.image = transparent_sprite

    def show(self):
        img = pygame.transform.scale(
            load_image(f"traffic{random.choice(['1', '2', '3', '4', '5'])}.png"), (9 * 15, 16 * 15))  # 16x9
        self.visible = True
        self.image = img


class Car(pygame.sprite.Sprite):
    image = load_image("car_blue.png")
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
        self.lives_cnt = 0
        self.is_alive = True
        self.mask = pygame.mask.from_surface(self.image)
        with open("coins_count.txt", "r") as coins_count:
            self.coins_cnt = int(coins_count.read())
        with open("lives_count.txt", "r") as lives_count:
            self.lives_cnt = int(lives_count.read())

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
        collided_coins = [pygame.sprite.collide_mask(self, coin) for coin in coins]
        if any(collided_coins):
            collided_coins_sprites = [coins[i] for i in range(len(coins)) if collided_coins[i]]
            for collided_coin in collided_coins_sprites:
                if collided_coin and collided_coin.visible:
                    self.coins_cnt += 1
                    collided_coin.hide()

        collided_traffics = [pygame.sprite.collide_mask(self, traffic) for traffic in traffics]
        if any(collided_traffics):
            self.is_alive = False

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
        self.rect.y = random.randint(-3 * height, -height)
        while pygame.sprite.spritecollideany(self, coins_group):
            if pygame.sprite.spritecollideany(self, coins_group) == self:
                self.rect.x = random.randint(5, width - Coin.coin_width - 5)
                self.rect.y = random.randint(-3 * height, -height)
                break
        self.mask = pygame.mask.from_surface(self.image)
        self.visible = True

    def update(self, *args):
        self.rect.y += self.coin_speed
        if self.rect.y >= height:
            self.rect.y = -width
            self.rect.x = random.randint(5, width - Coin.coin_width - 5)
            self.rect.y = random.randint(-height, 0)
            collided = pygame.sprite.spritecollideany(self, coins_group)
            while collided != self:
                self.rect.x = random.randint(5, width - Coin.coin_width - 5)
                self.rect.y = random.randint(-height, 0)
                collided = pygame.sprite.spritecollideany(self, coins_group)

            self.show()

    def hide(self):
        self.visible = False
        transparent_sprite = pygame.Surface((self.width, self.height))
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
        string_rendered = font.render(self.coins_cnt, 1, pygame.Color('#f4de7e'))
        rect = string_rendered.get_rect()
        text_coord = 10
        rect.top = text_coord
        rect.x = width - rect.right - 20
        text_coord += rect.height
        screen.blit(coin_ico, (rect.left - 35, rect.y + 30, 30, 30))
        screen.blit(string_rendered, rect)

    def update(self, coins_cnt):
        self.coins_cnt = coins_cnt
        self.__init__(coins_cnt)


class LivesCounter:
    def __init__(self, lives_cnt):
        self.lives_cnt = str(lives_cnt)
        heart_ico = load_image("heart_ico.png")
        self.heart_ico = pygame.transform.scale(heart_ico, (30, 30))
        self.font = pygame.font.Font("fonts/distance_counter_font.ttf", 60)
        text_coord = 0
        self.string_rendered = self.font.render(self.lives_cnt, 1, pygame.Color('#f18c8e'))
        self.rect = self.string_rendered.get_rect()
        text_coord += 10
        self.rect.top = text_coord
        self.rect.x = width - self.rect.right - 20
        text_coord += self.rect.height
        screen.blit(self.heart_ico, (self.rect.left - 35, 0, 30, 30))
        screen.blit(self.string_rendered, (self.rect.left - 35, 0, 30, 30))

    def update(self, lives_cnt):
        self.lives_cnt = lives_cnt
        text_coord = 0
        self.string_rendered = self.font.render(str(self.lives_cnt), 1, pygame.Color('#f18c8e'))
        self.rect = self.string_rendered.get_rect()
        text_coord += 10
        self.rect.top = text_coord
        self.rect.x = width - self.rect.right - 20
        text_coord += self.rect.height

    def draw(self):
        screen.blit(self.heart_ico, (self.rect.left - 35, 85, 30, 30))
        screen.blit(self.string_rendered, (self.rect.left, 60, 30, 30))

    def add_life(self):
        self.lives_cnt = int(self.lives_cnt) + 1
        self.update(self.lives_cnt)


def terminate():
    with open("coins_count.txt", "w") as coins_count:
        coins_count.write(coins_counter.coins_cnt)
    with open("lives_count.txt", "w") as lives_count:
        lives_count.write(str(lives_counter.lives_cnt))
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
        self.ico_name = ico_name
        self.ico_hovered = pygame.transform.scale(load_image(ico_name.split(".")[0] + "_hovered.png"),
                                                  (self.btn_w, self.btn_h))
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect.x = width // 2 - self.btn_w // 2
        self.rect.y = y_coord
        self.y_coord = y_coord

    def resize(self, w, h):
        self.btn_w = w
        self.btn_h = h
        self.ico = pygame.transform.scale(load_image(self.ico_name), (self.btn_w, self.btn_h))
        self.image = self.ico
        self.ico_hovered = pygame.transform.scale(load_image(self.ico_name.split(".")[0] + "_hovered.png"),
                                                  (self.btn_w, self.btn_h))
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect.x = width // 2 - self.btn_w // 2
        self.rect.y = self.y_coord

    def move(self, x, y):
        self.rect.x = x
        self.rect.y = y


def new_game():
    write_score(car.distance // fps * 5)
    car.distance = 0
    game()


def buy_heart():
    coins_count = int(coins_counter.coins_cnt)
    if coins_count >= 200:
        coins_count -= 200
        lives_counter.add_life()
        coins_counter.update(coins_count)
        with open("coins_count.txt", "w") as coins_cnt:
            coins_cnt.write(str(coins_count))
        car.coins_cnt = coins_count
    shop()


def shop():
    bg = pygame.transform.scale(load_image('menu_bg.png'), (width, height))
    screen.blit(bg, (0, 0))

    buy_block_size = 250

    buy_heart_block = pygame.transform.scale(load_image('buy_heart.png'), (buy_block_size, buy_block_size))
    screen.blit(buy_heart_block, (width // 2 - buy_block_size // 2, 250))

    buttons_group = pygame.sprite.Group()
    close_btn = MenuButton("close_btn.png", "main_menu", 0)
    close_btn.resize(65, 65)
    close_btn.move(15, 0)
    buy_heart_btn = MenuButton("buy_heart_btn.png", "buy_heart", 250)
    buy_heart_btn.resize(buy_block_size, buy_block_size)
    buttons_group.add(close_btn)
    buttons_group.add(buy_heart_btn)
    functions = {
        "play": new_game,
        "quit": terminate,
        "continue": game,
        "shop": shop,
        "main_menu": main_menu,
        "buy_heart": buy_heart
    }
    with open("coins_count.txt", "r") as coins_count:
        coins_count = int(coins_count.read())

    blit_text("SHOP", '#f4de7e', 90, 10)

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    return

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
        lives_counter.draw()
        clock.tick(fps)
        pygame.display.flip()


def scores():
    bg = pygame.transform.scale(load_image('menu_bg.png'), (width, height))
    screen.blit(bg, (0, 0))

    buttons_group = pygame.sprite.Group()
    close_btn = MenuButton("close_btn.png", "main_menu", 0)
    close_btn.resize(65, 65)
    close_btn.move(15, 0)

    buttons_group.add(close_btn)

    functions = {
        "play": new_game,
        "quit": terminate,
        "continue": game,
        "shop": shop,
        "main_menu": main_menu,
    }

    blit_text("SCORES", '#f4de7e', 90, 10)
    dy = 150
    scores = get_scores()
    blit_text(f"1 - {scores[0]}m", '#f4de7e', 70, dy)
    blit_text(f"2 - {scores[1]}m", '#f1d1b5', 60, dy + 70)
    blit_text(f"3 - {scores[2]}m", '#f1d1b5', 60, dy + 140)

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    return

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
        lives_counter.draw()
        clock.tick(fps)
        pygame.display.flip()


def main_menu():
    bg = pygame.transform.scale(load_image('menu_bg.png'), (width, height))
    screen.blit(bg, (0, 0))
    buttons_group = pygame.sprite.Group()
    functions = {
        "play": new_game,
        "quit": terminate,
        "continue": game,
        "shop": shop,
        "scores": scores
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
    scores_btn = MenuButton("scores_btn.png", "scores", dy)
    dy += 100
    quit_btn = MenuButton("quit_btn.png", "quit", dy)

    buttons_group.add(play_btn)
    buttons_group.add(shop_btn)
    buttons_group.add(scores_btn)
    buttons_group.add(quit_btn)

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

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
        lives_counter.draw()
        clock.tick(fps)
        pygame.display.flip()


def revive():
    lives_count = int(lives_counter.lives_cnt)
    if lives_count > 0:
        lives_counter.update(lives_count - 1)
        lives_counter.draw()
        game()
    else:
        lives_counter.draw()
        write_score(car.distance // fps * 5)
        car.__init__()


def death_screen():
    bg = pygame.transform.scale(load_image('menu_bg.png'), (width, height))
    screen.blit(bg, (0, 0))
    buttons_group = pygame.sprite.Group()
    youdied_img = Image((width // 2 - 200, -50), "you_died.png", (400, 400))
    images_group = pygame.sprite.Group()
    images_group.add(youdied_img)
    functions = {
        "play": new_game,
        "quit": terminate,
        "continue": game,
        "shop": shop,
        "revive": revive
    }
    with open("coins_count.txt", "r") as coins_count:
        coins_count = int(coins_count.read())
    with open("lives_count.txt", "r") as lives_count:
        lives_count = int(lives_count.read())
    lives_counter.update(lives_count)
    dy = 300
    play_btn = MenuButton("play_btn.png", "play", dy)

    dy += 100
    revive_btn = MenuButton("revive_btn.png", "revive", dy)
    buttons_group.add(revive_btn)
    dy += 100
    shop_btn = MenuButton("shop_btn.png", "shop", dy)
    dy += 100
    quit_btn = MenuButton("quit_btn.png", "quit", dy)

    buttons_group.add(play_btn)
    buttons_group.add(revive_btn)
    buttons_group.add(shop_btn)
    buttons_group.add(quit_btn)

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

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
        images_group.draw(screen)
        buttons_group.draw(screen)
        coins_counter.update(coins_count)
        lives_counter.draw()
        clock.tick(fps)
        pygame.display.flip()


def game():
    game_running = True
    dx = angle = 0
    while game_running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
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
                        with open("lives_count", "w") as lives_count:
                            lives_count.write(str(lives_counter.lives_cnt))
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
        [traffic.update() for traffic in traffics]
        all_sprites.draw(screen)
        coins_group.draw(screen)
        traffics_group.draw(screen)
        car.update(dx, angle)
        car_group.draw(screen)

        if not car.is_alive:
            with open("coins_count.txt", "w") as coins_count:
                coins_count.write(coins_counter.coins_cnt)
            with open("lives_count.txt", "w") as lives_count:
                lives_count.write(str(lives_counter.lives_cnt))
            dist = car.distance
            car.__init__()
            car.distance = dist
            [traffic.__init__() for traffic in traffics]
            game_running = False
            death_screen()

        clock.tick(fps)
        pygame.display.flip()

    main_menu()


all_sprites = pygame.sprite.Group()
coins_group = pygame.sprite.Group()
traffics_group = pygame.sprite.Group()
car_group = pygame.sprite.Group()

car = Car()
roads = [Road(0), Road(-height)]
coins = [Coin(), Coin(), Coin()]
traffics = [Traffic(), Traffic(), Traffic()]

[all_sprites.add(road) for road in roads]
[coins_group.add(coin) for coin in coins]
[traffics_group.add(traffic) for traffic in traffics]

car_group.add(car)

with open("coins_count.txt", "r") as coins_count:
    coins_count = int(coins_count.read())
    coins_counter = CoinsCounter(coins_count)

with open("lives_count.txt", "r") as lives_count:
    lives_count = int(lives_count.read())
    lives_counter = LivesCounter(lives_count)

if __name__ == '__main__':
    show_intro()
    main_menu()

# # Created by Sergey Yaksanov at 10.12.2020
# Copyright © 2020 Yakser. All rights reserved.
