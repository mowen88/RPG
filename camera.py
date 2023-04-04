
import pygame, csv, random

class CameraGroup(pygame.sprite.Group):
	def __init__(self, game, zone):
		super().__init__()
		self.game = game
		self.zone = zone
		self.display_surf = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()
		self.screen_shaking = False
		
		self.scroll_delay = 32
		self.screen_transition_speed = 32 # ensure this is equal to or less than scroll delay above
		self.scroll_speed = 32

		self.get_zone_size()

		# load images
		self.bg_surf = pygame.image.load(f'zones/zone_{self.game.current_zone}/bg.png').convert_alpha()
		self.bg_surf = pygame.transform.scale(self.bg_surf, (self.zone_size[0], self.zone_size[1]))
		self.bg_surf1 = pygame.image.load(f'zones/zone_{self.game.current_zone}/bg1.png').convert_alpha()
		self.bg_surf1 = pygame.transform.scale(self.bg_surf1, (self.zone_size[0], self.zone_size[1]))
		self.bg_surf2 = pygame.image.load(f'zones/zone_{self.game.current_zone}/map.png').convert_alpha()
		self.bg_surf2 = pygame.transform.scale(self.bg_surf2, (self.zone_size[0], self.zone_size[1]))

		self.cloud_surf = pygame.image.load(f'maps/clouds.png').convert_alpha()
		self.cloud_surf = pygame.transform.scale(self.cloud_surf, (self.zone_size))
		self.cloud_surf.set_alpha(100)

	def get_zone_size(self):
		# get size (length and width) of zone in pixels for bg surf...

		with open(f'zones/zone_{self.game.current_zone}/zone_{self.game.current_zone}_block.csv', newline='') as csvfile:
		    reader = csv.reader(csvfile, delimiter=',')
		    for row in reader:
		        rows = (sum (1 for row in reader) + 1)
		        cols = len(row)
		self.zone_size = (cols * self.game.TILESIZE, rows * self.game.TILESIZE)

	def bg_blit(self):
		# display bg image as zone width divided by screen size...

		self.display_surf.blit(self.bg_surf,(0 - int(self.offset[0]) * 0.2, 0 - int(self.offset[1]) * 0.2))
		self.display_surf.blit(self.bg_surf1,(0 - int(self.offset[0]) * 0.3, 0 - int(self.offset[1]) * 0.3))
		self.display_surf.blit(self.bg_surf2,(0 - int(self.offset[0]), 0 - int(self.offset[1])))

		# below is to create a camera box around the target to move the scroll instead of the target moving the scroll if wanted
		# get cam position

		# if target[0] < self.camera_rect.left:
		# 	self.camera_rect.left = target[0]
		# if target[0] > self.camera_rect.right:
		# 	self.camera_rect.right = target[0]
		# if target[1] < self.camera_rect.top:
		# 	self.camera_rect.top = target[1]
		# if target[1] > self.camera_rect.bottom:
		# 	self.camera_rect.bottom = target[1]
		# # cam offset
		# self.offset = pygame.math.Vector2(self.camera_rect.left - self.CAMERA_BORDERS['left'], self.camera_rect.top - self.CAMERA_BORDERS['top'])

	def screenshake(self):
		random_number = random.randint(-4, 4)
		self.offset[0] -= random_number
		self.offset[1] -= random_number

	def keyboard_control(self):

		# scroll with keyboard
		keys = pygame.key.get_pressed()
		self.zone_boundary_limits()
		if keys[pygame.K_a] and self.offset[0] > 0:
			self.offset[0] -= self.scroll_speed
		elif keys[pygame.K_d] and self.offset[0] < self.zone_size[0] - self.display_surf.get_width():
			self.offset[0] += self.scroll_speed
		if keys[pygame.K_w] and self.offset[1] > 0:
			self.offset[1] -= self.scroll_speed
		elif keys[pygame.K_s] and self.offset[1] < self.zone_size[1] - self.display_surf.get_width():
			self.offset[1] += self.scroll_speed

	def zone_boundary_limits(self):
		if self.offset[0] <= 0:
			self.offset[0] = 0
		elif self.offset[0] >= self.zone_size[0] - self.display_surf.get_width():
			self.offset[0] = self.zone_size[0] - self.display_surf.get_width()
		if self.offset[1] <= 0:
			self.offset[1] = 0
		elif self.offset[1] >= self.zone_size[1] - self.display_surf.get_height():
			self.offset[1] = self.zone_size[1] - self.display_surf.get_height()

	def offset_draw(self, target):
		if self.zone.player.invincible and self.zone.player.alive:
			self.screenshake()
		for enemy in self.zone.enemy_sprites:
			if enemy.state == 'hit':
				self.screenshake()

		self.zone_boundary_limits()
		self.bg_blit()

		# get room transition when collide with room
	
		for room in self.game.room_dict[self.game.current_zone].values():
			if (room[1]).collidepoint(target):
				room_pos = room[1].topleft	
				room_size = room[0]

		# normal scrolling only when cutscene not running (cutscene has its own scroll control)
		if not self.zone.cutscene_running:
			
			self.offset[0] += (target[0] - self.offset[0] - self.display_surf.get_width() *0.5)/self.scroll_delay
			self.offset[1] += (target[1] - self.offset[1] - self.display_surf.get_height() *0.5)/self.scroll_delay * (16/9)

			if self.offset[0] <= room_pos[0]:
				self.offset[0] += (self.display_surf.get_width()/self.screen_transition_speed)
				if self.offset[0] >= room_pos[0]:
					self.offset[0] = room_pos[0]
			elif self.offset[0] >= room_size[0] - self.display_surf.get_width():
				self.offset[0] -= (self.display_surf.get_width()/self.screen_transition_speed)
				if self.offset[0] <= room_size[0] - self.display_surf.get_width():
					self.offset[0] = room_size[0] - self.display_surf.get_width()

			if self.offset[1] <= room_pos[1]:
				self.offset[1] += self.display_surf.get_height()/self.screen_transition_speed
				if self.offset[1] >= room_pos[1]:
					self.offset[1] = room_pos[1]
			elif self.offset[1] >= room_size[1] - self.display_surf.get_height():
				self.offset[1] -= self.display_surf.get_height()/self.screen_transition_speed
				if self.offset[1] <= room_size[1] - self.display_surf.get_height():
					self.offset[1] = room_size[1] - self.display_surf.get_height()

			# if self.offset[0] <= room_pos[0]:
			# 	self.offset[0] = room_pos[0]
			# elif self.offset[0] >= room_size[0] - self.display_surf.get_width():
			# 	self.offset[0] = room_size[0] - self.display_surf.get_width()

			# if self.offset[1] <= room_pos[1]:
			# 	self.offset[1] = room_pos[1]
			# elif self.offset[1] >= room_size[1] - self.display_surf.get_height():
			# 	self.offset[1] = room_size[1] - self.display_surf.get_height()	
		else:
			self.keyboard_control()


		# seperate blits to layer target on top of other sprites
		for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
			offset = sprite.rect.topleft - self.offset
			self.display_surf.blit(sprite.image, offset)

			# if sprite.rect.left > self.zone_size[0] or sprite.rect.right < 0 or\
			# 	sprite.rect.top > self.zone_size[1] or sprite.rect.bottom < 0:
			# 	sprite.kill()

	def enemy_update(self, target):
		#enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
		#for enemy in enemy_sprites:
		for sprite in self.zone.enemy_sprites:
			sprite.enemy_update(target)










		






		
