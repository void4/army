from goapy import Planner, Action_List
from random import choice
import time

# interrupt as priority increases

class Order:
    def __init__(self, target, message):
        self.target = target
        self.message = message

c_selforder = lambda s, o: o.target == s
c_passorder = lambda s, o: o.target != s

class Agent:

    def __init__(self):
        self.superior = None
        self.orders = []
        self.listening = False
        self.need_hunger = 0
        self.need_sleep = 0
        self.bored = False

        self.history = []

    def __str__(self):
        return f"Agent<{self.need_hunger} {self.need_sleep}>"

    def getOrders(self, condition):
        return [o for o in self.orders if condition(self, o)]

    def step(self):

        selforders = self.getOrders(c_selforder)
        passorders = self.getOrders(c_passorder)

        print(selforders, passorders)

        world = Planner('hungry', 'tired', "has_noorder", "has_order", "has_passorder", "get_order", "give_order", "execute_order", "bored")
        world.set_start_state(hungry=self.need_hunger > 70, tired=self.need_sleep > 70, has_order=len(selforders), has_passorder=len(passorders)>0, has_noorder=len(selforders)==0, bored=self.bored)
        world.set_goal_state(tired=False, has_passorder=False, has_noorder=True, has_order=True, bored=True)

        actions = Action_List()
        actions.add_condition('eat', hungry=True)
        actions.add_reaction('eat', hungry=False)

        actions.add_condition('sleep', tired=True)
        actions.add_reaction('sleep', tired=False)

        actions.add_condition("get_order", has_order=False)
        actions.add_reaction("get_order", has_order=True)
        actions.set_weight('get_order', 10)#dynamically adjust these weights

        actions.add_condition("give_order", has_passorder=True)
        actions.add_reaction("give_order", has_passorder=False)
        actions.set_weight('give_order', 5)

        actions.add_condition("execute_order", has_noorder=False)
        actions.add_reaction("execute_order", has_noorder=True)
        actions.set_weight('execute_order', 1)

        actions.add_condition("idle", bored=False)
        actions.add_reaction("idle", bored=True)
        actions.set_weight('idle', 20)



        world.set_action_list(actions)

        _t = time.time()
        path = world.calculate()
        _took_time = time.time() - _t

        #print(path)

        for pi, p in enumerate(path):
            print(pi, p['name'])

        if path is None or len(path) == 0:
            print("no path found")
            return

        self.listening = False


        pn = path[0]["name"]
        self.history.append(pn)
        if pn == "eat":
            self.need_hunger = max(0, self.need_hunger-20)
        elif pn == "sleep":
            self.need_sleep = max(0, self.need_sleep-20)
        elif pn == "give_order":
            po = choice(passorders)

            if po.target.listening:
                self.orders.remove(po)
                po.target.orders.append(po)
        elif pn == "get_order":
            self.listening = True
            print("listening")
        elif pn == "execute_order":
            order = selforders.pop(0)
            print("EXEC", order.message)
            self.orders.remove(order)

        if pn == "idle":
            self.bored = True
        else:
            self.bored = False
        #print('\nTook:', _took_time)

        self.need_hunger += 1
        self.need_sleep += 1

agents = []

for a in range(2):
    agent = Agent()
    if agents:
        agent.superior = agents[-1]
    agents.append(agent)

agents[0].orders.append(Order(agents[-1], "hello"))

for i in range(300):
    for ai, a in enumerate(agents):
        print("\nAgent", ai, a)
        a.step()



import matplotlib.pyplot as plt


actions = "eat sleep get_order give_order execute_order idle".split()

fig, ax = plt.subplots(1,1)


for agent in agents:
    ax.plot([actions.index(action) for action in agent.history])

ax.set_yticks(range(len(actions)))
ax.set_yticklabels(actions)

#ax.xlabel("Time")
#fig.ylabel('Actions')
plt.show()
