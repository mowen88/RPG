import pygame
from state import State

fade_speed = 75 # higher is slower

class FadeOut(State):
	def __init__(self, game, zone, colour, max_saturation, counter):
		State.__init__(self, game)

		self.zone = zone
		self.colour = colour
		self.max_saturation = max_saturation
		self.counter = counter
		self.display_surf = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
		self.display_surf.fill((self.colour))
		self.display_surf2 = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
		self.display_surf2.fill((self.game.BLACK))

	def update(self, actions):
		self.prev_state.player.animate('end_on_last_frame', 0.15)
		self.counter += (255/fade_speed)
		if self.counter >= self.max_saturation:
			self.zone.respawn()
		self.game.reset_keys()

	def render(self, display):
		self.prev_state.render(display)
		if self.counter <= 255:
			self.display_surf.set_alpha(self.counter)
			display.blit(self.display_surf, (0,0))
			self.display_surf2.set_alpha(self.counter)
			display.blit(self.display_surf2, (0,0))

class FadeIn(State):
	def __init__(self, game):
		State.__init__(self, game)
		self.counter = 600
		self.display_surf = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
		self.display_surf.fill((self.game.BLACK))

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
		else:
			display.blit(self.display_surf, (0,0))