from random import random, randint, choice
from copy import deepcopy

import pygame
import pymunk
from pymunk import Space, Body, Poly, Vec2d, ShapeFilter

from parsetxt import parse

cats = parse("Needs.txt")

space = Space()
space.gravity = 0,0

world = []


def gel(a,b):
	if a < b:
		return -3
	elif a > b:
		return 3
	else:
		return 0

def dist(x1,y1,x2,y2):
	return ((x1-x2)**2+(y1-y2)**2)**0.5

A_MOVE, A_RECRUIT, A_FOLLOW, A_COLOR, A_IDLE, A_SHOOT, A_MOVETOOBJECT, A_MOVETOPOSITION = range(8)

task_soldier = "'(0,100,0) color 20 200 follow idle".split()
task_teamleader = "'(0,150,0) color 5 'soldier recruit 20 20 follow idle".split()
task_groupleader = "'(0,200,0) color 4 'teamleader recruit 15 20 follow idle".split()
task_platoonleader = "'(0,150,150) color 4 'groupleader recruit 300 300 1000 move idle".split()
#task_companyleader = "'(0,200,200) color 3 'platoonleader recruit 10 30 follow idle".split()
#task_battalionleader = "'(150,0,0) color 3 'companyleader recruit 300 300 1000 move idle".split()
#task_brigadeleader = "'(200,0,0) color 3 'battalionleader recruit 300 300 move".split()

task_worker = "idle".split()

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
		self.code = code
		self.hasworker = False
		self.step = 0
		self.stack = []

class Chair:
	def __init__(self, x, y):

		self.kill = False

		self.sx = 12
		self.sy = 14

		global space
		self.body = Body(1,100)
		poly = Poly.create_box(self.body, (self.sx, self.sy))
		poly._o = self
		self.body.position = x,y
		self.color = (150,100,150)
		space.add(self.body, poly)

	def draw(self, screen):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.body.position.x, self.body.position.y, self.sx, self.sy))

	def update(self):
		return self.kill

class Tree:
	def __init__(self, x, y):

		self.kill = False

		self.task = Task("gotome 'Wood transform end".split())

		self.sx = 3
		self.sy = 30

		global space
		self.body = Body(1,100)
		poly = Poly.create_box(self.body, (self.sx, self.sy))
		poly._o = self
		self.body.position = x,y
		self.color = (100,250,50)
		space.add(self.body, poly)

	def draw(self, screen):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.body.position.x, self.body.position.y, self.sx, self.sy))

	def update(self):
		return self.kill

class Wood:
	def __init__(self, x, y):

		self.kill = False

		self.task = Task("gotome pickmeup carryme dropme 'Chair transform end".split())

		self.sx = 15
		self.sy = 5

		global space
		self.body = Body(1,100)
		poly = Poly.create_box(self.body, (self.sx, self.sy))
		poly._o = self
		self.body.position = x,y
		self.color = (100,50,50)
		space.add(self.body, poly)

	def draw(self, screen):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.body.position.x, self.body.position.y, self.sx, self.sy))

	def update(self):
		return self.kill


