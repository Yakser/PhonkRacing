import pygame
import os
import sys
import random
import csv
from pygame.locals import *

# ------------------- CONSTANTS -------------------
size = width, height = 800, 800
fps = 60
heart_cost = 200
skin_cost = 1000
GRAVITY = 1
# ------------------- ИНИЦИАЛИЗАЦИЯ -------------------
pygame.init()
pygame.display.set_caption('PhonkRacing')
pygame.display.set_icon(pygame.image.load(os.path.join('sprites', "ico.png")))
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN])
screen = pygame.display.set_mode(size, DOUBLEBUF | SCALED)
screen.set_alpha(None)
screen_rect = screen.get_rect()
clock = pygame.time.Clock()
speed_accel = 0

# ------------------- ЗВУКИ -------------------
pygame.mixer.init()
coin_sound1 = pygame.mixer.Sound('sounds/coin1.mp3')
coin_sound2 = pygame.mixer.Sound('sounds/coin2.mp3')
click_sound = pygame.mixer.Sound('sounds/click.mp3')
crash_sound = pygame.mixer.Sound('sounds/crash.mp3')

# --- СЧИТВАНИЕ СПИСКА СКИНОВ ---
with open("skins.txt", "r") as f:
    skins = list(f.read().split())
    if not skins:
        skins += ['car_blue.png']

# --- ВЫБРАННЫЙ СКИН ---
with open("selected_skin.txt", "r") as f:
    selected_skin = f.read().strip()
    if not selected_skin or selected_skin not in skins:
        selected_skin = 'car_blue.png'


# --- ЗАГРУЗКА СПРАЙТОВ ---
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


# --- ПОЛУЧЕНИЕ СПИСКА РЕКОРДОВ ---
def get_scores():
    try:
        with open('scores.csv', 'r', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            return [int(row[0]) for row in reader]
    except:
        return [0, 0, 0]


# --- ДОБАВЛЕНИЕ НОВОГО РЕКОРДА ---
def write_score(score: int):
    try:
        scores = get_scores()
        with open('scores.csv', 'w', newline='') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for nscore in (sorted(scores + [score], reverse=True))[:3]:
                writer.writerow([nscore])
    except:
        write_score(0)


# --- СОХРАНЕНИЕ ТЕКУЩЕГО КОЛИЧЕСТВА МОНЕТ ---
def write_coins():
    try:
        with open("coins_count.txt", "w") as coins_count:
            coins_count.write(coins_counter.coins_cnt)
    except:
        with open("coins_count.txt", "w") as coins_count:
            coins_count.write("0")


# ---  ПОЛУЧЕНИЕ ТЕКУЩЕГО КОЛИЧЕСТВА МОНЕТ ---
def get_coins():
    try:
        with open("coins_count.txt", "r") as coins_count:
            return int(coins_count.read())
    except:
        return 0


# ---  ПОЛУЧЕНИЕ ТЕКУЩЕГО КОЛИЧЕСТВА ЖИЗНЕЙ ---
def get_lives():
    try:
        with open("lives_count.txt", "r") as lives_count:
            return int(lives_count.read())
    except:
        return 0


# --- СОХРАНЕНИЕ ТЕКУЩЕГО КОЛИЧЕСТВА ЖИЗНЕЙ ---
def write_lives():
    try:
        with open("lives_count.txt", "w") as lives_count:
            lives_count.write(str(lives_counter.lives_cnt))
    except:
        lives_count.write("0")


# --- ОТОБРАЖЕНИЕ ТЕКСТА ---
def blit_text(text: str, color: str, size: int, ycoord: int, xcoord: int = None):
    font = pygame.font.Font("fonts/distance_counter_font.ttf", size)
    string_rendered = font.render(text, 1, pygame.Color(color))
    rect = string_rendered.get_rect()
    rect.top = ycoord
    rect.x = width // 2 - rect.width // 2
    if xcoord:
        rect.x = xcoord
    screen.blit(string_rendered, rect)


# --- СПРАЙТ ИЗОБРАЖЕНИЯ ---
class Image(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, filename: str, size: tuple, *group):
        super().__init__(*group)
        self.image = load_image(filename)
        self.image = pygame.transform.scale(self.image, size)
        self.width, self.height = size
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos


# --- СПРАЙТ ТАЙЛА ДОРОГИ ---
class Road(pygame.sprite.Sprite):
    image = load_image("road1.jpg")
    image = pygame.transform.scale(image, (width, width))
    height = image.get_height()

    def __init__(self, pos_y: int, *group):
        super().__init__(*group)
        self.image = Road.image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = height // 2 - self.width // 2
        self.rect.y = pos_y
        self.pos_y = pos_y
        self.road_speed = 600 / fps
        self.i = 0

    def update(self, speed_accel: int):  # как только тайл выходит за границы экрана снизу, он перемещается наверх
        self.rect.y += int((self.road_speed + speed_accel))
        if self.rect.y >= height:
            self.rect.y = -height


# --- СПРАЙТ ВСТРЕЧНЫХ МАШИН ---
class Traffic(pygame.sprite.Sprite):
    images = [pygame.transform.scale(load_image(f"traffic{i}.png"), (9 * 15, 16 * 15))
              for i in range(1, 6)]

    def __init__(self, *group):
        super().__init__(*group)
        self.image = random.choice(Traffic.images)
        self.speed = 450 / fps
        self.visible = True
        self.height = self.image.get_height()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):  # рандомный спавн машины на одной из 4-ёх полос движения
        self.rect.x = random.choice([40, 235, 440, 640])
        self.rect.y = -random.randint(height, height * 3)
        # проверка на столкновения с другими машинами
        collided = len([1 for traffic in traffics if pygame.sprite.collide_mask(self, traffic)])
        while collided > 1:
            self.rect.x = random.choice([40, 235, 440, 640])
            self.rect.y = random.randint(-height * 3, - height)
            collided = len([1 for traffic in traffics if pygame.sprite.collide_mask(self, traffic)])

    def update(self, speed_accel: int):  # респавн при выходе за границы экрана
        self.rect.y += int(self.speed + speed_accel)
        if self.rect.y >= height:
            self.spawn()


