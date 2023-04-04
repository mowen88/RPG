import pygame

class Tile(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.image = surf
		self.image = pygame.transform.scale(self.image, (self.game.TILESIZE, self.game.TILESIZE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect

class SpawnPoint(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.image = surf
		self.image = pygame.transform.scale(self.image, (self.game.TILESIZE, self.game.TILESIZE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect

class Box(pygame.sprite.Sprite):
	def __init__(self, game, zone, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.zone = zone
		self.frames = self.game.import_folder('img/box')
		self.frame_index = 0
		self.frame_rate = 0.3
		self.image = surf
		self.vec = pygame.math.Vector2()
		self.image = pygame.transform.scale(self.image, (self.game.TILESIZE, self.game.TILESIZE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-5, 0)

	def animate(self):
		self.frame_index += self.frame_rate
		if self.frame_index >= len(self.frames) -1:
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def update(self):
		self.animate()
		self.vec.x = 1
		self.rect.x += self.vec.x
		self.rect.y += self.vec.y
		

class Ramp(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.image = surf
		self.image = pygame.transform.scale(self.image, (self.game.TILESIZE, self.game.TILESIZE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-25, -25) # ideal amount to stop player 'jumping' too much when hitting the first ramp on the edge - do not change

class Stairs(pygame.sprite.Sprite):
	def __init__(self, game, zone, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.zone = zone
		self.image = surf
		self.image = pygame.transform.scale(self.image, (self.game.TILESIZE, self.game.TILESIZE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-8, -8)

	def collide_stairs(self):
		if pygame.sprite.spritecollide(self.zone.player, self.zone.stairs_right_up_sprites, False):
			self.zone.player.on_stairs_right_up = True

		elif pygame.sprite.spritecollide(self.zone.player, self.zone.stairs_right_down_sprites, False):
			self.zone.player.on_stairs_right_down = True

		elif pygame.sprite.spritecollide(self.zone.player, self.zone.stairs_left_down_sprites, False):
			self.zone.player.on_stairs_left_down = True
		
		elif pygame.sprite.spritecollide(self.zone.player, self.zone.stairs_left_up_sprites, False):
			self.zone.player.on_stairs_left_up = True
		else:
			self.zone.player.on_stairs_left_up, self.zone.player.on_stairs_right_up, self.zone.player.on_stairs_right_down,\
			self.zone.player.on_stairs_left_down = False, False, False, False






	

