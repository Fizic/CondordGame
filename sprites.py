"""
Файл со всеми классами для персонажей
"""
import pygame
vector = pygame.math.Vector2


class LoadImage:
    def __init__(self, filename):
        self.sprite = pygame.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height))
        image.blit(self.sprite, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (width // 2, height // 2))
        return image


class Player(pygame.sprite.Sprite):
    def __init__(self, game_obj, sprite, x):
        self.sprite = sprite
        self._layer = 2
        self.groups = game_obj.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game_obj = game_obj
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.have_gun = False
        self.image = self.standing_right
        self.rect = self.image.get_rect()
        self.rect.center = (100, 900)
        self.pos = vector(x, 900)
        self.vel = vector(0, 0)
        self.acc = vector(0, 0)
        self.side = 'r'

    def load_images(self):
        self.standing_right = self.sprite.get_image(1152, 256, 192, 256)
        self.standing_right.set_colorkey((0, 0, 0))
        self.standing_left = pygame.transform.flip(self.standing_right, True, False)
        self.walk_right = [self.sprite.get_image(1152, 512, 192, 256),
                           self.sprite.get_image(1344, 512, 192, 256),
                           self.sprite.get_image(1536, 512, 192, 256),
                           ]
        self.walk_left = []
        for frame in self.walk_right:
            frame.set_colorkey((0, 0, 0))
            self.walk_left.append(pygame.transform.flip(frame, True, False))
        self.jump_frame = self.sprite.get_image(1536, 0, 192, 256)
        self.jump_frame.set_colorkey((0, 0, 0))

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def jump(self):
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, self.game_obj.platforms, False)
        self.rect.y -= 2
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -22

    def update(self):
        pass

    def animate(self):
        now = pygame.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        if self.walking:
            if now - self.last_update > 180:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_left)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_right[self.current_frame]
                    self.side = 'r'
                else:
                    self.image = self.walk_left[self.current_frame]
                    self.side = 'l'
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                bottom = self.rect.bottom
                if self.side == 'r':
                    self.image = self.standing_right
                else:
                    self.image = self.standing_left
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        self.mask = pygame.mask.from_surface(self.image)


class Block(pygame.sprite.Sprite):
    def __init__(self, game_obj, x, y):
        self._layer = 1
        self.groups = game_obj.all_sprites, game_obj.platforms
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game_obj = game_obj
        self.image = self.game_obj.blocks_sprite.get_image(0, 0, 140, 140)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Bullet(pygame.sprite.Sprite):
    def __init__(self, game_obj, x, y, side, player_group):
        self.side = side
        self._layer = 1
        self.groups = game_obj.all_sprites, player_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game_obj = game_obj
        self.image = self.game_obj.blocks_sprite.get_image(160, 160, 20, 20)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y + 20

    def update(self):
        if self.side == 'r':
            self.rect.x += 50
        else:
            self.rect.x -= 50


class Weapon(pygame.sprite.Sprite):
    def __init__(self, game_obj, x, y):
        self.collected = False
        self.weapon_owner = ''
        self._layer = 2
        self.groups = game_obj.all_sprites, game_obj.guns
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game_obj = game_obj
        self.image = self.game_obj.weapon_sprite.get_image(0, 0, 236, 80)
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if self.collected:
            self.rect.x = self.weapon_owner.rect.x - 10
            self.rect.y = self.weapon_owner.rect.y + 85
            if self.weapon_owner.side == 'r':
                self.image = self.game_obj.weapon_sprite.get_image(0, 0, 236, 80)
            else:
                self.image = pygame.transform.flip(
                    self.game_obj.weapon_sprite.get_image(0, 0, 236, 80), True, False)
            self.image.set_colorkey((255, 255, 255))