# --- СПРАЙТ МАШИНЫ ИГРОКА ---
class Car(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image(selected_skin), (9 * 15, 16 * 15))  # 16x9

    def __init__(self, *group):
        super().__init__(*group)
        self.is_alive = True
        self.image = Car.image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = height // 2 - self.width // 2
        self.rect.y = width - self.height // 2 - 150
        self.mask = pygame.mask.from_surface(self.image)
        self.distance = 0
        self.speed_x = 450 / fps
        self.distance_counter = DistanceCounter(0)  # счетчик пройденного расстояния
        self.speed_accel = 0
        self.coins_cnt = get_coins()  # количество монет
        self.lives_cnt = get_lives()  # количество жизней

    def update(self, x: int, angle: int, speed_accel: int):  # движение машины игрока
        self.rect.x = x
        self.distance += 1 + speed_accel // 20
        self.distance_counter.update(self.distance)
        if self.rect.x + self.width >= width:
            self.rect.x = width - self.width
        if self.rect.x <= 0:
            self.rect.x = 0
        self.image = pygame.transform.rotate(Car.image, angle)

        # подсчет собранных монет
        collided_coins = [pygame.sprite.collide_mask(self, coin) for coin in coins]
        if any(collided_coins):
            collided_coins_sprites = [coins[i] for i in range(len(coins)) if collided_coins[i]]
            for collided_coin, coords in zip(collided_coins_sprites, collided_coins):
                if collided_coin and collided_coin.visible:
                    random.choice([coin_sound1, coin_sound2]).play()

                    create_particles((collided_coin.rect.x + collided_coin.width // 2,
                                     collided_coin.rect.y + collided_coin.rect.height // 2))
                    self.coins_cnt += 1
                    collided_coin.hide()

        # "смерть" при столкновении со встречной машиной
        collided_traffics = [pygame.sprite.collide_mask(self, traffic) for traffic in traffics]
        if any(collided_traffics):
            self.is_alive = False

        coins_counter.update(self.coins_cnt)  # обновление количества монет

    def reset(self):  # сброс
        self.__init__()

    def get_distance(self):  # пройденная дистанция
        return self.distance

    def set_skin(self, skin_name):  # установка скина
        image = pygame.transform.scale(load_image(skin_name), (9 * 15, 16 * 15))  # 9x16
        Car.image = image
        self.image = image


# --- СПРАЙТ МОНЕТЫ ---
class Coin(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image("coin.png"), (75, 75))
    coin_width = image.get_width()

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Coin.image
        self.coin_speed = 600 / fps
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(10, width - Coin.coin_width)
        self.rect.y = random.randint(-3 * height, -height)
        self.mask = pygame.mask.from_surface(self.image)
        self.mask = pygame.mask.from_surface(self.image)
        self.visible = True
        self.transparent_sprite = pygame.Surface((self.width, self.height)).convert_alpha()
        self.transparent_sprite.fill((0, 0, 0, 0))

    def update(self, speed_accel: int):  # перемещение монеты по экрану
        self.rect.y += int(self.coin_speed + speed_accel)
        if self.rect.y >= height:  # респавн при выходе за границы экрана
            self.spawn()
            self.show()

    def spawn(self):

        self.rect.x = random.randint(5, width - Coin.coin_width - 5)
        self.rect.y = random.randint(-height, -self.height)
        # проверка на столкновения с другими монетами
        collided = len([1 for coin in coins if pygame.sprite.collide_mask(self, coin)])
        while collided > 1:
            self.rect.x = random.randint(5, width - Coin.coin_width - 5)
            self.rect.y = random.randint(-height, -self.height)
            collided = len([1 for coin in coins if pygame.sprite.collide_mask(self, coin)])

    def hide(self):  # монетка пропадает при столкновении
        self.visible = False
        self.image = self.transparent_sprite

    def show(self):  # появление монеты
        self.visible = True
        self.image = Coin.image


# --- СЧЕТЧИК ПРОЙДЕННОГО РАССТОЯНИЯ ---
class DistanceCounter:
    def __init__(self, dist: int):
        self.dist = str(dist)
        self.font = pygame.font.Font("fonts/distance_counter_font.ttf", 60)
        self.update(dist)

    def update(self, dist: int):  # обновление счетчика
        self.dist = str(dist // fps * 5)
        string_rendered = self.font.render(f"{self.dist} m", 1, pygame.Color('white'))
        rect = string_rendered.get_rect()
        rect.top = 60
        rect.x = width - rect.right - 20
        screen.blit(string_rendered, rect)


# --- СЧЕТЧИК КОЛИЧЕСТВА МОНЕТ ---
class CoinsCounter:
    def __init__(self, coins_cnt: int):
        self.coins_cnt = str(coins_cnt)
        self.coin_ico = pygame.transform.scale(Coin.image, (40, 40))
        font = pygame.font.Font("fonts/distance_counter_font.ttf", 60)
        self.string_rendered = font.render(self.coins_cnt, 1, pygame.Color('#f4de7e'))
        self.rect = self.string_rendered.get_rect()
        self.rect.top = 10
        self.rect.x = width - self.rect.right - 20
        self.blit()

    def update(self, coins_cnt: int):  # обновление счетчика
        self.coins_cnt = coins_cnt
        self.__init__(coins_cnt)

    def blit(self):
        screen.blit(self.coin_ico, (self.rect.left - 45, self.rect.y + 20, 40, 40))
        screen.blit(self.string_rendered, self.rect)


# --- СЧЕТЧИК КОЛИЧЕСТВА ЖИЗНЕЙ ---
class LivesCounter:
    def __init__(self, lives_cnt: int):
        self.lives_cnt = str(lives_cnt)
        heart_ico = load_image("heart_ico.png")
        self.heart_ico = pygame.transform.scale(heart_ico, (30, 30))
        self.font = pygame.font.Font("fonts/distance_counter_font.ttf", 60)
        self.string_rendered = self.font.render(self.lives_cnt, 1, pygame.Color('#f18c8e'))
        self.rect = self.string_rendered.get_rect()
        self.rect.top = 10
        self.rect.x = width - self.rect.right - 20
        screen.blit(self.heart_ico, (self.rect.left - 35, 0, 30, 30))
        screen.blit(self.string_rendered, (self.rect.left - 35, 0, 30, 30))

    def update(self, lives_cnt: int):  # обновление счетчика
        self.lives_cnt = lives_cnt
        text_coord = 0
        self.string_rendered = self.font.render(str(self.lives_cnt), 1, pygame.Color('#f18c8e'))
        self.rect = self.string_rendered.get_rect()
        text_coord += 10
        self.rect.top = text_coord
        self.rect.x = width - self.rect.right - 20
        text_coord += self.rect.height

    def draw(self):  # перерисовка счетчика
        screen.blit(self.heart_ico, (self.rect.left - 35, 85, 30, 30))
        screen.blit(self.string_rendered, (self.rect.left, 60, 30, 30))

    def add_life(self):  # добавление жизни
        self.lives_cnt = int(self.lives_cnt) + 1
        self.update(self.lives_cnt)


# --- ВЫХОД ИЗ ИГРЫ ---
def terminate():
    global skins
    write_coins()
    write_lives()
    write_score(car.distance // fps * 5)
    with open("skins.txt", "w") as f:
        [f.write(skin + '\n') for skin in skins]
    pygame.quit()
    sys.exit()


# --- ЗАСТАВКА ---
def show_intro():
    bg = pygame.transform.scale(load_image('bg.png'), (width, height))
    screen.blit(bg, (0, 0))
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONDOWN:
                click_sound.play()
                return
        clock.tick(fps)
        pygame.display.flip()


# --- КНОПКА МЕНЮ ---
class MenuButton(pygame.sprite.Sprite):
    def __init__(self, ico_name: str, functype: str, y_coord: int, x_coord=None):
        super(MenuButton, self).__init__()
        self.btn_w = int(125 * 1.5)
        self.btn_h = int(75 * 1.5)
        self.functype = functype
        self.ico = pygame.transform.scale(load_image(ico_name), (self.btn_w, self.btn_h))
        self.image = self.ico
        self.ico_name = ico_name
        self.ico_hovered = pygame.transform.scale(load_image(ico_name.split(".")[0] + "_hovered.png"),
                                                  (self.btn_w, self.btn_h))
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        if not x_coord:
            self.rect.x = width // 2 - self.btn_w // 2
        self.rect.y = y_coord
        self.y_coord = y_coord

    def resize(self, w: int, h: int):  # изменение размера кнопки
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

    def move(self, x: int, y: int):  # перемещение кнопки
        self.rect.x = x
        self.rect.y = y


# --- КНОПКА МАГАЗИНА ---
class ShopButton(MenuButton):
    def __init__(self, ico_name: str, functype: str, y_coord: int, x_coord=None, skin=None):
        super(ShopButton, self).__init__(ico_name, functype, y_coord, x_coord)
        self.skin = skin


# --- НОВАЯ ИГРА ---
def new_game():
    global speed_accel
    speed_accel = 0
    write_score(car.distance // fps * 5)
    car.reset()
    game()


# --- ПОКУПКА ЖИЗНИ ---
def buy_heart():
    coins_count = int(coins_counter.coins_cnt)
    if coins_count >= heart_cost:
        coins_count -= heart_cost
        lives_counter.add_life()
        coins_counter.update(coins_count)
        write_coins()
        car.coins_cnt = coins_count
    shop()


# --- ПОКУПКА СКИНА ---
def buy_skin(cost, skin, grid):
    global skins, selected_skin
    need_to_set_skin = False
    if skin not in skins:
        coins_count = int(coins_counter.coins_cnt)
        if coins_count >= cost:
            coins_count -= cost
            coins_counter.update(coins_count)
            write_coins()
            car.coins_cnt = coins_count
            car.set_skin(skin)
            skins += [skin]
            need_to_set_skin = True
    else:
        need_to_set_skin = True
    if need_to_set_skin:
        with open("selected_skin.txt", "w") as f:
            f.write(skin)
        selected_skin = skin
        car.set_skin(skin)
        [block.__init__(block.block_filename, block.item_filename, block.functype) for block in grid.table]

    shop()


# --- LAYOUT ТОВАРОВ В МАГАЗИНЕ ---
class Grid:
    def __init__(self):
        self.table = []
        self.buttons_group = pygame.sprite.Group()
        self.margin = 0
        self.block_width = 0

    def add(self, block):
        self.table.append(block)
        self.buttons_group.add(block.button)
        self.block_width = max(self.block_width, block.buy_block_size)
        self.margin = max((width - len(self.table) * self.block_width) // (len(self.table) + 1), 10)

    def draw(self):
        x = self.margin
        y = self.block_width
        for block in self.table:
            screen.blit(block.block, (x, y))
            block.button.move(x, y)
            x += self.margin + self.block_width
            if x + self.block_width >= width:
                x = self.margin
                y += self.block_width + self.margin

        self.buttons_group.draw(screen)


# --- БЛОК ТОВАРА В МАГАЗИНЕ ---
class BuyBlock:
    def __init__(self, block_filename, item_filename, functype):
        self.buy_block_size = 250
        default_y_coord = 250
        self.block_filename = block_filename
        self.item_filename = item_filename
        self.functype = functype
        skin = None
        if "car" in item_filename:
            skin = item_filename.replace("buy_", "").replace("_block", "")
            if skin == selected_skin:
                item_filename = "selected.png"
            elif skin in skins:
                item_filename = "select.png"
            else:
                item_filename = "buy_car_btn.png"

        self.block = pygame.transform.scale(load_image(block_filename), (self.buy_block_size, self.buy_block_size))
        self.button = ShopButton(item_filename, functype, default_y_coord, skin=skin)
        self.button.resize(self.buy_block_size, self.buy_block_size)


# --- МАГАЗИН ---
def shop():
    bg = pygame.transform.scale(load_image('menu_bg.png'), (width, height))
    screen.blit(bg, (0, 0))
    grid = Grid()
    [grid.add(block) for block in [BuyBlock("buy_heart.png", "buy_heart_btn.png", "buy_heart"),
                                   BuyBlock("buy_car_pink_block.png", "buy_car_pink_block.png", "buy_skin"),
                                   BuyBlock("buy_car_blue_block.png", "buy_car_blue_block.png", "buy_skin"),
                                   BuyBlock("buy_car_red_block.png", "buy_car_red_block.png", "buy_skin"),
                                   BuyBlock("buy_car_orange_block.png", "buy_car_orange_block.png", "buy_skin"),
                                   BuyBlock("buy_car_green_block.png", "buy_car_green_block.png", "buy_skin")
                                   ]]

    buttons_group = pygame.sprite.Group()
    close_btn = MenuButton("close_btn.png", "menu", 0)
    close_btn.resize(65, 65)
    close_btn.move(15, 0)
    buttons_group.add(close_btn)
    functions = {
        "play": new_game,
        "quit": terminate,
        "continue": game,
        "shop": shop,
        "menu": to_menu,
        "buy_heart": buy_heart,
        "buy_skin": buy_skin
    }

    blit_text("SHOP", '#f4de7e', 90, 10)
    coins_counter.blit()
    lives_counter.draw()
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
                    click_sound.play()
                    functions[sprite.functype]()
                    return
            else:
                sprite.image = sprite.ico
        args = ()
        for sprite in grid.buttons_group.sprites():
            if sprite.rect.collidepoint((mx, my)):
                sprite.image = sprite.ico_hovered
                if sprite.functype == "buy_skin":
                    skin = sprite.skin
                    args = (skin_cost, skin, grid)
                if clicked:
                    click_sound.play()
                    functions[sprite.functype](*args)
                    return
            else:
                sprite.image = sprite.ico

        buttons_group.draw(screen)
        grid.draw()
        clock.tick(fps)
        pygame.display.flip()


# --- РЕКОРДЫ ---
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
    scores = get_scores() + [0, 0, 0]
    blit_text(f"1 - {scores[0]}m", '#f4de7e', 70, dy)
    blit_text(f"2 - {scores[1]}m", '#f1d1b5', 70, dy + 70)
    blit_text(f"3 - {scores[2]}m", '#f1d1b5', 70, dy + 140)

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
                    click_sound.play()
                    functions[sprite.functype]()
                    return
            else:
                sprite.image = sprite.ico

        buttons_group.draw(screen)
        clock.tick(fps)
        pygame.display.flip()

# --- НАСТРОЙКИ ---
def settings():
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
    coins_counter.blit()
    lives_counter.draw()
    h = MenuButton("play_btn.png", "", 0).height
    n = 3
    y = (height - (n + 1) * h) // n
    dy = y + h

    shop_btn = MenuButton("shop_btn.png", "shop", y)
    y += dy
    scores_btn = MenuButton("scores_btn.png", "scores", y)
    y += dy
    quit_btn = MenuButton("quit_btn.png", "quit", y)

    buttons_group.add(shop_btn)
    buttons_group.add(scores_btn)
    buttons_group.add(quit_btn)

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if car.distance:
                        click_sound.play()
                        return game()
                    else:
                        terminate()

        for sprite in buttons_group.sprites():
            if sprite.rect.collidepoint((mx, my)):
                sprite.image = sprite.ico_hovered
                if clicked:
                    click_sound.play()
                    return functions[sprite.functype]()
            else:
                sprite.image = sprite.ico
        buttons_group.draw(screen)
        pygame.display.flip()
        clock.tick(fps)

# --- ОСНОВНОЕ МЕНЮ ---
def main_menu():
    bg = pygame.transform.scale(load_image('menu_bg.png'), (width, height))
    screen.blit(bg, (0, 0))
    buttons_group = pygame.sprite.Group()
    functions = {
        "play": new_game,
        "quit": terminate,
        "continue": game,
        "shop": shop,
        "scores": scores,
        "settings": settings
    }
    coins_counter.blit()
    lives_counter.draw()
    h = MenuButton("play_btn.png", "", 0).height
    n = 5 if not car.distance else 6
    y = (height - (n + 1) * h) // n
    dy = y + h

    play_btn = MenuButton("play_btn.png", "play", y)
    y += dy
    if car.distance:
        continue_btn = MenuButton("continue_btn.png", "continue", y)
        buttons_group.add(continue_btn)
        y += dy
    shop_btn = MenuButton("shop_btn.png", "shop", y)
    y += dy
    scores_btn = MenuButton("scores_btn.png", "scores", y)
    y += dy
    settings_btn = MenuButton("settings_btn.png", "settings", y)
    y += dy
    quit_btn = MenuButton("quit_btn.png", "quit", y)

    buttons_group.add(play_btn)
    buttons_group.add(shop_btn)
    buttons_group.add(scores_btn)
    buttons_group.add(settings_btn)
    buttons_group.add(quit_btn)

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if car.distance:
                        click_sound.play()
                        return game()
                    else:
                        terminate()

        for sprite in buttons_group.sprites():
            if sprite.rect.collidepoint((mx, my)):
                sprite.image = sprite.ico_hovered
                if clicked:
                    click_sound.play()
                    return functions[sprite.functype]()
            else:
                sprite.image = sprite.ico
        buttons_group.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


# --- ВОЗРОЖДЕНИЕ ---
def revive():
    lives_count = int(lives_counter.lives_cnt)
    coins_cnt = int(coins_counter.coins_cnt)
    if lives_count > 0:
        lives_counter.update(lives_count - 1)
        lives_counter.draw()
        game()
    elif coins_cnt >= heart_cost:
        coins_cnt -= heart_cost
        coins_counter.update(coins_cnt)
        car.coins_cnt = coins_cnt
        write_coins()
        game()
    else:
        lives_counter.draw()
        write_score(car.distance // fps * 5)
        car.distance = 0


# --- ВЫХОД В МЕНЮ ---
def to_menu():
    write_score(car.distance // fps * 5)
    car.distance = 0
    main_menu()


# --- ЭКРАН СМЕРТИ ---
def death_screen():
    crash_sound.play()
    bg = pygame.transform.scale(load_image('menu_bg.png'), (width, height))
    screen.blit(bg, (0, 0))
    buttons_group = pygame.sprite.Group()
    youdied_img = Image((width // 2 - 200, -50), "you_died.png", (400, 400))
    images_group = pygame.sprite.Group()
    images_group.add(youdied_img)
    functions = {
        "play": new_game,
        "quit": terminate,
        "shop": shop,
        "revive": revive,
        "menu": to_menu
    }
    coins_count = get_coins()
    lives_count = get_lives()
    lives_counter.update(lives_count)

    h = MenuButton("play_btn.png", "", 0).height
    n = 4 if not car.distance else 5
    y = (height - (n + 1) * h) // n
    dy = y + h
    play_btn = MenuButton("play_btn.png", "play", y)

    y += dy
    revive_btn = MenuButton("revive_btn.png", "revive", y)
    buttons_group.add(revive_btn)
    y += dy
    menu_btn = MenuButton("menu_btn.png", "menu", y)
    y += dy
    shop_btn = MenuButton("shop_btn.png", "shop", y)
    y += dy
    quit_btn = MenuButton("quit_btn.png", "quit", y)

    buttons_group.add(play_btn)
    buttons_group.add(revive_btn)
    buttons_group.add(menu_btn)
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
                    click_sound.play()
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


# --- ОСНОВНАЯ ИГРА ---
def game():
    global speed_accel
    x = car.rect.x
    game_running = True
    angle = 0
    max_speed = 7
    max_angle = 5
    accel_x = x_change = 0

    while game_running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    accel_x = -.4
                elif event.key == pygame.K_RIGHT:
                    accel_x = .4
                if event.key == pygame.K_ESCAPE:
                    write_coins()
                    write_lives()
                    click_sound.play()
                    return main_menu()
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    accel_x = 0

        speed_accel += 1 / fps
        x_change += accel_x
        if abs(x_change) >= max_speed:
            x_change = x_change / abs(x_change) * max_speed
        angle_change = -x_change / 10

        if angle > 0 and accel_x > 0:
            angle *= .87

        elif angle < 0 and accel_x < 0:
            angle *= .87

        if accel_x == 0:
            x_change *= .87
            angle *= .87
        x += x_change
        angle += angle_change
        if abs(angle) >= max_angle:
            angle = angle / abs(angle) * max_angle

        [road.update(int(speed_accel) // 20) for road in roads]
        [coin.update(int(speed_accel) // 20) for coin in coins]
        [traffic.update(int(speed_accel) // 20) for traffic in traffics]
        road_group.draw(screen)
        coins_group.draw(screen)
        traffics_group.draw(screen)

        if not car.is_alive:
            write_coins()
            write_lives()
            dist = car.distance
            car.__init__()
            car.distance = dist
            [traffic.__init__() for traffic in traffics]
            game_running = False
            death_screen()

        car.update(x, angle, int(speed_accel))
        car_group.draw(screen)
        particle_group.update()
        particle_group.draw(screen)
        clock.tick(fps)
        pygame.display.flip()

    main_menu()


# --- СИСТЕМА ЧАСТИЦ ---
class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    particle = [pygame.transform.scale(load_image("coin.png"), (15, 15))]
    for scale in (5, 10, 15):
        particle.append(pygame.transform.scale(particle[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(particle_group)
        self.image = random.choice(self.particle)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-4, 4)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


# --- ГРУППЫ СПРАЙТОВ ---
road_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()
traffics_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()

car = Car()
car_group = pygame.sprite.GroupSingle(car)
roads = [Road(0), Road(-height)]
coins = []
coins += [Coin(), Coin(), Coin()]
traffics = []
traffics += [Traffic(), Traffic(), Traffic()]

[road_group.add(road) for road in roads]
[coins_group.add(coin) for coin in coins]
[traffics_group.add(traffic) for traffic in traffics]
[traffic.spawn() for traffic in traffics]

car_group.add(car)

coins_counter = CoinsCounter(get_coins())
lives_counter = LivesCounter(get_lives())

if __name__ == '__main__':
    show_intro()
    main_menu()

# # Created by Sergey Yaksanov at 10.12.2020
# Copyright © 2020 Yakser. All rights reserved.
