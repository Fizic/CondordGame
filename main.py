import pygame
import random
from sprites import *
import os


class Game:
    def __init__(self):
        self.settings()
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_name = pygame.font.match_font('arial')
        self.load_data()

    def settings(self):
        """
        Задание начальных переменных
        :return: None
        """
        self.width = 1920
        self.height = 1080
        self.fps = 60

    def load_data(self):
        """
        Загрузка всех файлов, необходимых для проекта
        :return:
        """
        self.dir = os.path.dirname(__file__)
        self.fon = pygame.transform.scale(self.load_image('1.gif'),
                                          (self.width, self.height))

        img_dir = os.path.join(self.dir, 'img')
        self.player_1_sprite = LoadImage(os.path.join('img', 'player1_sprite.png'))
        self.player_2_sprite = LoadImage(os.path.join('img', 'player2_sprite.png'))
        self.blocks_sprite = LoadImage(
            os.path.join('img', 'platformIndustrial_sheet2.png'))
        self.weapon_sprite = LoadImage(
            os.path.join('img', 'Ak47 Custom Sheet.png'))

    def new(self):
        names = ['map.txt', 'map1.txt']
        with open(os.path.join(self.dir, random.choice(names)), 'r') as map1:
            self.blocks = map1.readlines()
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.platforms = pygame.sprite.Group()
        self.guns = pygame.sprite.Group()
        self.bullet_player_1 = pygame.sprite.Group()
        self.bullet_player_2 = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.player_1 = Player(self, self.player_1_sprite, 100)
        self.player_2 = Player(self, self.player_2_sprite, 1700)
        for y_cord, block_s in enumerate(self.blocks):
            for x_cord, block in enumerate(block_s):
                if block == '#':
                    Block(self, x_cord * 70 - 95, y_cord * 70 - 25)

        Weapon(self, 100, 500)
        Weapon(self, 900, 700)
        self.mob_timer = 0
        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(self.fps)
            self.events()
            self.update()
            self.draw()
        pygame.mixer.music.fadeout(500)

    def update(self):
        self.all_sprites.update()
        self.control(self.player_1, self.bullet_player_2)
        self.control(self.player_2, self.bullet_player_1)
        if len(self.platforms) == 0:
            self.playing = False

    def control(self, player, gr_plr):
        """
        Контроль за основными столкновениями
        :param player: объект игрока
        :param gr_plr: группа со всеми объектами
        :return: None
        """
        if player.vel.y > 0:
            intersections = pygame.sprite.spritecollide(player, self.platforms, False)
            if intersections:
                for lowest in intersections:
                    for intersection in intersections:
                        if intersection.rect.bottom > lowest.rect.bottom:
                            lowest = intersection
                        if player.pos.x < lowest.rect.right + 10 and player.pos.x > lowest.rect.left - 10:
                            if player.pos.y < lowest.rect.centery:
                                player.pos.y = lowest.rect.top
                                player.vel.y = 0
                                player.jumping = False

        intersections = pygame.sprite.spritecollide(player, gr_plr, False)
        if intersections:
            player.kill()
            self.playing = False

        intersections = pygame.sprite.spritecollide(player, self.guns, False)
        for weapon in intersections:
            if not player.have_gun and not weapon.collected:
                player.have_gun = True
                weapon.collected = True
                weapon.weapon_owner = player

        if len(self.platforms) == 0:
            self.playing = False

    def events(self):
        """

        :return:
        """
        self.player_1.animate()
        self.player_1.acc = vector(0, 0.7)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_1.acc.x = -1
        if keys[pygame.K_RIGHT]:
            self.player_1.acc.x = 1
        self.moving_player(self.player_1)
        self.player_2.animate()
        self.player_2.acc = vector(0, 0.7)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.player_2.acc.x = -1
        if keys[pygame.K_d]:
            self.player_2.acc.x = 1

        self.moving_player(self.player_2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player_1.jump()
                if event.key == pygame.K_w:
                    self.player_2.jump()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP0 and self.player_1.have_gun:
                    a = Bullet(self, self.player_1.rect.x + 48, self.player_1.rect.y + 64,
                               self.player_1.side, self.bullet_player_1)
                if event.key == pygame.K_v and self.player_2.have_gun:
                    a = Bullet(self, self.player_2.rect.x + 48, self.player_2.rect.y + 64,
                               self.player_2.side, self.bullet_player_2)

    def moving_player(self, obj_player):
        """
        Отвечает за перенос игрока с одной стороны на другую в случае выхода за карту
        :param obj_player: Объект игрока
        :return: None
        """

        obj_player.acc.x += obj_player.vel.x * -0.12
        obj_player.vel += obj_player.acc
        if abs(obj_player.vel.x) < 0.1:
            obj_player.vel.x = 0
        obj_player.pos += obj_player.vel + 0.5 * obj_player.acc
        if obj_player.pos.x > 1920 + obj_player.rect.width / 2:
            obj_player.pos.x = 0 - obj_player.rect.width / 2
        if obj_player.pos.x < 0 - obj_player.rect.width / 2:
            obj_player.pos.x = 1920 - obj_player.rect.width / 2

        obj_player.rect.midbottom = obj_player.pos

    def draw(self):
        """
        Отрисовка всех элементов игры
        :return:
        """
        self.screen.blit(self.fon, (0, 0))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def load_image(self, name, colorkey=None):
        file_name = os.path.join('img', name)
        if not os.path.isfile(file_name):
            print(f"Файл с изображением '{file_name}' не найден")
            sys.exit()
        image = pygame.image.load(file_name)
        return image

    def start_screen(self):
        fon = pygame.transform.scale(self.load_image('fon.png'),
                                     (self.width, self.height))
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        while True:
            for event in pygame.event.get():
                if not event.type == pygame.QUIT:
                    return

            pygame.display.flip()
            self.clock.tick(60)



g = Game()
g.start_screen()
while g.running:
    g.new()
    g.start_screen()

pygame.quit()
