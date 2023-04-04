import pygame, os, csv
from state import State
from player import Player
from tile import Tile
from player import Player
from camera import CameraGroup

class World(State):
	def __init__(self, game):
		State.__init__(self, game)


		self.visible_sprites = CameraGroup(self.game, self, self.game.room, self.game.room_pos, self.game.room_size)
		self.obstacle_sprites = pygame.sprite.Group()
		self.active_sprites = pygame.sprite.Group()
		self.display_surf = pygame.display.get_surface()

		self.cutscene_running = False

		self.create_map()

	def create_map(self):
		layouts = {
		'block':self.game.import_csv(f'maps/zone_block.csv'),
		'player':self.game.import_csv(f'maps/zone_player.csv'),
		}
		images = {
		'tiles':self.game.import_folder(f'maps/tiles')
		}

		for style, layout in layouts.items():
			for row_index, row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * self.game.TILESIZE
						y = row_index * self.game.TILESIZE

						if style == 'block':
							surf = images['tiles'][int(col)]
							Tile(self.game, (x,y), [self.visible_sprites, self.obstacle_sprites], surf)
						if style == 'player':
							if col == '0':
								self.player = Player(self.game, self, (x, y), [self.visible_sprites, self.active_sprites])

	def update(self, actions):	
		self.active_sprites.update()
		self.game.reset_keys()

	def render(self, display):
		
		self.visible_sprites.offset_draw(self.player.rect.center)
