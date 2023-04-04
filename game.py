
import os, sys, time, pygame, csv, json
from os import walk
from csv import reader
from title import Title
# from zone import Zone

class Game:
	def __init__(self):
		pygame.init()
		
		self.SCALE = 2
		self.TILESIZE = 16 * self.SCALE
		self.HEIGHT = 288 * self.SCALE #288 #212
		self.WIDTH = self.HEIGHT // 9*16
		self.FPS = 60
		self.screen = pygame.display.set_mode((int(self.WIDTH), int(self.HEIGHT)), pygame.FULLSCREEN|pygame.SCALED)
		self.clock = pygame.time.Clock()
		self.running = True
		self.state_stack = []

		# game colours
		self.BLACK = ((22, 0, 32))
		self.GREY = ((128, 166, 205))
		self.WHITE = ((245, 245, 245))
		self.BLUE = ((100,140,230))
		self.RED = ((193,85,118))
		self.PINK = ((234, 173, 237))
		self.LIGHT_BLUE = ((143, 248, 226))

		# game fonts
		self.font = pygame.font.Font('font/ShareTechMono-Regular.ttf', 24)
		
		# game data
		with open('data_dicts/room_data.txt') as f: self.room_dict = eval(f.read())
		with open('data_dicts/enemy_data.txt') as f: self.enemy_data = eval(f.read())
		with open('data_dicts/action_key_data.txt') as f: self.actions = eval(f.read())
		
		# persistent game variables
		self.current_zone = 0
		self.current_exit = 0
		self.max_health = 5
		self.health = self.max_health
		self.points = 0
		self.kills = 0
 
		self.load_states()

# 		self.dialog_dict = {
# 'NPC4': ["""This is a biblical example in pygame 
# and what happens if the text is far 
# too long for the box...""",
# """Undeniably the best at the second
# and what happens if the text is far 
# too long for the box now ???"""],
# 'NPC5': ["""This is a biblical example in pygame 
# and what happens if the text is far 
# too long for the box...""",
# """Undeniably the best at the second
# and what happens if the text is far 
# too long for the box now ???"""],

# 		'NPC6': ['This is a biblical example of wrapping text, into a box in pygame and what happens if the text is far too long for the box...',
# 				'This is the next sentence you are going to see when you press space bar.....',
# 				'To be honest, we may as well add one more sentence to make sure our dialogue box works as intended!!!']
# 				}

	def load_states(self):
		self.title_screen = Title(self)
		self.state_stack.append(self.title_screen)

	def get_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.actions['escape']= True
					self.running = False
				elif event.key == pygame.K_LEFT:
					self.actions['left'] = True
				elif event.key == pygame.K_RIGHT:
					self.actions['right'] = True
				elif event.key == pygame.K_UP:
					self.actions['up'] = True
				elif event.key == pygame.K_DOWN:
					self.actions['down'] = True
				elif event.key == pygame.K_RETURN:
					self.actions['return'] = True
				elif event.key == pygame.K_BACKSPACE:
					self.actions['backspace'] = True
				elif event.key == pygame.K_SPACE:
					self.actions['space'] = True
				elif event.key == pygame.K_LCTRL:
					self.actions['left_ctrl'] = True

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					self.actions['left'] = False
				elif event.key == pygame.K_RIGHT:
					self.actions['right'] = False
				elif event.key == pygame.K_UP:
					self.actions['up'] = False
				elif event.key == pygame.K_DOWN:
					self.actions['down'] = False
				elif event.key == pygame.K_RETURN:
					self.actions['return'] = False
				elif event.key == pygame.K_BACKSPACE:
					self.actions['backspace'] = False
				elif event.key == pygame.K_SPACE:
					self.actions['space'] = False
				elif event.key == pygame.K_LCTRL:
					self.actions['left_ctrl'] = False

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.actions['left_click'] = True
				elif event.button == 3:
					self.actions['right_click'] = True
				elif event.button == 4:
					self.actions['scroll_down'] = True
				elif event.button == 2:
					self.actions['scroll_up'] = True

			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					self.actions['left_click'] = False
				elif event.button == 3:
					self.actions['right_click'] = False
				elif event.button == 4:
					self.actions['scroll_down'] = False
				elif event.button == 2:
					self.actions['scroll_up'] = False


	def draw_text(self, surf, text, colour, size, pos):
		text_surf = self.font.render(text, True, colour, size)
		text_rect = text_surf.get_rect(center = pos)
		surf.blit(text_surf, text_rect)

	def import_csv(self, path):
		zone_grid = []
		with open(path) as grid:
			zone = reader(grid, delimiter=',')
			for row in zone:
				zone_grid.append(list(row))

		return zone_grid

	def import_folder(self, path):
		surf_list = []

		for _, __, img_files in walk(path):
			for img in img_files:
				full_path = path + '/' + img
				img_surf = pygame.image.load(full_path).convert_alpha()
				img_surf = pygame.transform.scale(img_surf,(img_surf.get_width() * self.SCALE, img_surf.get_height() * self.SCALE))
				surf_list.append(img_surf)

		return surf_list

	def reset_keys(self):
		for key_pressed in self.actions:
			self.actions[key_pressed] = False

	def game_loop(self):
		self.clock.tick(self.FPS)
		self.show_fps = str(int(self.clock.get_fps()))
		self.get_events()
		self.update()
		self.render()

	def update(self):
		self.state_stack[-1].update(self.actions)

	def render(self):
		self.state_stack[-1].render(self.screen)
		pygame.display.update()

if __name__ == "__main__":
	game = Game()
	while game.running:
		game.game_loop()


