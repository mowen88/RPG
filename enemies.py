import pygame, random
from math import atan2, degrees, pi
from entities import Entity


class Enemy(Entity):
	def __init__(self, character_name, game, zone, pos, groups):
		super().__init__(game, zone, pos, groups)

		self.game = game
		self.zone = zone
		self.angle = None

		self.image = pygame.image.load('img/enemies/samurai/idle/0.png').convert_alpha()
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.game.SCALE, self.image.get_height() * self.game.SCALE))
		self.left_image = pygame.transform.flip(self.image, True, False)
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(-24, -8)
		self.alpha = 255

		# put all attributes from enemy dict into a variable below
		self.data = self.game.enemy_data[character_name]

		self.speed = random.uniform(self.data['speed'] * 0.8, self.data['speed'] * 1.2)
		self.health = self.data['health']
		self.damage = self.data['damage']
		self.resistance = self.data['resistance']
		self.invincible_time = self.data['invincible_time']
		self.knockback_time = self.data['knockback_time']

		self.attack_type = self.data['attack_type']
		self.windup_time = self.data['windup_time']
		self.attack_speed = self.data['attack_speed']
		self.attack_radius = self.data['attack_radius']
		self.alert_radius = self.data['alert_radius']

		self.state = 'idle'
		#self.state = random.choice(['left_idle', 'right_idle'])
		self.import_imgs(character_name)

	def import_imgs(self, name):
		character_path = f'img/enemies/{name}/'
		self.animations = {'idle':[], 'moving': [], 'attack': [], 'windup': [], 'hit': [], 'death': []}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = self.game.import_folder(full_path)

	def get_distance_direction_and_angle(self, target):
		enemy_vec = pygame.math.Vector2(self.rect.center)
		target_vec = pygame.math.Vector2(target.rect.center)
		distance = (target_vec - enemy_vec).magnitude()
		
		if (target_vec - enemy_vec) != pygame.math.Vector2(0,0):
		    direction = (target_vec - enemy_vec).normalize()
		else:
			direction = pygame.math.Vector2(1,1)
			
		dx = self.rect.centerx - (target.rect.x)
		dy = self.rect.centery - (target.rect.y)

		radians = atan2(-dx, dy)
		radians %= 2*pi
		angle = int(degrees(radians))

		return(distance, direction, angle)

	def attack_committed(self, target):
		self.state = 'windup'
		self.animate('end_on_last_frame')
		self.vec = pygame.math.Vector2()
		self.windup_counter += 1
		if self.windup_counter > self.windup_time:
			self.state = 'attack'
			self.attack(target)
			self.speed = self.speed
			self.windup_counter = 0

	def attack(self, target):
		self.attacking = True
		self.frame_index = 0
		self.angle = self.get_distance_direction_and_angle(target)[2]
		self.vec = self.get_distance_direction_and_angle(target)[1] * self.attack_speed

	def get_state(self, target):
		distance = self.get_distance_direction_and_angle(target)[0]

		if not self.zone.player.alive:
			self.state = 'idle'

		elif not self.alive:
			self.state = 'death'

		elif self.invincible:
			self.state = 'hit'

		elif distance <= self.attack_radius:
			self.state = 'attack'

		elif distance <= self.alert_radius:
			self.state = 'moving'
			
		else:
			self.state = 'idle'

	def animate(self, animation_type):

		animation = self.animations[self.state]
		self.frame_index += self.frame_rate

		if self.frame_index >= len(animation) -1:
			if self.attacking:
				self.attacking = False
			if not self.alive:
				self.frame_index = len(animation) -1
			if animation_type == 'loop':
				self.frame_index = 0
			else:
				self.frame_index = len(animation) -1

		if self.alive:
			if self.attacking:
				if self.rect.x > self.zone.player.rect.x:
					self.image = animation[int(self.frame_index)]
				elif self.rect.x < self.zone.player.rect.x:
					self.image = pygame.transform.flip(animation[int(self.frame_index)], True, False)
			elif self.rect.x < self.zone.player.rect.x:
				self.image = animation[int(self.frame_index)]

			else:
				self.image = pygame.transform.flip(animation[int(self.frame_index)], True, False)

		else:
			if self.knockback_direction == 'right':
				self.image = animation[int(self.frame_index)]
			else:
				self.image = pygame.transform.flip(animation[int(self.frame_index)], True, False)
			

		self.rect = self.image.get_rect(center = self.hitbox.center)


	def action(self, target):
		if not self.alive:
			self.state = 'death'
			self.vec = self.get_distance_direction_and_angle(target)[1] * self.attack_speed
			self.vec.x *= -1
			self.vec.y *= -1
			if self.knockback_timer == self.knockback_time:
				self.vec = pygame.math.Vector2()

		elif self.state == 'attack' and not self.attacking:
			self.attack_committed(target)
			self.windup_counter == 0
			
		elif self.attacking:
			self.state = 'attack'
			self.deceleration_x(0.5)
			self.deceleration_y(0.5)

		elif self.state == 'moving':
			self.windup_counter = 0
			self.vec = self.get_distance_direction_and_angle(target)[1] * self.speed
			
		else:
			self.vec = pygame.math.Vector2()

	def update(self):
		if not self.attacking:
			self.move(self.speed)
		else:
			self.move(self.attack_speed)

		if self.state == 'death':
			self.alpha -= 1
			self.image.set_alpha(self.alpha)

		if self.alpha <= 0:
			self.kill()

	def enemy_update(self, target):
		self.run_invincibility_time()
		self.run_knockback_time()
		if self.state == 'windup' or not self.alive:
			self.animate('end_on_last_frame')
		else:
			self.animate('loop')
		self.get_state(target)
		self.action(target)
		
		
	
