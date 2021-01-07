import pygame
import os
import sys
import random
import csv

pygame.init()
pygame.display.set_caption('PhonkRacing')
pygame.display.set_icon(pygame.image.load(os.path.join('sprites', "ico.png")))
size = width, height = 800, 800
screen = pygame.display.set_mode(size)
fps = 60
heart_cost = 200
skin_cost = 1000
clock = pygame.time.Clock()
PIXEL_FONT = pygame.font.Font("fonts/pixel.otf", 60)
with open("skins.txt", "r") as f:
    skins = list(f.read().split())
    if not skins:
        skins += ['car_blue.png']
with open("selected_skin.txt", "r") as f:
    selected_skin = f.read().strip()
    if not selected_skin:
        selected_skin = 'car_blue.png'



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
    try:
        with open('scores.csv', 'r', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            return [int(row[0]) for row in reader]
    except:
        return [0, 0, 0]


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


def write_coins():
    try:
        with open("coins_count.txt", "w") as coins_count:
            coins_count.write(coins_counter.coins_cnt)
    except:
        with open("coins_count.txt", "w") as coins_count:
            coins_count.write("0")


def get_coins():
    try:
        with open("coins_count.txt", "r") as coins_count:
            return int(coins_count.read())
    except:
        return 0


def get_lives():
    try:
        with open("lives_count.txt", "r") as lives_count:
            return int(lives_count.read())
    except:
        return 0


def write_lives():
    try:
        with open("lives_count.txt", "w") as lives_count:
            lives_count.write(str(lives_counter.lives_cnt))
    except:
        lives_count.write("0")


def blit_text(text: str, color: str, size: int, ycoord: int, xcoord: int = None):
    font = pygame.font.Font("fonts/distance_counter_font.ttf", size)
    string_rendered = font.render(text, 1, pygame.Color(color))
    rect = string_rendered.get_rect()
    rect.top = ycoord
    rect.x = width // 2 - rect.width // 2
    if xcoord:
        rect.x = xcoord
    screen.blit(string_rendered, rect)


class Image(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, filename: str, size: tuple, *group):
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

    def __init__(self, pos_y: int, *group):
        super().__init__(*group)
        self.image = Road.image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = height // 2 - self.width // 2
        self.rect.y = pos_y
        self.pos_y = pos_y

        # self.max_road_speed = 10
        self.road_speed = 600
        self.i = 0

    def update(self):
        # self.road_speed += 1
        # self.road_speed = min(self.road_speed, self.max_road_speed)

        self.rect.y += int(self.road_speed / fps)

        if self.rect.y >= height:
            self.rect.y = -width


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
        self.rect.x = random.choice([40, 235, 440, 640])
        self.rect.y = random.randint(-height * 3, -2 * height)

    def spawn(self):
        self.rect.x = random.choice([40, 235, 440, 640])
        self.rect.y = random.randint(-height * 3, - height)
        collided = pygame.sprite.spritecollideany(self, traffics_group)
        while collided != self:
            self.rect.x = random.choice([40, 235, 440, 640])
            self.rect.y = random.randint(-height * 3, - height)
            collided = pygame.sprite.spritecollideany(self, traffics_group)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= height:
            self.spawn()


class Car(pygame.sprite.Sprite):
    image = load_image(selected_skin)
    image = pygame.transform.scale(image, (9 * 15, 16 * 15))  # 16x9

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Car.image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = height // 2 - self.width // 2
        self.rect.y = width - self.height // 2 - 150
        self.distance = 0
        self.speed_x = 450 / fps
        self.distance_counter = DistanceCounter(0)
        self.coins_cnt = 0
        self.lives_cnt = 0
        self.is_alive = True
        self.mask = pygame.mask.from_surface(self.image)

        self.coins_cnt = get_coins()
        self.lives_cnt = get_lives()

    def update(self, x: int, angle: int):
        self.rect.x = x
        self.distance += 1
        self.distance_counter.update(self.distance)
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

    def set_skin(self, skin_name):
        image = load_image(skin_name)
        image = pygame.transform.scale(image, (9 * 15, 16 * 15))  # 16x9
        Car.image = image
        self.image = image


class Coin(pygame.sprite.Sprite):
    image = load_image("coin.png")

    image = pygame.transform.scale(image, (75, 75))
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

    def update(self):
        self.rect.y += self.coin_speed
        if self.rect.y >= height:

            self.rect.x = random.randint(5, width - Coin.coin_width - 5)
            self.rect.y = random.randint(-height, -self.height)
            collided = pygame.sprite.spritecollideany(self, coins_group)
            while collided != self:
                self.rect.x = random.randint(5, width - Coin.coin_width - 5)
                self.rect.y = random.randint(-height, -self.height)
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
    def __init__(self, dist: int):
        self.dist = str(dist)
        self.font = pygame.font.Font("fonts/distance_counter_font.ttf", 60)
        self.update(dist)

    def update(self, dist: int):
        self.dist = str(dist // fps * 5)
        string_rendered = self.font.render(f"{self.dist} m", 1, pygame.Color('white'))
        rect = string_rendered.get_rect()
        rect.top = 60
        rect.x = width - rect.right - 20
        screen.blit(string_rendered, rect)


class CoinsCounter:
    def __init__(self, coins_cnt: int):
        self.coins_cnt = str(coins_cnt)
        coin_ico = Coin.image
        coin_ico = pygame.transform.scale(coin_ico, (40, 40))
        font = pygame.font.Font("fonts/distance_counter_font.ttf", 60)
        string_rendered = font.render(self.coins_cnt, 1, pygame.Color('#f4de7e'))
        rect = string_rendered.get_rect()
        rect.top = 10
        rect.x = width - rect.right - 20
        screen.blit(coin_ico, (rect.left - 45, rect.y + 20, 40, 40))
        screen.blit(string_rendered, rect)

    def update(self, coins_cnt: int):
        self.coins_cnt = coins_cnt
        self.__init__(coins_cnt)


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

    def update(self, lives_cnt: int):
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
    global skins
    write_coins()
    write_lives()
    write_score(car.distance // fps * 5)
    with open("skins.txt", "w") as f:
        [f.write(skin + '\n') for skin in skins]
    pygame.quit()
    sys.exit()


def show_intro():
    bg = pygame.transform.scale(load_image('bg.png'), (width, height))
    screen.blit(bg, (0, 0))
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP or event.type == pygame.MOUSEBUTTONDOWN:
                return
        clock.tick(fps)
        pygame.display.flip()


class MenuButton(pygame.sprite.Sprite):
    def __init__(self, ico_name: str, functype: str, y_coord: int, x_coord=None):
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
        if not x_coord:
            self.rect.x = width // 2 - self.btn_w // 2
        self.rect.y = y_coord
        self.y_coord = y_coord

    def resize(self, w: int, h: int):
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

    def move(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y


class ShopButton(MenuButton):
    def __init__(self, ico_name: str, functype: str, y_coord: int, x_coord=None, skin=None):
        super(ShopButton, self).__init__(ico_name, functype, y_coord, x_coord)
        self.skin = skin


def new_game():
    write_score(car.distance // fps * 5)
    car.distance = 0
    game()


def buy_heart():
    coins_count = int(coins_counter.coins_cnt)
    if coins_count >= heart_cost:
        coins_count -= heart_cost
        lives_counter.add_life()
        coins_counter.update(coins_count)
        write_coins()
        car.coins_cnt = coins_count
    shop()


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
            #  TODO добавление скинов в список
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


def shop():
    bg = pygame.transform.scale(load_image('menu_bg.png'), (width, height))
    screen.blit(bg, (0, 0))

    grid = Grid()
    heart_block = BuyBlock("buy_heart.png", "buy_heart_btn.png", "buy_heart")
    car_pink_block = BuyBlock("buy_car_pink_block.png", "buy_car_pink_block.png", "buy_skin")
    car_blue_block = BuyBlock("buy_car_blue_block.png", "buy_car_blue_block.png", "buy_skin")
    car_red_block = BuyBlock("buy_car_red_block.png", "buy_car_red_block.png", "buy_skin")

    grid.add(heart_block)
    grid.add(car_blue_block)
    grid.add(car_pink_block)
    grid.add(car_red_block)

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
    coins_count = get_coins()

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
        args = ()
        for sprite in grid.buttons_group.sprites():
            if sprite.rect.collidepoint((mx, my)):
                sprite.image = sprite.ico_hovered
                if sprite.functype == "buy_skin":
                    skin = sprite.skin
                    args = (skin_cost, skin, grid)
                if clicked:
                    functions[sprite.functype](*args)
                    return
            else:
                sprite.image = sprite.ico

        buttons_group.draw(screen)
        grid.draw()
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
                    functions[sprite.functype]()
                    return
            else:
                sprite.image = sprite.ico

        buttons_group.draw(screen)
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
    coins_count = get_coins()

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
                    return functions[sprite.functype]()
            else:
                sprite.image = sprite.ico
        buttons_group.draw(screen)
        coins_counter.update(coins_count)
        lives_counter.draw()
        pygame.display.flip()
        clock.tick(fps)


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


def to_menu():
    write_score(car.distance // fps * 5)
    car.distance = 0
    main_menu()


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
        "shop": shop,
        "revive": revive,
        "menu": to_menu
    }
    coins_count = get_coins()
    lives_count = get_lives()

    lives_counter.update(lives_count)
    dy = 300
    play_btn = MenuButton("play_btn.png", "play", dy)

    dy += 100
    revive_btn = MenuButton("revive_btn.png", "revive", dy)
    buttons_group.add(revive_btn)
    dy += 100
    menu_btn = MenuButton("menu_btn.png", "menu", dy)
    dy += 100
    shop_btn = MenuButton("shop_btn.png", "shop", dy)
    dy += 100
    quit_btn = MenuButton("quit_btn.png", "quit", dy)

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
    x = car.rect.x
    game_running = True
    angle = 0
    max_speed = 7
    max_angle = 5
    accel_x = x_change = 0

    while game_running:
        # screen.fill((0, 0, 0))
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

                    return main_menu()
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    accel_x = 0

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

        [road.update() for road in roads]
        [coin.update() for coin in coins]
        [traffic.update() for traffic in traffics]
        road_group.draw(screen)
        coins_group.draw(screen)
        traffics_group.draw(screen)
        car.update(x, angle)
        car_group.draw(screen)

        if not car.is_alive:
            write_coins()
            write_lives()
            dist = car.distance
            car.__init__()
            car.distance = dist
            [traffic.__init__() for traffic in traffics]
            game_running = False
            death_screen()

        clock.tick(fps)
        pygame.display.flip()

    main_menu()


road_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()
traffics_group = pygame.sprite.Group()
car_group = pygame.sprite.Group()

car = Car()
roads = [Road(0), Road(-height)]
coins = [Coin(), Coin(), Coin()]
traffics = [Traffic(), Traffic(), Traffic()]

[road_group.add(road) for road in roads]
[coins_group.add(coin) for coin in coins]
[traffics_group.add(traffic) for traffic in traffics]

car_group.add(car)

coins_counter = CoinsCounter(get_coins())
lives_counter = LivesCounter(get_lives())

if __name__ == '__main__':
    show_intro()
    main_menu()

# # Created by Sergey Yaksanov at 10.12.2020
# Copyright © 2020 Yakser. All rights reserved.
