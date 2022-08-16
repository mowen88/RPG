import pygame, os, csv


from state import State
from player import Player
from tile import Tile, Stairs, Ramp
from player import Player
from enemies import Enemy
from camera import CameraGroup
from actions import Melee, Projectile, DashParticles

class Zone(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.visible_sprites = CameraGroup(self.game, self)
		self.active_sprites = pygame.sprite.Group()
		self.melee_sprite = pygame.sprite.GroupSingle()
		self.projectile_sprites = pygame.sprite.Group()
		self.display_surf = pygame.display.get_surface()

		# blocked off tile
		self.obstacle_sprites = pygame.sprite.Group()

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

		#enemies
		self.enemy_sprites = pygame.sprite.Group()
		self.player_sprite = pygame.sprite.GroupSingle()

		self.cutscene_running = False

		self.create_map()

	def create_map(self):
		layouts = {
		'block':self.game.import_csv(f'maps/zone_block.csv'),
		'player':self.game.import_csv(f'maps/zone_player.csv'),
		'entities':self.game.import_csv(f'maps/zone_entities.csv')
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
								sprite = Ramp(self.game, (x,y), [self.visible_sprites, self.active_sprites], surf)
								self.ramp_right_up_sprites.add(sprite)
								self.all_ramp_sprites.add(sprite)
							elif col == '2':
								sprite = Ramp(self.game, (x,y), [self.visible_sprites, self.active_sprites], surf)
								self.ramp_left_up_sprites.add(sprite)
								self.all_ramp_sprites.add(sprite)
							elif col == '3':
								sprite = Ramp(self.game, (x,y), [self.visible_sprites, self.active_sprites], surf)
								self.ramp_right_down_sprites.add(sprite)
								self.all_ramp_sprites.add(sprite)
							elif col == '4':
								sprite = Ramp(self.game, (x,y), [self.visible_sprites, self.active_sprites], surf)
								self.ramp_left_down_sprites.add(sprite)
								self.all_ramp_sprites.add(sprite)
							elif col == '5':
								sprite = Stairs(self.game, self, (x,y), [self.visible_sprites, self.active_sprites], surf)
								self.stairs_right_up_sprites.add(sprite)
								self.all_stairs_sprites.add(sprite)
							elif col == '6':
								sprite = Stairs(self.game, self, (x,y), [self.visible_sprites, self.active_sprites], surf)
								self.stairs_left_up_sprites.add(sprite)
								self.all_stairs_sprites.add(sprite)
							elif col == '7':
								sprite = Stairs(self.game, self, (x,y), [self.visible_sprites, self.active_sprites], surf)
								self.stairs_right_down_sprites.add(sprite)
								self.all_stairs_sprites.add(sprite)
							elif col == '8':
								sprite = Stairs(self.game, self, (x,y), [self.visible_sprites, self.active_sprites], surf)
								self.stairs_left_down_sprites.add(sprite)
								self.all_stairs_sprites.add(sprite)

						elif style == 'player':
							if col == '0':
								self.player = Player(self.game, self, (x, y), [self.visible_sprites, self.active_sprites])
								self.player_sprite.add(self.player)
						elif style == 'entities':
							if col == '0':
								self.enemy = Enemy('samurai', self.game, self, (x, y), [self.visible_sprites, self.active_sprites])
								self.enemy_sprites.add(self.enemy)
							

	def create_melee(self):
		self.melee_sprite = Melee(self.game, self, [self.visible_sprites, self.active_sprites], self.display_surf)

	def create_projectile(self):
		sprite = Projectile(self.game, self, [self.visible_sprites, self.active_sprites], self.display_surf)
		self.projectile_sprites.add(sprite)

	def create_dash_particles(self):
		DashParticles(self.game, self, [self.visible_sprites, self.active_sprites], 'dash')

	def create_shadows(self):
		shadow_img = pygame.image.load('img/shadow.png').convert_alpha()
		shadow_img = pygame.transform.scale(shadow_img, (shadow_img.get_width() * self.game.SCALE, shadow_img.get_height() * self.game.SCALE))
		shadow_img.set_alpha(80)
		shadow_rect = shadow_img.get_rect()
		self.display_surf.blit(shadow_img, (self.player.rect.midbottom[0] - self.visible_sprites.offset[0] - (shadow_img.get_width()//2), self.player.rect.midbottom[1] - self.visible_sprites.offset[1] - (shadow_img.get_height()//2)))

		for sprite in self.enemy_sprites:
			self.display_surf.blit(shadow_img, (sprite.rect.midbottom[0] - self.visible_sprites.offset[0] - (shadow_img.get_width()//2), sprite.rect.midbottom[1] - self.visible_sprites.offset[1] - (shadow_img.get_height()//2)))
	
	def dash_line_particle(self, colour, width):
		if self.player.dashing:
			pygame.draw.line(self.display_surf, colour, (self.player.dash_start_pos[0] - self.visible_sprites.offset[0], self.player.dash_start_pos[1] - self.visible_sprites.offset[1]), (self.player.rect.centerx - self.visible_sprites.offset[0], self.player.rect.centery - self.visible_sprites.offset[1]), width)

	def custom_cursor(self):
		pygame.mouse.set_visible(False)
		cursor_img = pygame.image.load('img/cursor/0.png').convert_alpha()
		cursor_img = pygame.transform.scale(cursor_img,(cursor_img.get_width()*self.game.SCALE, cursor_img.get_height()*self.game.SCALE))
		cursor_img.set_alpha(150)
		cursor_rect = cursor_img.get_rect()
		self.display_surf.blit(cursor_img, (self.player.mx, self.player.my))
	
	def update(self, actions):	
		if self.game.actions['return']:
			self.cutscene_running = True
		self.active_sprites.update()
		self.game.reset_keys()

	def render(self, display):
		self.visible_sprites.offset_draw(self.player.rect.center)
		self.visible_sprites.enemy_update(self.player)
		self.create_shadows()
		self.dash_line_particle(self.game.BLACK, 6)
		self.dash_line_particle(self.game.GREY, 4)
		self.dash_line_particle(self.game.WHITE, 2)
		self.custom_cursor()
		self.game.draw_text(display, str('ATTACKING: ' + str(self.enemy.state) + ' ATTACK COUNT: ' + str(self.enemy.attacking) + ' CAN ATTACK: ' + str(self.enemy.windup_counter)), self.game.WHITE, 70, (display.get_width() *0.5,display.get_height() * 0.2))
		self.game.draw_text(display, str('FPS: ' + self.game.show_fps), self.game.WHITE, 70, (display.get_width() *0.5,display.get_height() * 0.1))


