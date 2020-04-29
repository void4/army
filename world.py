from objects import *
from tasks import *



#world.append(Person(128, 128, None, task_platoonleader, (10,50,10)))
#world.append(Person(500, 500, None, task_platoonleader, (210,240,210)))

for i in range(1):
    world.append(Person(128, 128, None, task_worker, (255,255,0)))

#world.append(PassiveTaskObject(randint(0,640), randint(0,480), 20, 20, path, color_wood, Task(f"gotome pickmeup {tx} {ty} carryme dropme end".split())))
