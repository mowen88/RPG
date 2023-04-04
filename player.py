import pygame
from math import atan2, degrees, pi
from entities import Entity

class Player(Entity):
	def __init__(self, game, zone, pos, groups):
		super().__init__(game, zone, pos, groups)
		self.game = game
		self.zone = zone
		self.image = pygame.image.load('img/monk - Copy/down/0.png').convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-10, -25)

		self.mx, self.my = (0,0)

		# player variables
		self.invincible_time = 20
		self.invincibility_timer = 0
		self.knockback_time = 0

		self.on_edge = False
		self.speed = 5
		self.speed_on_stairs = 3
		self.dash_speed_multiplier = 5
		self.angle = None
		self.acceleration = 0.5
		self.attack_deceleration = 0.5

		# melee
		self.sword_type = 'img/small_sword'
		self.sword_upgraded = False
		self.sword_upgrade_timer = 0
		self.sword_upgrade_time = 200
		self.max_kills_to_sword_upgrade = 4
		self.kills = 0

		self.attacking = False
		self.can_attack = True
		self.next_attack_pending = False
		self.attack_time = None
		self.attack_count = 0
		self.max_chain_attacks = 3
		self.attack_cooldown = 500
		
		self.attack_count_reset = True
		self.last_attack_time = None
		self.last_attack_cooldown = 700

		#dashing
		self.max_chain_dashes = 3
		self.dashing = False
		self.can_dash = True
		self.dash_time = None
		self.dash_count = 0
		self.dash_cooldown = 400

		self.dash_count_reset = True
		self.last_dash_time = None
		self.last_dash_cooldown = 600
		self.dash_start_pos = self.hitbox.center

		self.import_imgs()
		self.state = 'down'

	def import_imgs(self):
		character_path = f'img/monk - Copy/'
		self.animations = {'up':[], 'down':[], 'left':[], 'right':[], 'up_idle':[], 'down_idle':[], 'left_idle':[], 'right_idle':[], 
		'up_accelerating':[], 'down_accelerating':[], 'left_accelerating':[], 'right_accelerating':[],
		'right_attack':[], 'left_attack':[], 'up_attack':[], 'down_attack':[], 'right_attack_2':[], 'left_attack_2':[], 'up_attack_2':[], 'down_attack_2':[],
		'left_hit':[], 'right_hit':[], 'left_death':[], 'right_death':[]}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = self.game.import_folder(full_path)

	def get_state(self):
		if self.alive:
		
			if self.vec.x == 0 and self.vec.y == 0:
				if not 'idle' in self.state:
					self.state = self.state + '_idle'
					if 'right_hit' in self.state and '_idle' in self.state:
						self.state = 'right_hit'
					elif 'left_hit' in self.state and '_idle' in self.state:
						self.state = 'left_hit'

				if not self.invincible and self.alive:
					self.state = self.state.replace('left_hit','left_idle')
					self.state = self.state.replace('right_hit','right_idle')


			if self.vec.x > 0 and self.vec.y > 0 or self.vec.x > 0 and self.vec.y < 0:
				self.state = 'right'
			elif self.vec.x < 0 and self.vec.y < 0 or self.vec.x < 0 and self.vec.y > 0:
				self.state = 'left'

			if self.vec.x != 0 and self.vec.y == 0:
				if self.vec.x > 0 and self.vec.x < self.speed:
					self.state = 'right_accelerating'
				elif self.vec.x >= self.speed:
					self.state = 'right'
				elif self.vec.x < 0 and self.vec.x > -self.speed:
					self.state = 'left_accelerating'
				elif self.vec.x <= -self.speed:
					self.state = 'left'

			if self.vec.y != 0 and self.vec.x == 0:
				if self.vec.y > 0 and self.vec.y < self.speed:
					self.state = 'down_accelerating'
				elif self.vec.y >= self.speed:
					self.state = 'down'
				elif self.vec.y < 0 and self.vec.y > -self.speed:
					self.state = 'up_accelerating'
				elif self.vec.y <= -self.speed:
					self.state = 'up'

			if self.attacking:
				if self.get_distance_direction_and_angle()[2] > 45 and self.get_distance_direction_and_angle()[2] <= 135:
					self.state = 'right_attack'
					if self.attack_count % 2 == 0:
						self.state = self.state.replace('_attack','_attack_2')
				elif self.get_distance_direction_and_angle()[2] > 135 and self.get_distance_direction_and_angle()[2] <= 225:
					self.state = 'down_attack'
					if self.attack_count % 2 == 0:
						self.state = self.state.replace('_attack','_attack_2')
				elif self.get_distance_direction_and_angle()[2] > 225 and self.get_distance_direction_and_angle()[2] <= 315:
					self.state = 'left_attack'
					if self.attack_count % 2 == 0:
						self.state = self.state.replace('_attack','_attack_2')
				else:
					self.state = 'up_attack'
					if self.attack_count % 2 == 0:
						self.state = self.state.replace('_attack','_attack_2')


			elif ('_attack' and '_idle') in self.state:
				self.state = self.state.replace('_attack','')
				self.state = self.state.replace('_2','')

			if ('_accelerating' or '_idle') in self.state:
				self.state = self.state.replace('_accelerating','')

		elif self.state == 'right_hit':
			self.state = 'right_death'	
		elif self.state == 'left_hit':
			self.state = 'left_death'		

	def animate(self, animation_type, animation_speed):
		animation = self.animations[self.state]
		self.frame_index += animation_speed

		if self.frame_index >= len(animation) -1:
			if animation_type == 'loop':
				self.frame_index = 0
			else:
				self.frame_index = len(animation) -1
					
		self.image = animation[int(self.frame_index)]

	def melee(self):

		if self.game.actions['left_click'] and (self.attack_count > 0 and self.attack_count < self.max_chain_attacks):
			self.next_attack_pending = True

		elif self.game.actions['left_click'] and not self.attacking and not self.dashing:
			if self.can_attack:
				self.angle = self.get_distance_direction_and_angle()[2]
				self.vec = self.get_distance_direction_and_angle()[1] * self.speed
				self.attacking = True
				self.attack_count += 1
				self.attack_count_reset = False
				self.attack_time = pygame.time.get_ticks()
				self.zone.create_melee()

		if self.attack_count == self.max_chain_attacks:
			self.last_attack_time = pygame.time.get_ticks()
			self.can_attack = False

		if self.next_attack_pending and not self.attacking:
			self.angle = self.get_distance_direction_and_angle()[2]
			self.vec = self.get_distance_direction_and_angle()[1] * self.speed
			self.attacking = True
			self.attack_count += 1
			self.attack_count_reset = False
			self.attack_time = pygame.time.get_ticks()
			self.zone.create_melee()
			self.next_attack_pending = False

		if self.sword_upgraded:
			self.sword_type = 'img/big_sword'

	def dash(self):
		
		if self.game.actions['right_click'] and not self.dashing:
			if self.can_dash:
				self.dash_start_pos = self.hitbox.center
				self.speed *= self.dash_speed_multiplier
				self.vec = self.get_distance_direction_and_angle()[1] * self.speed
				self.dashing = True
				self.dash_count += 1
				self.dash_count_reset = False
				self.dash_time = pygame.time.get_ticks()
				self.zone.create_dash_particles()
		if self.dash_count == self.max_chain_dashes:
			self.last_dash_time = pygame.time.get_ticks()
			self.can_dash = False

	def up_stairs(self, keys):
		if pygame.sprite.spritecollide(self, self.zone.stairs_left_up_sprites, False, pygame.sprite.collide_rect_ratio(0.6)):
			if keys[pygame.K_LEFT] or keys[pygame.K_a]:	
				if keys[pygame.K_UP]:
					self.vec.x = -1
				elif keys[pygame.K_DOWN]:
					self.vec.y = -1
				else:  
					self.vec.x = -self.speed_on_stairs
					self.vec.y = self.vec.x 
			elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				if keys[pygame.K_DOWN]:
					self.vec.x = 2
				elif keys[pygame.K_UP]:
					self.vec.y = 2
				else: 
					self.vec.x = self.speed_on_stairs
					self.vec.y = self.vec.x 

		elif pygame.sprite.spritecollide(self, self.zone.stairs_right_up_sprites, False, pygame.sprite.collide_rect_ratio(0.6)):
			if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				if keys[pygame.K_DOWN]:
					self.vec.y = -1
				elif keys[pygame.K_UP]:
					self.vec.x = 2
				else: 
					self.vec.x = self.speed_on_stairs
					self.vec.y = -self.vec.x 

			elif keys[pygame.K_LEFT] or keys[pygame.K_a]:	
				if keys[pygame.K_UP]:
					self.vec.y = 2
				elif keys[pygame.K_DOWN]:
					self.vec.x = -1
				else:  
					self.vec.x = -self.speed_on_stairs
					self.vec.y = -self.vec.x 

	def input(self):

		keys = pygame.key.get_pressed()
		mouse = pygame.mouse.get_pressed(num_buttons=5)
		self.mx, self.my = pygame.mouse.get_pos()		

		if self.game.actions['space']:
			self.zone.create_projectile()

		if not self.attacking and not self.dashing:
			
			# accelerating the player in y direction
			if keys[pygame.K_UP]:
				self.vec.y -= self.acceleration
				if self.vec.y <= -self.speed:
					self.vec.y = -self.speed
			elif keys[pygame.K_DOWN]:
				self.vec.y += self.acceleration
				if self.vec.y >= self.speed:
					self.vec.y = self.speed	
			else:
				self.deceleration_y(self.acceleration)

			# accelerating the player in x direction
			if keys[pygame.K_LEFT]:
				self.vec.x -= self.acceleration
				if self.vec.x <= -self.speed:
					self.vec.x = -self.speed	
			elif keys[pygame.K_RIGHT]:
				self.vec.x += self.acceleration
				if self.vec.x >= self.speed:
					self.vec.x = self.speed	
			else:
				self.deceleration_x(self.acceleration)

			self.up_stairs(keys)

		elif self.attacking:
			# deccelerating the player
			self.deceleration_y(self.attack_deceleration)
			self.deceleration_x(self.attack_deceleration)

		self.melee()
		self.dash()		
			
	def cooldowns(self):

		current_time = pygame.time.get_ticks()

		# sword cooldowns
		if not self.can_attack:
			if current_time - self.last_attack_time >= self.last_attack_cooldown:
				self.can_attack = True

		if not self.attack_count_reset and  self.can_attack:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.attack_count_reset = True
				self.attack_count = 0

		# dash cooldowns
		if not self.can_dash:
			if current_time - self.last_dash_time >= self.last_dash_cooldown:
				self.can_dash = True

		if not self.dash_count_reset and self.can_dash:
			if current_time - self.dash_time >= self.dash_cooldown:
				self.dash_count_reset = True
				self.dash_count = 0

	def run_invincibility_time(self):
		if self.invincible:
			self.invincibility_timer += 1
			if self.invincibility_timer >= self.invincible_time:
				self.invincible = False
				self.invincibility_timer = 0

	def run_upgraded_sword_time(self):
		if self.kills >= self.max_kills_to_sword_upgrade:
			self.sword_upgraded = True
			self.sword_type = 'img/big_sword'
		if self.sword_upgraded:
			self.sword_upgrade_timer += 1
			if self.sword_upgrade_timer >= self.sword_upgrade_time:
				self.sword_upgraded = False
				self.sword_type = 'img/small_sword'
				self.sword_upgrade_timer = 0
				self.kills = 0

	def get_distance_direction_and_angle(self):
		player_vec = pygame.math.Vector2((self.rect.center[0] - self.zone.visible_sprites.offset[0], self.rect.center[1]  - self.zone.visible_sprites.offset[1]))
		mouse_vec = pygame.math.Vector2(self.mx, self.my)
		distance = (mouse_vec - player_vec).magnitude()
		if (mouse_vec - player_vec) != pygame.math.Vector2(0,0):
		    direction = (mouse_vec - player_vec).normalize()
		else:
			direction = pygame.math.Vector2(1,1)
		
		dx = self.rect.centerx - (self.mx + self.zone.visible_sprites.offset[0])
		dy = self.rect.centery - (self.my + self.zone.visible_sprites.offset[1])

		radians = atan2(-dx, dy)
		radians %= 2*pi
		angle = int(degrees(radians))

		return(distance, direction, angle)

	def update(self):
		if not self.zone.cutscene_running:
			self.input()
		if self.invincible:
			self.vec = pygame.math.Vector2()
		self.run_invincibility_time()
		self.run_upgraded_sword_time()
		self.get_off_edge()
		self.cooldowns()
		self.get_state()
		if self.alive:
			self.animate('loop', self.frame_rate)

		elif self.zone.melee_sprite:
			self.zone.melee_sprite.kill()
		self.move(self.speed)
		self.game.reset_keys()


