#pyrisonarchitect
from time import sleep
from collections import defaultdict

import pygame

from world import *

pygame.init()
pygame.display.set_caption("army")

screen = pygame.display.set_mode((640,480))

color = (210, 210, 200)#(255, 255, 255)

delta = 0.025

i = 0
running = True

sel_start = None
sel_intermediate = None
sel_end = None
# TODO weakmap, in case object is removed
selected = []

keymap = defaultdict(lambda: 0)

while running:
	screen.fill(color)

	space.step(delta)

	killlist = []
	for oi, obj in enumerate(world):
		kill = obj.update()
		if kill:
			killlist.append(obj)
		obj.draw(screen)

	if sel_start and sel_intermediate:
		x1 = min(sel_start[0], sel_intermediate[0])
		x2 = max(sel_start[0], sel_intermediate[0])
		y1 = min(sel_start[1], sel_intermediate[1])
		y2 = max(sel_start[1], sel_intermediate[1])
		pygame.draw.rect(screen, (0, 100, 255), (x1, y1, x2-x1, y2-y1), 2)

	for obj in killlist:
		world.remove(obj)

	#TODO print(len(world))

	i += 1


	if sel_start:
		sel_intermediate = pygame.mouse.get_pos()

	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			keymap[event.key] = 1
		elif event.type == pygame.KEYUP:
			keymap[event.key] = 0
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mx, my = pygame.mouse.get_pos()
			if keymap[pygame.K_g]:
				worldgrid[my//GS][mx//GS] = 1 - worldgrid[my//GS][mx//GS]
			elif keymap[pygame.K_b]:
				createObjectAt("box", mx, my)
			elif keymap[pygame.K_t]:
				createObjectAt("tree", mx, my)
			elif keymap[pygame.K_w]:
				createObjectAt("wood", mx, my)
			elif keymap[pygame.K_c]:
				world.append(Person(mx, my, None, task_worker, (255,255,0)))
			else:
				sel_start = pygame.mouse.get_pos()
		elif event.type == pygame.MOUSEBUTTONUP:

			if sel_start:

				pos = pygame.mouse.get_pos()

				if pos == sel_start:
					for selection in selected:
						selection.settask(f"{pos[0]} {pos[1]} 200 move".split())
					print("moved")

				else:
					sel_end = pos

					x1 = min(sel_start[0], sel_end[0])
					x2 = max(sel_start[0], sel_end[0])
					y1 = min(sel_start[1], sel_end[1])
					y2 = max(sel_start[1], sel_end[1])

					selected = []

					for obj in world:
						if not isinstance(obj, Person):
							continue

						ox, oy = obj.body.position
						if x1 <= ox <= x2 and y1 <= oy <= y2:
							selected.append(obj)


					print("Selected:", selected)

				sel_start = None
				sel_intermediate = None
				sel_end = None

		elif event.type == pygame.QUIT:
			running = False

	# how come deleted objects are not selected anymore?
	if len(selected) > 0:
		p = selected[0]
		for need in p.cats["Need"]:
			#print(need["Name"], need["Value"])
			pass

	pygame.display.flip()
	sleep(delta)
