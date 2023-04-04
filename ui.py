import pygame

class UI:
	def __init__(self, game, zone):

		self.game = game
		self.zone = zone

		self.health_icon_img = pygame.image.load('img/ui/health_icon.png').convert_alpha()
		self.health_bar_img = pygame.image.load('img/ui/health_bar.png').convert_alpha()
		self.health_icon_img = pygame.transform.scale(self.health_icon_img, (self.health_icon_img.get_width() * self.game.SCALE, self.health_icon_img.get_height() * self.game.SCALE))
		self.health_bar_img = pygame.transform.scale(self.health_bar_img, (self.health_bar_img.get_width() * self.game.SCALE, self.health_bar_img.get_height() * self.game.SCALE))

	def health_display(self):
		self.game.screen.blit(self.health_bar_img, ((57.5, 27.5)))
		for box in range(self.game.health):
			box *= 30
			self.game.screen.blit(self.health_icon_img, ((box + 60, 30)))

	def render(self):
		self.health_display()

