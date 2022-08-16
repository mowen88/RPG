import pygame

class Tile(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.image = surf
		self.image = pygame.transform.scale(self.image, (self.game.TILESIZE, self.game.TILESIZE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-8, -8)

class Ramp(pygame.sprite.Sprite):
	def __init__(self, game, pos, groups, surf):
		super().__init__(groups)
		self.game = game
		self.image = surf
		self.image = pygame.transform.scale(self.image, (self.game.TILESIZE, self.game.TILESIZE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-26, -26) # ideal amount to stop player 'jumping' too much when hitting the first ramp on the edge - do not change

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

	# def update(self):
	# 	self.collide_stairs()




	

