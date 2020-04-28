from objects import *

#world.append(Person(128, 128, None, task_platoonleader, (10,50,10)))
#world.append(Person(500, 500, None, task_platoonleader, (210,240,210)))

world.append(Person(128, 128, None, task_worker, (255,255,0)))

for i in range(5):
    world.append(Box(randint(0,400), randint(0,400)))
