from objects import *
from tasks import *

#world.append(Person(128, 128, None, task_platoonleader, (10,50,10)))
#world.append(Person(500, 500, None, task_platoonleader, (210,240,210)))

for i in range(40):
    world.append(Person(128, 128, None, task_worker, (255,255,0)))

from glob import glob

for path in glob("split/*.png"):
    tx, ty = path.split("/")[-1].split(".")[0].split("-")
    tx = int(tx)
    ty = int(ty)
    world.append(PassiveTaskObject(randint(0,640), randint(0,480), 20, 20, path, color_wood, Task(f"gotome pickmeup {tx} {ty} carryme dropme end".split())))

for i in range(50):
    #world.append(Box(randint(0,400), randint(0,400)))
    #world.append(Wood(randint(0,400), randint(0,400)))
    #world.append(Tree(randint(0,400), randint(0,400)))
    pass
