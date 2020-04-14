#pyrisonarchitect
from time import sleep

import pygame

from world import *

pygame.init()
pygame.display.set_caption("army")

screen = pygame.display.set_mode((1920,1080))

color = (255, 255, 255)

delta = 0.05

i = 0
running = True
while running:
	screen.fill(color)

	space.step(delta)

	killlist = []
	for oi, obj in enumerate(world):
		kill = obj.update()
		if kill:
			killlist.append(obj)
		obj.draw(screen)

	for obj in killlist:
		world.remove(obj)

	print(len(world))

	i += 1

	for event in pygame.event.get():

		if event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()
			print(pos)
			world[0].settask(f"{pos[0]} {pos[1]} move".split())

		elif event.type == pygame.QUIT:
			running = False

	pygame.display.flip()
	sleep(delta)
