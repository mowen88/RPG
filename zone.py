import pygame, os, csv, random

from state import State
from player import Player
from tile import Tile, Stairs, Ramp, SpawnPoint, Box
from player import Player
from enemies import Enemy
from camera import CameraGroup
from actions import Melee, Projectile, DashParticles, DashTrailFade, Blood, BloodTrail
from ui import UI
from transition import FadeIn, FadeOut


class Zone(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.visible_sprites = CameraGroup(self.game, self)
		self.active_sprites = pygame.sprite.Group()
		self.melee_sprite = pygame.sprite.GroupSingle()
		self.projectile_sprites = pygame.sprite.Group()
		self.display_surf = pygame.display.get_surface()

		self.target = [0,0]
		self.spawn_locations = []
		self.enemy_names = ['samurai', 'samurai_2']

		# blocked off tile
		self.obstacle_sprites = pygame.sprite.Group()
		self.spawn_point_sprites = pygame.sprite.Group()
		self.box_sprites = pygame.sprite.Group()

		self.stairs_right_up_sprites = pygame.sprite.Group()
		self.stairs_right_down_sprites = pygame.sprite.Group()
		self.stairs_left_up_sprites = pygame.sprite.Group()
		self.stairs_left_down_sprites = pygame.sprite.Group()
		# all stairs groups in one for easy access
		self.all_stairs_sprites = pygame.sprite.Group()

		self.ramp_left_up_sprites = pygame.sprite.Group()
		self.ramp_right_up_sprites = pygame.sprite.Group()
		self.ramp_left_down_sprites = pygame.sprite.Group()
		self.ramp_right_down_sprites = pygame.sprite.Group()

		# all ramp groups in one for easy access
		self.all_ramp_sprites = pygame.sprite.Group()

		self.attack_sprites = pygame.sprite.Group()
		self.enemy_sprites = pygame.sprite.Group()
		self.player_sprite = pygame.sprite.GroupSingle()

		self.cutscene_running = False

		self.create_map()
		self.get_spawn_random_locations()

		self.ui = UI(self.game, self)

	def create_map(self):
		layouts = {
		'block':self.game.import_csv(f'zones/zone_{self.game.current_zone}/zone_{self.game.current_zone}_block.csv'),
		'player':self.game.import_csv(f'zones/zone_{self.game.current_zone}/zone_{self.game.current_zone}_player.csv'),
		'entities':self.game.import_csv(f'zones/zone_{self.game.current_zone}/zone_{self.game.current_zone}_entities.csv')
		}
		images = {
		'blocks':self.game.import_folder(f'maps/blocks')
		}

		for style, layout in layouts.items():
			for row_index, row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * self.game.TILESIZE
						y = row_index * self.game.TILESIZE

						if style == 'block':
							surf = images['blocks'][int(col)]
							if col == '0':
								sprite = Tile(self.game, (x,y), [self.obstacle_sprites], surf)
								self.obstacle_sprites.add(sprite)
							elif col == '1':
								sprite = Ramp(self.game, (x,y), [self.active_sprites], surf)
								self.ramp_right_up_sprites.add(sprite)
								self.all_ramp_sprites.add(sprite)
							elif col == '2':
								sprite = Ramp(self.game, (x,y), [self.active_sprites], surf)
								self.ramp_left_up_sprites.add(sprite)
								self.all_ramp_sprites.add(sprite)
							elif col == '3':
								sprite = Ramp(self.game, (x,y), [self.active_sprites], surf)
								self.ramp_right_down_sprites.add(sprite)
								self.all_ramp_sprites.add(sprite)
							elif col == '4':
								sprite = Ramp(self.game, (x,y), [self.active_sprites], surf)
								self.ramp_left_down_sprites.add(sprite)
								self.all_ramp_sprites.add(sprite)
							elif col == '5':
								sprite = Stairs(self.game, self, (x,y), [self.active_sprites], surf)
								self.stairs_right_up_sprites.add(sprite)
								self.all_stairs_sprites.add(sprite)
							elif col == '6':
								sprite = Stairs(self.game, self, (x,y), [self.active_sprites], surf)
								self.stairs_left_up_sprites.add(sprite)
								self.all_stairs_sprites.add(sprite)
							elif col == '7':
								sprite = SpawnPoint(self.game, (x,y), [self.visible_sprites], surf)
								self.spawn_point_sprites.add(sprite)
							elif col == '8':
								sprite = Box(self.game, self, (x,y), [self.visible_sprites, self.active_sprites], surf)
								self.box_sprites.add(sprite)
						
						elif style == 'player':
							if col == '0':
								self.player = Player(self.game, self, (x, y), [self.visible_sprites, self.active_sprites])
								self.player_sprite.add(self.player)

						elif style == 'entities':
							if col == '0':
								self.enemy = Enemy('samurai', self.game, self, (x, y), [self.visible_sprites, self.active_sprites])
								self.enemy_sprites.add(self.enemy)
							elif col == '1':
								self.enemy = Enemy('samurai_2', self.game, self, (x, y), [self.visible_sprites, self.active_sprites])
								self.enemy_sprites.add(self.enemy)
			
	def get_spawn_random_locations(self):
		for sprite in self.spawn_point_sprites:
			pos = sprite.rect.center
			self.spawn_locations.append(pos)

	def attack_logic(self):
		if self.melee_sprite:
			melee_collision = pygame.sprite.spritecollide(self.melee_sprite, self.enemy_sprites, False)
			if melee_collision:
				for target in melee_collision:
					if self.melee_sprite.frame_index == (0 or 1 or 2) and not target.invincible and target.alive:
						if target.hitbox.colliderect(self.melee_sprite):
							Blood(self.game, self, [self.visible_sprites, self.active_sprites], self.display_surf, target.hitbox.center)
							target.invincible = True
							target.health -= 1
							if target.health <= 0:
								self.game.points += target.data['points']
								self.player.kills += 1
								self.create_blood_trail(target)
								target.alive = False

								self.enemy = Enemy(random.choice(self.enemy_names), self.game, self, (random.choice(self.spawn_locations)), [self.visible_sprites, self.active_sprites])
								self.enemy_sprites.add(self.enemy)
				
								if target.hitbox.x < self.player.hitbox.x:
									target.knockback_direction = 'right'
								else:
									target.knockback_direction = 'left'

	def enemy_attack_logic(self):
		if not self.player.dashing:
			for sprite in self.enemy_sprites:
				if not self.player.invincible and self.player.alive and sprite.state == 'attack' and sprite.frame_index < 5:
					if sprite.hitbox.colliderect(self.player.hitbox):
						# sprite.state = 'hit'
						self.reduce_health(sprite.damage)
						self.player.invincible = True
						if self.player.hitbox.x < sprite.hitbox.x:
							self.player.state = 'left_hit'
						else:
							self.player.state = 'right_hit'
			
	def reduce_health(self, amount):
		if not self.player.invincible:
			self.game.health -= amount
			if self.game.health <= 0:
				self.player.alive = False
				self.death_fadeout()
			else:
				Blood(self.game, self, [self.visible_sprites, self.active_sprites], self.display_surf, self.player.hitbox.center)

	def create_melee(self):
		self.melee_sprite = Melee(self.game, self, [self.visible_sprites, self.active_sprites], self.display_surf)

	def create_projectile(self):
		sprite = Projectile(self.game, self, [self.visible_sprites, self.active_sprites], self.display_surf)
		self.projectile_sprites.add(sprite)

	def create_dash_particles(self):
		DashParticles(self.game, self, [self.visible_sprites, self.active_sprites], 'dash')

	def dash_line_particle(self, width):
		if self.player.dashing:
			DashTrailFade(self.game, self, [self.visible_sprites, self.active_sprites], self.display_surf, 7.5, self.game.PINK, self.player.hitbox.midtop)
			DashTrailFade(self.game, self, [self.visible_sprites, self.active_sprites], self.display_surf, 7.5, self.game.WHITE, self.player.hitbox.center)
			DashTrailFade(self.game, self, [self.visible_sprites, self.active_sprites], self.display_surf, 7.5, self.game.LIGHT_BLUE, self.player.hitbox.midbottom)
			#pygame.draw.line(self.display_surf, colour, (self.player.dash_start_pos[0] - self.visible_sprites.offset[0], self.player.dash_start_pos[1] - self.visible_sprites.offset[1]), (self.player.rect.centerx - self.visible_sprites.offset[0], self.player.rect.centery - self.visible_sprites.offset[1]), width)

	def create_blood_trail(self, target):
		self.blood_trail = BloodTrail(self.game, self, [self.visible_sprites, self.active_sprites], self.display_surf, target.hitbox.center)
				
	def create_shadows(self):
		shadow_img = pygame.image.load('img/shadow.png').convert_alpha()
		shadow_img = pygame.transform.scale(shadow_img, (shadow_img.get_width() * self.game.SCALE, shadow_img.get_height() * self.game.SCALE))
		shadow_alpha = 80
		shadow_img.set_alpha(shadow_alpha)
		shadow_rect = shadow_img.get_rect()

		self.display_surf.blit(shadow_img, (self.player.rect.midbottom[0] - self.visible_sprites.offset[0] - (shadow_img.get_width()//2), self.player.rect.midbottom[1] - self.visible_sprites.offset[1] - (shadow_img.get_height()//2)))
		for sprite in self.enemy_sprites:
			self.display_surf.blit(shadow_img, (sprite.rect.midbottom[0] - self.visible_sprites.offset[0] - (shadow_img.get_width()//2), sprite.rect.midbottom[1] - self.visible_sprites.offset[1] - (shadow_img.get_height()//2)))
			if sprite.alpha < shadow_alpha:
				shadow_img.set_alpha(sprite.alpha)

	def custom_cursor(self):
		pygame.mouse.set_visible(False)
		cursor_img = pygame.image.load('img/cursor/0.png').convert_alpha()
		cursor_img = pygame.transform.scale(cursor_img,(cursor_img.get_width()*self.game.SCALE, cursor_img.get_height()*self.game.SCALE))
		cursor_img.set_alpha(150)
		cursor_rect = cursor_img.get_rect()
		self.display_surf.blit(cursor_img, (self.player.mx, self.player.my))

	def respawn(self):
		self.game.health = self.game.max_health
		new_state = Zone(self.game)
		new_state.enter_state()
		new_state = FadeIn(self.game)
		new_state.enter_state()

	def death_fadeout(self):
		new_state = FadeOut(self.game, self, self.game.RED, 255, -350)
		new_state.enter_state()
	
	def update(self, actions):
		self.attack_logic()	
		self.enemy_attack_logic()
		if self.game.actions['return']:
			self.cutscene_running = True
		self.active_sprites.update()
		self.game.reset_keys()

	def render(self, display):
		self.visible_sprites.offset_draw(self.player.rect.center)
		self.visible_sprites.enemy_update(self.player)
		self.create_shadows()
		self.dash_line_particle(6)
		self.dash_line_particle(4)
		self.dash_line_particle(2)
		self.custom_cursor()
		self.ui.render()
		self.game.draw_text(display, str('ATTACKING: ' + str(self.player.attacking) + ' ATTACK COUNT: ' + str(self.player.attack_count) + ' CAN ATTACK: ' + str(self.player.can_attack)), self.game.WHITE, 70, (display.get_width() *0.5,display.get_height() * 0.2))
		self.game.draw_text(display, str('FPS: ' + self.game.show_fps), self.game.WHITE, 70, (display.get_width() *0.5,display.get_height() * 0.1))
		self.game.draw_text(display, str('pts: ' + str(self.player.get_distance_direction_and_angle()[2])), self.game.WHITE, 70, (display.get_width() *0.5,display.get_height() * 0.1))
