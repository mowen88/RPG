import pygame, math, random
		
class Melee(pygame.sprite.Sprite):
	def __init__(self, game, zone, groups, surf):
		super().__init__(groups)

		self.zone = zone
		self.game = game
		self.vec = pygame.math.Vector2()
		self.vec = self.zone.player.vec
		self.frames = self.game.import_folder(str(self.zone.player.sword_type))
		self.opposite_frames = self.game.import_folder(str(self.zone.player.sword_type)+'_2')
		self.frame_index = 0
		self.frame_rate = 0.25
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = self.zone.player.rect.center)

	def animate(self):

		self.frame_index += self.frame_rate
		if self.frame_index >= len(self.frames) -1 or self.zone.player.dashing:
			self.kill()
			self.zone.player.attacking = False
			if self.zone.player.attack_count == self.zone.player.max_chain_attacks:
				self.zone.player.attack_count = 0

		if self.zone.player.attack_count % 2 == 0:
			self.image = self.opposite_frames[int(self.frame_index)]
		else:
			self.image = self.frames[int(self.frame_index)]
			

	def update(self):
		self.zone.display_surf.blit(pygame.Surface((28, 28)), self.rect)
		self.animate()

		# self.image = pygame.transform.rotate(self.image, 360 - self.zone.player.angle)

		if self.zone.player.angle >= 45 and self.zone.player.angle <= 135:
			self.rect = self.image.get_rect(midleft = (self.zone.player.rect.left + (self.zone.player.image.get_width()//4), self.zone.player.rect.top + (self.zone.player.image.get_height()//2)))

		elif self.zone.player.angle > 135 and self.zone.player.angle < 225:
			self.image = pygame.transform.rotate(self.image, 270)
			self.rect = self.image.get_rect(midtop = (self.zone.player.rect.left + (self.zone.player.image.get_width()//2), self.zone.player.rect.top + (self.zone.player.image.get_height()//4)))

		elif self.zone.player.angle >= 225 and self.zone.player.angle <= 315:
			self.image = pygame.transform.rotate(self.image, 180)
			self.rect = self.image.get_rect(midright = (self.zone.player.rect.right - (self.zone.player.image.get_width()//4), self.zone.player.rect.top + (self.zone.player.image.get_height()//2)))

		else:
			self.image = pygame.transform.rotate(self.image, 90)
			self.rect = self.image.get_rect(midbottom = (self.zone.player.rect.right - (self.zone.player.image.get_width()//2), self.zone.player.rect.bottom - (self.zone.player.image.get_height()//4)))


class DashParticles(pygame.sprite.Sprite):
	def __init__(self, game, zone, groups, surf):
		super().__init__(groups)

		self.zone = zone
		self.game = game
		self.vec = pygame.math.Vector2()
		self.vec = self.zone.player.vec
		self.frames = self.game.import_folder('img/particles/dash')
		self.frame_index = 0
		self.frame_rate = 0.4
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = self.zone.player.rect.center)
	
	def animate(self):

		self.frame_index += self.frame_rate
		if self.frame_index >= len(self.frames) -1:
			self.kill()
			self.zone.player.dashing = False
			self.zone.player.speed /= self.zone.player.dash_speed_multiplier
			if self.zone.player.dash_count == self.zone.player.max_chain_dashes:
				self.zone.player.dash_count = 0
		self.image = self.frames[int(self.frame_index)]
			
	def update(self):
		self.animate()


class Projectile(pygame.sprite.Sprite):
	def __init__(self, game, zone, groups, surf):
		super().__init__(groups)

		self.zone = zone
		self.game = game
		self.frames = self.game.import_folder('img/projectile')
		self.frame_index = 0
		self.frame_rate = 0.3
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = (self.zone.player.rect.center))
		self.vec = self.zone.player.get_distance_direction_and_angle()[1]
		self.speed = 12


	def animate(self):

		self.frame_index += self.frame_rate
		if self.frame_index >= len(self.frames) -1:
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def collide_obstacles(self):
		for sprite in self.zone.obstacle_sprites:
			if sprite.rect.colliderect(self.rect):
				self.kill()

	def update(self):
		self.vec = self.vec.normalize() * self.speed
		self.rect[0] += self.vec[0]
		self.rect[1] += self.vec[1]
		self.animate()
		self.collide_obstacles()

class DashTrailFade(pygame.sprite.Sprite):
	def __init__(self, game, zone, groups, surf, size, colour, pos):
		super().__init__(groups)

		self.zone = zone
		self.game = game
		self.image = pygame.Surface((size, size))
		self.image.fill((colour))
		self.alpha = 150
		self.rect = self.image.get_rect(center = pos)

	def update(self):
		self.alpha -= 10
		self.image.set_alpha(self.alpha)

class BloodTrail(pygame.sprite.Sprite):
	def __init__(self, game, zone, groups, surf, pos):
		super().__init__(groups)

		self.zone = zone
		self.game = game
		self.choice = random.choice((0, 1, 2))
		self.image = pygame.image.load(f'img/particles/blood_puddles/{self.choice}.png').convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE ) )
		self.alpha = 200
		self.rect = self.image.get_rect(center = pos)

	def update(self):
		self.alpha -= 0.5
		self.image.set_alpha(self.alpha)
		if self.alpha <= 0:
			self.kill()


class Blood(pygame.sprite.Sprite):
	def __init__(self, game, zone, groups, surf, pos):
		super().__init__(groups)

		self.zone = zone
		self.game = game
		self.choice = random.choice((0, 1))
		self.frames = self.game.import_folder(f'img/particles/blood_spray/{self.choice}')
		self.frame_index = 0
		self.frame_rate = 0.3
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center = (pos))

	def animate(self):
		self.frame_index += self.frame_rate
		if self.frame_index >= len(self.frames) -1:
			self.kill()
		self.image = self.frames[int(self.frame_index)]

	def update(self):
		self.animate()
		

		
