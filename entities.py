import pygame

class Entity(pygame.sprite.Sprite):
	def __init__(self, game, zone, pos, groups):
		super().__init__(groups)

		self.frame_index = 0
		self.frame_rate = 0.2

		self.vec = pygame.math.Vector2()
		
		self.alive = True
		self.knockback_direction = None
		self.attacking = False
		self.dashing = False

		self.hit = False
		self.invincible = False
		self.windup_counter = 0
		self.invincibility_timer = 0
		self.knockback_timer = 0

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

	def get_off_edge(self):
		self.on_edge = False

	def run_invincibility_time(self):
		if self.invincible:
			self.invincibility_timer += 1
			if self.invincibility_timer >= self.invincible_time:
				self.invincible = False
				self.invincibility_timer = 0

	def run_knockback_time(self):
		if not self.alive:
			self.knockback_timer += 1
			if self.knockback_timer >= self.knockback_time:
				self.knockback_timer = self.knockback_time

	def enemy_self_collisions(self, direction):
		enemies = []
		for sprite in self.zone.enemy_sprites:
			enemies.append(sprite)

		for i, enemy1 in enumerate(enemies):
		    for enemy2 in enemies[i+1:]:
		        if enemy1.hitbox.colliderect(enemy2.hitbox) and enemy2.alive:
		        	if direction == 'x':
		        		if enemy1.vec.x != 0:
		        			enemy1.vec.x = 0
		        		
		        	elif direction == 'y':
		        		if enemy1.vec.y != 0:
		        			enemy1.vec.y = 0
		        		
	
	def collisions(self, direction):
		self.enemy_self_collisions(direction)
		self.enemy_and_player_collision(direction)

		if not self.dashing:
			self.ramp_collisions()
			for sprite in self.zone.obstacle_sprites:
				if sprite.hitbox.colliderect(self.hitbox):

					if direction == 'x':
						if self.vec.x > 0:
							self.hitbox.right = sprite.hitbox.left
							self.on_edge = True
						if self.vec.x < 0:
							self.hitbox.left = sprite.hitbox.right
							self.on_edge = True

					elif direction == 'y':
						if self.vec.y < 0:
							self.hitbox.top = sprite.hitbox.bottom
							self.on_edge = True
						if self.vec.y > 0:
							self.hitbox.bottom = sprite.hitbox.top
							self.on_edge = True

	def enemy_and_player_collision(self, direction):
		# player blocked by enemies
		for sprite in self.zone.enemy_sprites:
			if sprite.hitbox.colliderect(self.zone.player.hitbox) and not self.zone.player.dashing and not sprite.state == 'attack' and sprite.alive:
				if direction == 'x':
					if self.zone.player.vec.x > 0:
						self.zone.player.hitbox.right = sprite.hitbox.left
					if self.zone.player.vec.x < 0:
						self.zone.player.hitbox.left = sprite.hitbox.right
				
				elif direction == 'y':
					if self.zone.player.vec.y < 0:
						self.zone.player.hitbox.top = sprite.hitbox.bottom
					if self.zone.player.vec.y > 0:
						self.zone.player.hitbox.bottom = sprite.hitbox.top

		
	def ramp_collisions(self):
		for sprite in self.zone.all_ramp_sprites:

			if sprite.rect.colliderect(self.hitbox):

				if sprite in self.zone.ramp_left_down_sprites:
					rel_x = self.hitbox.left - sprite.hitbox.left
					rel_y = self.hitbox.top - sprite.hitbox.top

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