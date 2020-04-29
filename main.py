#pyrisonarchitect
from time import sleep
from collections import defaultdict

import pygame
import pygame_gui

from world import *

pygame.init()
pygame.display.set_caption("army")

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_WH = (SCREEN_WIDTH,SCREEN_HEIGHT)
screen = pygame.display.set_mode(SCREEN_WH)

manager = pygame_gui.UIManager(SCREEN_WH)
#manager.set_visual_debug_mode(True)

button_roommenu = pygame_gui.elements.UIButton(
	relative_rect=pygame.Rect((50, 400), (50, 50)),
	text="Rooms",
	manager=manager
)

roommenu = pygame_gui.elements.UIWindow(
	rect=pygame.Rect((0, -5000), (400, 50)),
	manager=manager
)

room_buttons = []

for i in range(0, 5):
	button = pygame_gui.elements.UIButton(
		relative_rect=pygame.Rect((i*60, 0), (50, 50)),
		text=f"{i}",
		container=roommenu,
		manager=manager
	)
	button.data = i
	room_buttons.append(button)

button_staffmenu = pygame_gui.elements.UIButton(
	relative_rect=pygame.Rect((100, 400), (50, 50)),
	text="Staff",
	manager=manager
)

staffmenu = pygame_gui.elements.UIWindow(
	rect=pygame.Rect((0, -5000), (400, 50)),
	manager=manager
)

staff_buttons = []

for staff in [task_worker]:
	button = pygame_gui.elements.UIButton(
		relative_rect=pygame.Rect((i*60, 0), (50, 50)),
		text=f"Hire",
		container=staffmenu,
		manager=manager
	)
	button.data = staff
	staff_buttons.append(button)

button_objectmenu = pygame_gui.elements.UIButton(
	relative_rect=pygame.Rect((150, 400), (50, 50)),
	text="Objects",
	manager=manager
)

objectmenu = pygame_gui.elements.UIWindow(
	rect=pygame.Rect((0, -5000), (400, 50)),
	manager=manager
)

object_buttons = []

buildable_objects = ["tree", "wood", "chair"]
for i, objectname in enumerate(buildable_objects):
	button = pygame_gui.elements.UIButton(
		relative_rect=pygame.Rect((i*60, 0), (50, 50)),
		text=objectname,
		container=objectmenu,
		manager=manager
	)
	button.data = objectname
	object_buttons.append(button)

clock = pygame.time.Clock()

color = (210, 210, 200)#(255, 255, 255)

delta = 0.025

i = 0
running = True

sel_type = None
sel_data = None

sel_start = None
sel_intermediate = None
sel_end = None
# TODO weakmap, in case object is removed
selected = []

keymap = defaultdict(lambda: 0)

while running:

	time_delta = clock.tick(60)/1000

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
		sel_color = (0, 100, 255) if sel_type == "select" else (255,0,0)
		pygame.draw.rect(screen, sel_color, (x1, y1, x2-x1, y2-y1), 2)

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
				if sel_type is not None:
					pass
				elif keymap[pygame.K_r]:
					sel_type = "room"
					sel_data = 2
				else:
					sel_type = "select"
				sel_start = pygame.mouse.get_pos()
		elif event.type == pygame.MOUSEBUTTONUP:

			if sel_start:

				pos = pygame.mouse.get_pos()

				if pos == sel_start:
					if sel_type == "select":
						for selection in selected:
							selection.settask(f"{pos[0]} {pos[1]} 1000 move".split())
					elif sel_type == "hire":
						world.append(Person(pos[0], pos[1], None, sel_data, (255,255,0)))
					elif sel_type == "place":
						print(*pos, sel_data)
						createObjectAt(sel_data, *pos)
					else:
						print("unknown click sel_type", sel_type)
						sel_type = None
						sel_data = None

				else:
					sel_end = pos

					x1 = min(sel_start[0], sel_end[0])
					x2 = max(sel_start[0], sel_end[0])
					y1 = min(sel_start[1], sel_end[1])
					y2 = max(sel_start[1], sel_end[1])

					if sel_type == "select":
						selected = []

						for obj in world:
							if not isinstance(obj, Person):
								continue

							ox, oy = obj.body.position
							if x1 <= ox <= x2 and y1 <= oy <= y2:
								selected.append(obj)


						print("Selected:", selected)
					elif sel_type == "room":
						for y in range(y1//GS, y2//GS):
							for x in range(x1//GS, x2//GS):
								worldgrid[y][x] = sel_data if event.button == 1 else 1#2 if worldgrid[y][x] == 1 else 1
								updatePathgrid()

					elif sel_type == "hire":
						sel_type = None
						sel_data = None

					else:
						print("Unknown sel_type:", sel_type)

				sel_start = None
				sel_intermediate = None
				sel_end = None

		elif event.type == pygame.QUIT:
			running = False



		elif event.type == pygame.USEREVENT:
			if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
				uie = event.ui_element

				buttonmap = {
					"room": room_buttons,
					"hire": staff_buttons,
					"place": object_buttons,
				}

				for selname, buttonlist in buttonmap.items():
					if uie in buttonlist:

						if sel_type == selname and sel_data == uie.data:
							sel_type = None
							sel_data = None
							uie.unselect()
						else:
							sel_type = selname
							sel_data = uie.data
							uie.select()
							for buttonlist2 in buttonmap.values():
								for button2 in buttonlist2:
									if button2 != uie and button2.is_selected:
										button2.unselect()

						break


				#for:else:

				menumap = {
					button_roommenu: roommenu,
					button_staffmenu: staffmenu,
					button_objectmenu: objectmenu,
				}

				for menubutton, menu in menumap.items():
					if uie == menubutton:
						menupos = menu.get_relative_rect()
						if menupos.y > -30:
							menu.set_position(Vec2d(0, -5000))
							sel_type = None
							sel_data = None
						else:
							# TODO: old position
							menu.set_position(Vec2d(50, 300))

						# TODO hide all others?
						for menu2 in menumap.values():
							if menu2 != menu:
								menu2.set_position(Vec2d(0, -5000))
						break

		manager.process_events(event)

	manager.update(time_delta)

	# how come deleted objects are not selected anymore?
	if len(selected) > 0:
		p = selected[0]
		for need in p.cats["Need"]:
			#print(need["Name"], need["Value"])
			pass

	manager.draw_ui(screen)
	pygame.display.flip()
