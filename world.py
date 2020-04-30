from objects import *
from tasks import *


#world.append(Person(128, 128, None, task_platoonleader, (10,50,10)))
#world.append(Person(300, 100, None, task_platoonleader, (210,240,210)))

world.append(Person(50, 50, None, task_leader, (250,50,10)))

for i in range(1):
    world.append(Person(128, 128, None, task_worker, (255,255,0)))
