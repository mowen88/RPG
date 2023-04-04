import pygame, time, os
from state import State
from npc import NPC
from random import randint


class Board(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.alpha = 200
        self.image = pygame.Surface((self.game.WIDTH * 0.6, self.game.HEIGHT * 0.25))
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect()
      
    def add(self, letter, pos):
        s = self.game.font.render(letter, 1, self.game.WHITE)
        self.image.blit(s, pos)

class Cursor(pygame.sprite.Sprite):
    def __init__(self, board):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))
        self.text_height = 34
        self.text_width = 17
        self.rect = self.image.get_rect(topleft=(self.text_width, self.text_height))
        self.board = board
        self.step = 0
        self.text = ''
        self.cooldown = 0
        self.cooldowns = {'.': 6,
                       
                        ' ': 3,
                        '\n': 10}

    def write(self, text):
        self.text = list(text)

    def update(self):
        if not self.cooldown and self.text:

            letter = self.text.pop(0)

            if letter == '\n':
                self.rect.move_ip((0, self.text_height))
                self.rect.x = self.text_width

            else:
                self.board.add(letter, self.rect.topleft)
                self.rect.move_ip((self.text_width, 0))
            self.cooldown = self.cooldowns.get(letter, 1)

        if self.cooldown:
            self.cooldown -= 1

      
class Dialogue(State):
	def __init__(self, game, npc, dialog):
		State.__init__(self, game)

		self.display = pygame.display.get_surface()
		self.dialog = dialog
		self.box_img = pygame.Surface((self.game.WIDTH *0.6, self.game.HEIGHT * 0.3))
		self.arrow_img = pygame.Surface((self.game.WIDTH *0.025, self.game.HEIGHT * 0.025))
		self.arrow_img.fill(self.game.WHITE)
		self.timer = self.game.HEIGHT
		self.opening = True
		self.closing = False
		self.step = 0
		
		self.board = Board(self.game)
		self.cursor = Cursor(self.board)

		self.text_box = pygame.sprite.Group()
		self.text_box.add(self.board)

		self.cursor.write(self.dialog[self.step])

	def box(self, display):
		if self.opening == True:
			self.timer -= 8
			if self.timer <= self.game.HEIGHT * 0.7:
				self.timer = self.game.HEIGHT * 0.7
				self.opening = False

	def update(self, actions):
		if not self.opening and not self.closing:
			
			self.cursor.update()
			
			if actions['space'] and not self.cursor.text:
				self.board.image.fill((0,0,0))
				self.step += 1
				if self.step >= len(self.dialog):
					self.step = 0
					self.closing = True
					self.board.kill()
				self.cursor.write(self.dialog[self.step])
				self.cursor.rect.x, self.cursor.rect.y = self.cursor.text_width, self.cursor.text_height

					
		if self.timer >= self.game.HEIGHT and self.closing:
			self.exit_state()
						
		self.game.reset_keys()

	def render(self, display):
		self.prev_state.render(display)
		if self.closing:
			self.timer += 5
		else:
			self.box(display)
		self.board.rect.topleft = (self.game.WIDTH * 0.2, self.timer)
		self.text_box.draw(display)
		if not self.cursor.text:
			display.blit(self.arrow_img,((self.board.rect.bottomright[0] - self.arrow_img.get_width()), (self.board.rect.bottomright[1] - self.arrow_img.get_height())))

		self.game.draw_text(display, str(self.closing), ((200,200,200)), 100, (self.game.WIDTH * 0.5, self.game.HEIGHT * 0.1))



# class Dialogue(State):
# 	def __init__(self, game, npc, dialog):
# 		State.__init__(self, game)

# 		self.npc = npc
# 		self.dialog = dialog
# 		self.char_img = pygame.image.load(self.npc).convert_alpha()
# 		self.char_img = pygame.transform.scale(self.char_img, (self.char_img.get_width() *10, self.char_img.get_height() * 10))
# 		self.box_img = pygame.image.load('img/ui/dialog_bg.png').convert_alpha()
# 		self.box_img = pygame.transform.scale(self.box_img, (self.game.WIDTH *0.9, self.game.HEIGHT * 0.35))
# 		self.fadebox_img = pygame.Surface((self.game.WIDTH *0.6, self.game.HEIGHT * 0.25))
# 		self.fadebox_img.fill(self.game.BLUE)
# 		self.display_surf = pygame.display.get_surface()
# 		self.transitioning = True
# 		self.fade_speed = 8
		

# 		self.timer = self.game.HEIGHT
# 		self.fade_timer = 255
# 		self.opening = True
# 		self.closing = False
# 		self.step = 0

# 		self.index = -1
# 		self.words = []
# 		self.msg = []
# 		self.line = None
# 		self.lines = []
# 		self.typing = True
# 		self.message = "Computer: Hello, nice to meet you. \n Me: Nice to meet you. \n Computer: You too, goodbye!"

# 	def blit_text(self, display):
# 		initial_x = self.game.WIDTH * 0.3
# 		initial_y = self.game.HEIGHT * 0.7
# 		max_width = 700
# 		line_length = len(self.dialog[0][0])
# 		second_line_length = len(self.dialog[1][0])
# 		third_line_length  = len(self.dialog[1][0])
	
# 		offset_x = 12
# 		offset_y = 30

# 		if self.typing: 
# 			for letter in self.dialog[0]:
# 				self.index += 1
# 				offset_x *= self.index
# 				char = letter[self.index]
# 				if self.index >= line_length -1:
# 					self.index = -1
# 					self.typing = False
# 			self.words.append(char)
# 			self.line = (''.join(self.words))

# 		print(self.lines)
		
# 		line_surf = self.game.font.render(self.line, True, self.game.WHITE, 80)
# 		display.blit(line_surf, (initial_x, initial_y))

# 		pygame.time.wait(20)
	

# 	def fade(self, display):
# 		self.fade_timer -= self.fade_speed
# 		if self.fade_timer <= 255:
# 			self.fadebox_img.set_alpha(self.fade_timer)
# 			display.blit(self.fadebox_img, (self.game.self.game.WIDTH * 0.3, self.game.self.game.HEIGHT * 0.72))
# 		if self.fade_timer <= 0:
# 			self.transitioning = False
# 			self.fade_timer = 0
# 		else:
# 			self.trasitioning = True

# 	def box(self, display):
# 		if self.opening == True:
# 			self.timer -= 8
# 			if self.timer <= self.game.HEIGHT * 0.65:
# 				self.timer = self.game.HEIGHT * 0.65
# 				self.opening = False

# 	def update(self, actions):
# 		if actions['space'] and not self.transitioning:
# 			if self.transitioning == False:
# 				self.fade_timer = 255
# 				self.transitioning = True
# 			if self.step < len(self.dialog) -1:
# 				self.step += 1
# 			else:
# 				self.step = len(self.dialog) -1
# 				self.closing = True
# 		else:
# 			self.transitioning = False
# 		if self.timer >= self.game.HEIGHT and self.closing:
# 			self.exit_state()
# 		self.game.reset_keys()

# 	def render(self, display):
# 		self.prev_state.render(display)
# 		if self.closing:
# 			self.timer += 5
# 		else:
# 			self.box(display)
# 		display.blit(self.box_img, (self.game.WIDTH * 0.05, self.timer))
# 		if not (self.opening or self.closing):
# 			display.blit(self.char_img, (self.game.WIDTH * 0.05,  self.timer))
# 			self.blit_text(display)
# 			#self.fade(display)

# 		self.game.draw_text(display, str(self.line), ((200,200,200)), 100, (self.game.WIDTH * 0.5, self.game.HEIGHT * 0.1))

