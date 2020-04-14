import pygame
import pymunk
from pymunk import Space, Body, Poly, Vec2d, ShapeFilter
from random import random, randint, choice

space = Space()
space.gravity = 0,0

world = []

class Task:
	pass

def gel(a,b):
	if a < b:
		return -1
	elif a > b:
		return 1
	else:
		return 0

A_MOVE, A_RECRUIT, A_FOLLOW, A_COLOR = range(4)

task_soldier = "'(0,100,0) color 20 follow".split()
task_teamleader = "'(0,150,0) color 5 'soldier recruit 20 follow".split()
task_groupleader = "'(0,200,0) color 3 'teamleader recruit 15 follow".split()
task_platoonleader = "'(0,150,150) color 4 'groupleader recruit 10 follow".split()
task_companyleader = "'(0,200,200) color 3 'platoonleader recruit 10 300 300 move".split()
#task_battalionleader = "'(150,0,0) color 3 'companyleader recruit 300 300 move".split()
#task_brigadeleader = "'(200,0,0) color 3 'battalionleader recruit 300 300 move".split()

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
			ret = (A_MOVE, popn(2))
		elif cmd == "recruit":
			ret = (A_RECRUIT, popn(2))
		elif cmd == "follow":
			ret = (A_FOLLOW, pop())
		elif cmd == "color":
			ret = (A_COLOR, pop())
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
		self.t = 0

	def update(self):
		self.x += (self.tx-self.sx)/100
		self.y += (self.ty-self.sy)/100
		if self.t == 100:
			hit = space.point_query_nearest((self.x, self.y), 10, ShapeFilter())
			if hit and hit.shape is not None:
				hit.shape._o.hp -= 100
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

		self.size = 10

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

	def update(self):
		step = False
		if self.activity in [A_MOVE, A_FOLLOW]:
			if self.activity == A_MOVE:
				tx, ty = self.adata[0], self.adata[0]
			else:
				tx, ty = self.superior.body.position.x, self.superior.body.position.y
			dx, dy = gel(tx, self.body.position.x), gel(ty, self.body.position.y)
			#dist = ((self.y-ty)**2+(self.x-tx)**2)**0.5
			if (dx == 0 and dy == 0):# or (self.activity == A_FOLLOW and dist < self.adata):
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
		else:
			step = True

		if step:
			self.activity, self.adata = self.cpu.step()

		if random() < 0.01:
			target = choice([o for o in world if isinstance(o, Person)])
			world.append(Bullet(self.body.position.x, self.body.position.y, target.body.position.x, target.body.position.y))

		if random() < 0.01:
			target = choice([o for o in world if isinstance(o, Person)])
			world.append(Grenade(self.body.position.x, self.body.position.y, target.body.position.x, target.body.position.y))


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
