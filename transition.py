import pygame
from state import State

fade_speed = 50 # higher is slower

class FadeOut(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.counter = 0
		self.display_surf = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
		self.display_surf.fill((0,0,0))

	def update(self, actions):

		self.counter += (255/fade_speed)
		if self.counter >= 255:
			new_state = FadeIn(self.game)
			new_state.enter_state()
		self.game.reset_keys()

	def render(self, display):
		self.prev_state.render(display)
		if self.counter <= 255:
			self.display_surf.set_alpha(self.counter)
			display.blit(self.display_surf, (0,0))

class FadeIn(State):
	def __init__(self, game):
		State.__init__(self, game)

		self.counter = 255
		self.display_surf = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
		self.display_surf.fill((0,0,0))

	def update(self, actions):

		self.counter -= (255/fade_speed)
		if self.counter <= 0:
			#self.prev_state.exit_state()
			self.exit_state()
		self.game.reset_keys()

	def render(self, display):
		# self.prev_state.prev_state.render(display)
		self.prev_state.render(display)
		if self.counter <= 255:
			self.display_surf.set_alpha(self.counter)
			display.blit(self.display_surf, (0,0))