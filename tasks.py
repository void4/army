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

task_soldier = "'(0,100,0) color 20 200 follow idle".split()
task_teamleader = "'(0,150,0) color 5 'soldier recruit 20 20 follow idle".split()
task_groupleader = "'(0,200,0) color 4 'teamleader recruit 15 20 follow idle".split()
task_platoonleader = "'(0,150,150) color 4 'groupleader recruit 300 300 1000 move idle".split()
task_companyleader = "'(0,200,200) color 3 'platoonleader recruit 10 30 follow idle".split()
task_battalionleader = "'(150,0,0) color 3 'companyleader recruit 300 300 1000 move idle".split()
#task_brigadeleader = "'(200,0,0) color 3 'battalionleader recruit 300 300 move".split()

task_leader = "1 'follower recruit followme 300 300 1000 move idle".split()
task_follower = "idle".split()

task_worker = "idle".split()