class Box:
	def __init__(self, x, y):
		self.task = Task("gotome pickmeup carryme dropme end".split())

		self.size = 15

		global space
		self.body = Body(1,100)
		poly = Poly.create_box(self.body, (self.size, self.size))
		poly._o = self
		self.body.position = x,y
		self.color = (200,150,100)
		space.add(self.body, poly)

	def draw(self, screen):
		pygame.draw.rect(screen, self.color, pygame.Rect(self.body.position.x, self.body.position.y, self.size, self.size))

	def update(self):
		pass



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

		self.cats = deepcopy(cats)
		for need in self.cats["Need"]:
			need["Value"] = 0

		global space
		self.body = Body(1,100)
		poly = Poly.create_box(self.body, (self.size, self.size))
		poly._o = self
		self.body.position = x,y
		self.color = (0,0,0)
		space.add(self.body, poly)

	def draw(self, screen):
		pygame.draw.rect(screen, self.team, pygame.Rect(self.body.position.x, self.body.position.y, self.size, self.size))
		pygame.draw.rect(screen, self.color, pygame.Rect(self.body.position.x, self.body.position.y, self.size, self.size//2))

		hp = self.hp/100*self.size
		pygame.draw.rect(screen, (255,0,0), pygame.Rect(self.body.position.x+hp, self.body.position.y - 2, self.size-hp, 1))
		pygame.draw.rect(screen, (0,255,0), pygame.Rect(self.body.position.x, self.body.position.y - 2, hp, 1))


	def settask(self, task):
		self.cpu.pointer = 0
		self.cpu.task = task
		self.activity = None
		self.adata = None
		self.atime = 0

	def update(self):

		for need in self.cats["Need"]:
			if "AutoCharge" in need.get("Properties", []):
				need["Value"] += 1#*timeDelta

		step = False
		if self.activity in [A_MOVE, A_FOLLOW]:
			if self.activity == A_MOVE:
				tx, ty, td = self.adata[0], self.adata[1], self.adata[2]
			else:
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
				#self.body.position.x += dx
				#self.body.position.y += dy
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

					if random() < 0.9:
						world.append(Bullet(self.body.position.x, self.body.position.y, target.body.position.x, target.body.position.y))
					else:
						world.append(Grenade(self.body.position.x, self.body.position.y, target.body.position.x, target.body.position.y))


		elif self.activity == A_IDLE:
			if self.work is None:
				targets = [o for o in world if hasattr(o, "task") and len(o.task.code)>0 and not o.task.hasworker]
				if targets:
					target = choice(targets)
					target.task.hasworker = True
					print("Taking task", target.task)
					self.work = target
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
					self.adata = self.work
				elif cmd == "pickmeup":
					self.inventory.append(self.work)
					task.step += 1
				elif cmd == "carryme":
					self.activity = A_MOVETOPOSITION
					self.adata = [[200, 200], self.work]
				elif cmd == "dropme":
					self.inventory.remove(self.work)
					task.step += 1
				elif cmd == "transform":
					name = task.stack.pop(-1)
					world.append(globals()[name](self.work.body.position.x, self.work.body.position.y))
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

		elif self.activity == A_MOVETOOBJECT:
			x, y = self.body.position.x, self.body.position.y

			tx, ty = self.adata.body.position.x, self.adata.body.position.y

			if dist(x,y,tx,ty) < 20:
				self.adata.task.step += 1
				self.activity = A_IDLE
				self.adata = None
			else:
				dx, dy = gel(tx, x), gel(ty, y)
				#self.body.position.x += dx
				#self.body.position.y += dy
				#self.body.apply_force_at_local_point(Vec2d(dx,dy), (0,0))
				#print(self.body.position)
				self.body.position = Vec2d(x+dx,y+dy)
				print("Moving", dx, dy)

		elif self.activity == A_MOVETOPOSITION:
			x, y = self.body.position.x, self.body.position.y

			tx, ty = self.adata[0]

			if dist(x,y,tx,ty) < 20:
				self.adata[1].task.step += 1
				self.activity = A_IDLE
				self.adata = None
			else:
				dx, dy = gel(tx, x), gel(ty, y)
				#self.body.position.x += dx
				#self.body.position.y += dy
				#self.body.apply_force_at_local_point(Vec2d(dx,dy), (0,0))
				#print(self.body.position)
				self.body.position = Vec2d(x+dx,y+dy)
				print("Moving", dx, dy)

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
		for i in range(self.adata[0]):
			world.append(Person(self.body.position.x-16*i, self.body.position.y-10*i, superior=self, task=eval("task_"+self.adata[1]), team=self.team))

	def step(self, tick):
		pass

	def shout(msg):
		for obj in world:#quadtree
			if isinstance(obj, Person) and ((obj.x-self.body.position.x)**2+(obj.y-self.body.position.y)**2)**0.5 < 200:
				obj.inbox.append(msg)
