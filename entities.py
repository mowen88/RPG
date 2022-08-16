import pygame

class Entity(pygame.sprite.Sprite):
	def __init__(self, game, zone, pos, groups):
		super().__init__(groups)

		self.frame_index = 0
		self.frame_rate = 0.2

		self.vec = pygame.math.Vector2()

	def deceleration_y(self, speed):
		# deccelerating the player in y direction
		if self.vec.y > 0:
			self.vec.y -= speed
			if self.vec.y <= 0:
				self.vec.y = 0
		elif self.vec.y < 0:
			self.vec.y += speed
			if self.vec.y >= 0:
				self.vec.y = 0

	def deceleration_x(self, speed):
		# deccelerating the player in x direction
		if self.vec.x > 0:
			self.vec.x -= speed
			if self.vec.x <= 0:
				self.vec.x = 0
		elif self.vec.x < 0:
			self.vec.x += speed
			if self.vec.x >= 0:
				self.vec.x = 0

	def move(self, speed):
		if self.vec.magnitude() >= speed:
			self.vec = self.vec.normalize() * speed

		self.hitbox.x += self.vec.x 
		self.collisions('x')
		self.hitbox.y += self.vec.y 
		self.collisions('y')
		self.rect.center = self.hitbox.center

	def collisions(self, direction):

		self.ramp_collisions()
		
		for sprite in self.zone.obstacle_sprites:
			if sprite.hitbox.colliderect(self.hitbox):
				
				if direction == 'x':
					if self.vec.x > 0:
						self.hitbox.right = sprite.rect.left
					if self.vec.x < 0:
						self.hitbox.left = sprite.rect.right

					# if self.vec.y < 0:
					# 	self.hitbox.topright = sprite.rect.right - y_pos
					# 	print(y_pos)

				elif direction == 'y':
					if self.vec.y < 0:
						self.hitbox.top = sprite.rect.bottom
					if self.vec.y > 0:
						self.hitbox.bottom = sprite.rect.top

	def ramp_collisions(self):
		for sprite in self.zone.all_ramp_sprites:
			if sprite.rect.colliderect(self.hitbox):

				if sprite in self.zone.ramp_left_down_sprites:
					rel_x = self.hitbox.x - sprite.hitbox.x
					rel_y = self.hitbox.y - sprite.hitbox.y

					target_y = sprite.hitbox.top - rel_x
					target_x = sprite.hitbox.left - rel_y

					if self.hitbox.bottom >= target_y:
						self.hitbox.bottom = target_y
						self.hitbox.right = target_x

				elif sprite in self.zone.ramp_right_down_sprites:
					rel_x = self.hitbox.right - sprite.hitbox.right
					rel_y = self.hitbox.top - sprite.hitbox.top

					target_y = sprite.hitbox.top + rel_x
					target_x = sprite.hitbox.right + rel_y

					if self.hitbox.bottom >= target_y:
						self.hitbox.bottom = target_y
						self.hitbox.left = target_x

				elif sprite in self.zone.ramp_left_up_sprites:

					rel_x = sprite.hitbox.x - self.hitbox.x
					rel_y = sprite.hitbox.y - self.hitbox.y
					
					target_y = sprite.hitbox.top - rel_x
					target_x = sprite.hitbox.left - rel_y

					if self.hitbox.top <= target_y:
						self.hitbox.top = target_y
						self.hitbox.left = target_x

				elif sprite in self.zone.ramp_right_up_sprites:

					rel_x = sprite.hitbox.x - self.hitbox.x
					rel_y = sprite.hitbox.y - self.hitbox.y
					
					target_y = sprite.hitbox.top + rel_x
					target_x = sprite.hitbox.left + rel_y
					

					if self.hitbox.top <= target_y:
						self.hitbox.top = target_y
						self.hitbox.left = target_x