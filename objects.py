from random import random, randint, choice
from copy import deepcopy

import pygame
import pymunk
from pymunk import Space, Body, Poly, Vec2d, ShapeFilter

from parsetxt import parse
from tasks import *

cats = parse("Needs.txt")

space = Space()
space.gravity = 0,0

world = []

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# World size
WW = 640
WH = 480

# Grid size
GS = 10

worldgrid = []

for y in range(0, WH, GS):
	worldgrid.append([])
	for x in range(0, WW, GS):
		worldgrid[-1].append(1)

for i in range(20):
	worldgrid[20+i][30] = 0

for x in range(10):
	for y in range(20):
		worldgrid[5+y][5+x] = 2

class ImageCache:
	def __init__(self):
		self.cache = {}
	def __getitem__(self, path):
		if not path in self.cache:
			self.cache[path] = pygame.image.load(path)
		return self.cache[path]

imagecache = ImageCache()

pathgrid = None

def updatePathgrid():
	global pathgrid, worldgrid
	pathgrid = [[1 if worldgrid[y][x] > 0 else 0 for x in range(WW//GS)] for y in range(WH//GS)]

updatePathgrid()

R_BLOCKED, R_AIR, R_RED = range(3)

tileimages = {
	R_RED: "red.png"
}

class World:
	def update(self):
		return False

	def draw(self, screen):
		for y in range(0, WH//GS):
			for x in range(0, WW//GS):
				if worldgrid[y][x] <= 0:
					pygame.draw.rect(screen, (10,10,10), pygame.Rect(x*GS,y*GS,GS,GS))
				elif worldgrid[y][x] > 1:
					screen.blit(imagecache["images/"+tileimages[worldgrid[y][x]]], (x*GS, y*GS))


world.append(World())

def gel(a,b):
	if a < b:
		return -2#use 3 for hectic people :)
	elif a > b:
		return 2
	else:
		return 0

def dist(x1,y1,x2,y2):
	return ((x1-x2)**2+(y1-y2)**2)**0.5

A_MOVE, A_RECRUIT, A_FOLLOW, A_COLOR, A_IDLE, A_SHOOT, A_MOVETOOBJECT, A_MOVETOPOSITION = range(8)

def is_number(s):
	try:
		i = int(s)
		return True
	except ValueError:
		return False

class Interpreter:
	def __init__(self, task):
		self.stack = []
		self.pointer = 0
		self.task = task

	def step(self):

		def pop():
			return self.stack.pop(-1)

		def popNone():
			return self.stack.pop(-1) if len(self.stack) else None

		def popn(n):
			return [pop() for i in range(n)][::-1]

		def push(v):
			self.stack.append(v)

		if self.pointer >= len(self.task):
			return (None, None)

		cmd = self.task[self.pointer]

		ret = (None, None)
		if is_number(cmd):
			push(int(cmd))
		elif cmd.startswith("'"):
			push(cmd[1:])
		elif cmd == "move":
			ret = (A_MOVE, popn(3))
		elif cmd == "recruit":
			ret = (A_RECRUIT, popn(2))
		elif cmd == "follow":
			ret = (A_FOLLOW, popn(2))
		elif cmd == "color":
			ret = (A_COLOR, pop())
		elif cmd == "idle":
			ret = (A_IDLE, popNone())
		else:
			raise Exception("UNKNWOWN", cmd)

		self.pointer += 1
		return ret

class Shout:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.t = 0

	def update(self):
		self.t += 1
		if self.t > 20:
			return True

	def draw(self, screen):
		pygame.draw.circle(screen, (50,50,50), (int(self.x), int(self.y)), self.t, min(self.t, 1))

class Bullet:
	def __init__(self, x, y, tx, ty):
		self.sx = x
		self.sy = y
		self.x = x
		self.y = y
		self.tx = tx
		self.ty = ty
		self.speed = 10
		distance = ((self.tx-self.x)**2+(self.ty-self.y)**2)**0.5
		self.dx = (self.tx-self.x)/distance*self.speed
		self.dy = (self.ty-self.y)/distance*self.speed
		self.x += self.dx*3
		self.y += self.dy*3
		self.t = 0

	def update(self):

		self.x += self.dx
		self.y += self.dy

		#if self.t == 100:
		hit = space.point_query_nearest((self.x, self.y), 2, ShapeFilter())
		if hit and hit.shape is not None:
			if isinstance(hit.shape._o, Person):
				hit.shape._o.hp -= 100
			return True

		if self.t > 200:
			return True
		self.t += 1

	def draw(self, screen):
		pygame.draw.circle(screen, (10,10,10), (int(self.x), int(self.y)), 1)

class Grenade:
	def __init__(self, x, y, tx, ty):
		self.sx = x
		self.sy = y
		self.x = x
		self.y = y
		self.tx = tx
		self.ty = ty
		self.t = 0

	def update(self):
		self.x += (self.tx-self.sx)/100
		self.y += (self.ty-self.sy)/100
		if self.t == 100:
			hits = space.point_query((self.x, self.y), 10, ShapeFilter())
			for hit in hits:
				if hit.shape is not None:
					print(hit.distance)
					dist = abs(hit.distance)
					hit.shape._o.hp -= (10-dist)*15

		self.t += 1

		if self.t >= 110:
			return True

	def draw(self, screen):
		if self.t < 100:
			pygame.draw.circle(screen, (10,10,10), (int(self.x), int(self.y)), 1)
		else:
			pygame.draw.circle(screen, (250,110,110), (int(self.x), int(self.y)), self.t-100)

class Task:
	def __init__(self, code):
		if isinstance(code, str):
			code = code.split()
		self.code = code
		self.hasworker = False
		self.step = 0
		self.stack = []

def attachBoxBody(self, x, y, color=(0,0,0), w=10, h=10, impulse=100):
	global space
	self.w = w
	self.h = h
	self.body = Body(1,impulse)
	poly = Poly.create_box(self.body, (self.w, self.h))
	poly._o = self
	self.body.position = Vec2d(x,y)
	self.color = color
	space.add(self.body, poly)

class PassiveObject:
	def __init__(self, x, y, w=10, h=10, image=None, color=(40,40,40)):
		self.kill = False
		try:
			self.image = imagecache[image]
		except:
			print("No image for:", image)
			self.image = None
		attachBoxBody(self, x, y, color, w, h)#(150,100,150))

	def draw(self, screen):
		if self.image:
			screen.blit(self.image, (self.body.position.x, self.body.position.y))
		else:
			pygame.draw.rect(screen, self.color, pygame.Rect(self.body.position.x, self.body.position.y, self.w, self.h))

	def update(self):
		return self.kill

class PassiveTaskObject(PassiveObject):
	def __init__(self, x, y, w=10, h=10, image=None, color=(0,0,0), task=None):
		super().__init__(x,y,w,h,image,color)
		if isinstance(task, str):
			task = Task(task)
		self.task = Task([]) if task is None else task

task_tree = "gotome 'wood transform end"
color_tree = (100,250,50)
size_tree = (3,30)

task_wood = "gotome pickmeup 60 400 200 carryme dropme 'chair transform end"
color_wood = (100, 50, 50)
size_wood = (5,5)

task_box = "gotome pickmeup 60 200 200 carryme dropme end"
color_box = (200,150,100)
size_box = (15, 15)

color_chair = (20,20,200)
size_chair = (10, 10)

def createObjectAt(name, x, y):
	g = globals()

	scolor = g["color_"+name]
	ssize = g["size_"+name]
	simg = "images/"+name+".png"


	stask = "task_"+name
	if stask in g:
		obj = PassiveTaskObject(x, y, *ssize, simg, scolor, g[stask])
	else:
		obj = PassiveObject(x, y, *ssize, simg, scolor)

	world.append(obj)

class Person:
	def __init__(self, x, y, superior=None, task=None, team=(0,0,0)):
		self.hp = 100
		self.activity = None
		self.adata = None
		self.inbox = []
		self.inventory = []
		self.hand = []
		self.cpu = Interpreter(task)
		self.superior = superior
		self.team = team

		self.atime = 0

		self.size = 10

		self.work = None

		self.path = None

		self.cats = deepcopy(cats)
		for need in self.cats["Need"]:
			need["Value"] = 0

		attachBoxBody(self, x, y, (0,0,0), self.size, self.size)

	def draw(self, screen):
		x, y = self.body.position.x, self.body.position.y
		pygame.draw.rect(screen, self.team, pygame.Rect(x, y, self.size, self.size))
		pygame.draw.rect(screen, self.color, pygame.Rect(x, y, self.size, self.size//2))

		hp = self.hp/100*self.size
		pygame.draw.rect(screen, (255,0,0), pygame.Rect(x+hp, y - 2, self.size-hp, 1))
		pygame.draw.rect(screen, (0,255,0), pygame.Rect(x, y - 2, hp, 1))

		if self.path:
			line = [(x,y)] + [(px*GS, py*GS) for (px, py) in self.path]
			for i in range(1, len(line)):
				previous = line[i-1]
				this = line[i]
				pygame.draw.line(screen, (0,0,255), previous, this)

	def settask(self, task):
		self.cpu.pointer = 0
		self.cpu.task = task
		self.activity = None
		self.adata = None
		self.atime = 0
		self.path = None

	def update(self):

		for need in self.cats["Need"]:
			if "AutoCharge" in need.get("Properties", []):
				need["Value"] += 1#*timeDelta

		step = False

		if self.activity in [A_MOVE, A_MOVETOPOSITION, A_MOVETOOBJECT]:
			x, y = self.body.position.x, self.body.position.y

			if self.activity in [A_MOVE, A_MOVETOPOSITION]:
				tx, ty, td = self.adata[0], self.adata[1], self.adata[2]
			else:
				tx, ty = self.work.body.position.x, self.work.body.position.y
				td = self.adata

			if self.path is None:
				grid = Grid(matrix=pathgrid)
				start = grid.node(int(x//GS), int(y//GS))
				end = grid.node(int(tx//GS), int(ty//GS))
				finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
				path, runs = finder.find_path(start, end, grid)
				self.path = path
				#print(path)
				print(f"Found path of length {len(path)} in {runs} runs")

			if len(self.path) == 0:
				print("Couldn't find path")
				self.activity = A_IDLE
				self.adata = None
				self.path = None
				#TODO continue

			# TODO object positition might change? /destroyed

			tx, ty = self.path[0]
			tx *= GS
			ty *= GS

			if dist(x,y,tx,ty) < 3:
				self.path.pop(0)

			if len(self.path) == 0 or self.atime > td:

				if self.activity in [A_MOVETOOBJECT, A_MOVETOPOSITION]:
					self.work.task.step += 1

				self.adata = None
				self.path = None
				self.activity = A_IDLE
				self.atime = 0

			else:
				dx, dy = gel(tx, x), gel(ty, y)
				self.body.position = Vec2d(x+dx,y+dy)
				self.atime += 1



		elif self.activity == A_FOLLOW:
			tx, ty = self.superior.body.position.x, self.superior.body.position.y
			td = self.adata[1]

			dx, dy = gel(tx, self.body.position.x), gel(ty, self.body.position.y)
			#dist = ((self.y-ty)**2+(self.x-tx)**2)**0.5
			self.atime += 1
			if (dx == 0 and dy == 0) or self.atime > td:# or (self.activity == A_FOLLOW and dist < self.adata):
				self.atime = 0
				step = True
			else:
				self.body.apply_force_at_local_point(Vec2d(dx,dy), (0,0))
		elif self.activity == A_RECRUIT:
			world.append(Shout(self.body.position.x, self.body.position.y))
			self.recruit()
			step = True
		elif self.activity == A_COLOR:
			self.color = eval(self.adata)
			step = True
		elif self.activity == A_SHOOT:
			if random() < 0.01:
				targets = [o for o in world if isinstance(o, Person) and o.team != self.team]
				if targets:
					target = choice(targets)
					x,y = self.body.position.x, self.body.position.y
					if random() < 0.9:
						world.append(Bullet(x, y, target.body.position.x, target.body.position.y))
					else:
						world.append(Grenade(x, y, target.body.position.x, target.body.position.y))


		elif self.activity == A_IDLE:
			if self.work is None:
				targets = [o for o in world if hasattr(o, "task") and len(o.task.code)>0 and not o.task.hasworker]
				if targets:
					x,y = self.body.position.x, self.body.position.y
					target = sorted(targets, key=lambda t:dist(x, y, t.body.position.x, t.body.position.y))[0]#choice(targets)
					target.task.hasworker = True
					print("Taking task", target.task)
					self.work = target
				#else: step=True?
			else:
				task = self.work.task
				cmd = task.code[task.step]
				print(cmd)
				if is_number(cmd):
					task.stack.append(int(cmd))
					task.step += 1
				elif cmd.startswith("'"):
					task.stack.append(cmd[1:])
					task.step += 1
				elif cmd == "gotome":
					self.activity = A_MOVETOOBJECT
					self.adata = 200
				elif cmd == "pickmeup":
					self.inventory.append(self.work)
					task.step += 1
				elif cmd == "carryme":
					self.activity = A_MOVETOPOSITION
					self.adata = [task.stack.pop(-3), task.stack.pop(-2), task.stack.pop(-1)]
				elif cmd == "dropme":
					self.inventory.remove(self.work)
					task.step += 1
				elif cmd == "transform":
					name = task.stack.pop(-1)

					x, y = self.work.body.position.x, self.work.body.position.y

					createObjectAt(name, x, y)

					task.step += 1
					self.work.kill = True
				elif cmd == "end":
					task.hasworker = False
					task.code = []
					task.step = None
					task.stack = []
					self.work = None
				else:
					print("unknown cmd:", cmd)
		else:
			step = True

		for item in self.inventory:
			item.body.position = self.body.position

		if step:
			self.activity, self.adata = self.cpu.step()



		if self.hp <= 0:
			return True

	def recruit(self):
		global world
		x, y = self.body.position.x, self.body.position.y
		for i in range(self.adata[0]):
			world.append(Person(x-16*i, y-10*i, superior=self, task=eval("task_"+self.adata[1]), team=self.team))

	def shout(msg):
		x, y = self.body.position.x, self.body.position.y
		for obj in world:#quadtree
			if isinstance(obj, Person) and dist(x,y,obj.x,obj.y) < 200:
				obj.inbox.append(msg)
