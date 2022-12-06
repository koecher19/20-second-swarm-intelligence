"""
building a swarm intelligence (based on Swarm Evolve 1.0) for
20 SECONDS GAME JAM 2022 (https://itch.io/jam/20-second-game-jam)
Author: Felix Köcher (https://github.com/koecher19)
"""
import numpy as np
import turtle
import tkinter as tk
from pygame import mixer
import time
import itertools

# sound
mixer.init()

# WINDOW
w = turtle.Screen()
w.title("20 Second Swarm Intelligence")
w.bgcolor("black")
w.setup(width=500, height=500)
w.tracer(0)


# scalars for velocity calculation:
"""
 calculate veclocity as weighted sum of these vectors:

 v_1: points away from neighbors in vicinity
 v_2: points to world center
 v_3: mean vector of neighbours
 v_4: points to center of weight of all agents
 v_5: random vector
 v_6: points away from neighbours of different species
 v_7: points to energy source
 """
alpha_v_1 = 0.1
alpha_v_2 = 0.001
alpha_v_3 = 0.005
alpha_v_4 = 0.01
alpha_v_5 = 0.25
alpha_v_6 = 0.1
alpha_v_7 = 0.01
dampening_factor = 0.98


# PARTICLE
class Particle:
    def __init__(self, type):
        self.type = type
        self.turtle = turtle.Turtle()
        self.size = 0
        self.pos = np.array([0, 0], dtype=float)
        self.vel = np.array([0, 0], dtype=float)
        self.energy = 100.0
        if type == "foodsource":
            # random position, vel stays == 0
            self.pos = np.random.uniform(low=-240, high=240, size=(2,))

            # set turtle
            self.turtle.shape("circle")
            self.turtle.fillcolor("green")
            self.size = 30
            self.turtle.shapesize(stretch_len=self.size / 20, stretch_wid=self.size / 20)

            self.turtle.speed(0)
            self.turtle.penup()
            self.turtle.goto(self.pos[0], self.pos[1])
        elif type == "particle_a":
            # random vel, pos
            self.vel = np.array([np.random.uniform(-10, 10), np.random.uniform(-10, 10)], dtype=float)
            self.pos = np.array([np.random.uniform(-200, 200), np.random.uniform(-200, 200)], dtype=float)
            # fill up with random amount of energy
            self.energy = np.random.uniform(low=2, high=10)
            #self.energy = 5.0

            # set turtle
            self.turtle.shape("square")
            self.turtle.fillcolor("white")
            self.size = 5
            self.turtle.shapesize(stretch_wid=self.size/20, stretch_len=self.size/20)

            self.turtle.speed(0)
            self.turtle.penup()
            self.turtle.goto(self.pos[0], self.pos[1])
        elif type == "particle_b":
            # random vel and pos
            self.vel = np.array([np.random.uniform(-10, 10), np.random.uniform(-10, 10)], dtype=float)
            self.pos = np.array([np.random.uniform(-200, 200), np.random.uniform(-200, 200)], dtype=float)
            # fill up with random amount of energy
            self.energy = np.random.uniform(low=2, high=10)
            #self.energy = 5.0

            # set turtle
            self.turtle.shape("square")
            self.turtle.fillcolor("yellow")
            self.size = 5
            self.turtle.shapesize(stretch_wid=self.size / 20, stretch_len=self.size / 20)

            self.turtle.speed(0)
            self.turtle.penup()
            self.turtle.goto(self.pos[0], self.pos[1])
        else:
            print("no valid particle type")
            # do nothing
        return

    def __del__(self):
        self.turtle.hideturtle()
        self.turtle = 0

    def update_pos(self):
        # bounce off walls
        if 250 <= self.pos[0]:
            self.vel[0] *= -1
            self.pos[0] = 245
        elif self.pos[0] <= -250:
            self.vel[0] *= -1
            self.pos[0] = -245
        if 250 <= self.pos[1]:
            self.vel[1] *= -1
            self.pos[1] = 245
        elif self.pos[1] <= -250:
            self.vel[1] *= -1
            self.pos[1] = -245
        # update
        self.pos += self.vel
        self.turtle.setx(self.pos[0])
        self.turtle.sety(self.pos[1])
        return

    def add_vel(self, vector: np.array, scale: float):
        self.vel += (scale * vector)
        return

    def use_energy(self):
        # energy usage dependant on agents speed + const amount each timestep
        self.energy -= 0.1 + np.linalg.norm(self.vel) * 0.02
        return

    def eat(self):
        self.energy += 0.1
        #mixer.music.load("tone.mp3")
        #mixer.music.play()
        return


# PARTICLE SYSTEM
class ParticleSys:
    def __init__(self, num_particle_a: int, num_particle_b: int, num_foodsource: int):
        self.foodsources = [Particle(type="foodsource") for i in range(num_foodsource)]
        self.particles = [Particle(type="particle_a") for i in range(num_particle_a)] + \
                         [Particle(type="particle_b") for i in range(num_particle_b)]
        self.members = self.particles + self.foodsources
        # (list of members sorted by x and y koordinates in ascending order):
        self.members_sorted_x = sorted(self.members, key=lambda x: x.pos[0], reverse=False)
        self.members_sorted_y = sorted(self.members, key=lambda x: x.pos[1], reverse=False)
        self.interval_size = 5
        # system-wide parameters:
        self.weight_center_a = np.array([0, 0], dtype=float)
        self.weight_center_b = np.array([0, 0], dtype=float)
        return

    def update_pos(self):
        for obj in self.particles:
            obj.update_pos()
        return

    def sweep_and_prune(self):  # well its not actually SAP, but lets say its "SAP-inspired"
        # sort lists by coordinates
        self.members_sorted_x.sort(key=lambda x: x.pos[0], reverse=False)
        self.members_sorted_y.sort(key=lambda x: x.pos[1], reverse=False)

        #
        for i in range(0, len(self.members_sorted_x)-1, int(self.interval_size - 1)):
            temp_list_x = self.members_sorted_x[i: i + self.interval_size]
            for j in range(0, len(self.members_sorted_y)-1, int(self.interval_size - 1)):
                temp_list_y = self.members_sorted_y[j: j + self.interval_size]
                # list of particles that are near each other
                subset = return_subset(temp_list_x, temp_list_y)
                if len(subset) >= 2:    # at least two particles wich are near each other
                    for obj_a, obj_b in itertools.combinations(subset, 2):
                        # point away form neerest neighbors fom different species:

                        if self.check_if_neighbouring(obj_a, obj_b):
                            self.neighbour_response(obj_a, obj_b, len(subset))
                            if self.check_if_colliding(obj_a, obj_b):
                                self.colliding_response(obj_a, obj_b)
        return


    def neighbour_response(self, particle_a: Particle, particle_b: Particle, num_neighbours: int):
        # get direction
        direction = particle_a.pos - particle_b.pos
        # normalize vector
        dir_norm = np.linalg.norm(direction)
        direction = direction / dir_norm
        if particle_a.type == particle_b.type != "foodsource":
            particle_a.vel +=  alpha_v_3/num_neighbours * particle_b.vel                    # v_3
            particle_b.vel +=  alpha_v_3/num_neighbours * particle_a.vel                    # v_3
        elif particle_a.type == "foodsource":
            particle_b.vel += alpha_v_7 * direction                              # v_7
        elif particle_b.type == "foodsource":
            particle_a.vel -= alpha_v_7 * direction                              # v_7 (towards foodsource)
        elif particle_a.type != particle_b.type:                                            # v_6 (away from different species)
            particle_a.vel += alpha_v_6 * direction
            particle_b.vel -= alpha_v_6 * direction

        return


    def colliding_response(self, particle_a: Particle, particle_b: Particle):
        # get direction
        direction = particle_a.pos - particle_b.pos
        # normalize vector
        dir_norm = np.linalg.norm(direction)
        direction = direction / dir_norm
        if particle_a.type == particle_b.type != "foodsource":
            particle_a.vel += alpha_v_1 * direction                                         # v_1
            particle_b.vel -= alpha_v_1 * direction                                         # v_1
        elif particle_a.type == "foodsource":
            particle_b.eat()
        elif particle_b.type == "foodsource":
            particle_a.eat()

        return


    def get_weight_center(self, type):
        sumx = 0
        sumy = 0
        num_type = 0
        for obj in self.particles:
            if obj.type == type:
                sumx += obj.pos[0]
                sumy += obj.pos[1]
                num_type += 1
        if num_type == 0: return np.array([0, 0])
        center = np.array([sumx / num_type, sumy / num_type])
        return center

    def set_weight_center(self):
        self.weight_center_a = self.get_weight_center("particle_a")
        self.weight_center_b = self.get_weight_center("particle_b")
        return


    def check_if_neighbouring(self, a: Particle, b: Particle):
        distance = (a.size if a.size >= b.size else b.size) * 1.5
        if (((a.pos[0] - distance) <= b.pos[0] <= (a.pos[0] + distance))
                and ((a.pos[1] - distance) <= b.pos[1] <= (a.pos[1] + distance))):
            return True
        else:
            return False

    def check_if_colliding(self, a: Particle, b: Particle):
        distance = (a.size if a.size >= b.size else b.size) / 1.75
        if (((a.pos[0] - distance) <= b.pos[0] <= (a.pos[0] + distance))
                and ((a.pos[1] - distance) <= b.pos[1] <= (a.pos[1] + distance))):
            return True
        else:
            return False

    def update_vel(self):
        """
         calculate veclocity as weighted sum of these vectors:

         v_1: points away from neighbors in vicinity
         v_2: points to world center
         v_3: mean vector of neighbours
         v_4: points to center of weight of all agents
         v_5: random vector
         v_6: points away from neighbours of different species
         v_7: points to energy source
         """
        for obj in self.particles:
            #obj.vel = [0, 0]
            obj.add_vel(-1 * obj.pos/ np.linalg.norm(obj.pos), alpha_v_2)                            # v_2
            if obj.type == "particle_a":
                obj.add_vel(self.weight_center_a - obj.pos, alpha_v_4)      # v_4
            elif obj.type == "particle_b":
                obj.add_vel(self.weight_center_b - obj.pos, alpha_v_4)  # v_4
            obj.add_vel(np.random.random((2, )) - [0.5, 0.5], alpha_v_5)    # v_5
            self.sweep_and_prune()                                          # v_1 + v_3
            obj.vel *= dampening_factor
        return

    def live(self):
        for particle in self.particles:
            particle.use_energy()
            if particle.energy <= 0.5:
                particle.turtle.fillcolor("red")
            elif particle.type == "particle_a":
                particle.turtle.fillcolor("white")
            elif particle.type == "particle_b":
                particle.turtle.fillcolor("yellow")
            if particle.energy <= 0:
                particle.turtle.hideturtle()
                self.particles.remove(particle)
                mixer.music.load("DEATH.mp3")
                mixer.music.play()


def return_subset(list_a, list_b):
    subset = []
    for obj_a in list_a:
        for obj_b in list_b:
            if obj_a == obj_b:
                subset.append(obj_a)
    return subset


# TIMER
pen = turtle.Turtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(-250, 250-33)
pen.write("timer: 20", align="left", font=("Courier", 14, "normal"))

#  NUM LIVING PARTICLES
pen2 = turtle.Turtle()
pen2.speed(0)
pen2.color("white")
pen2.penup()
pen2.hideturtle()
pen2.goto(-250, 250-57)
pen2.write("alive: ", align="left", font=("Courier", 14, "normal"))


def update_timer(countdown: int):
    pen.clear()
    pen.write("timer: {}".format(countdown), align="left", font=("Courier", 14, "normal"))
    return


def update_num_living(num_living: int):
    pen2.clear()
    pen2.write("alive: {}".format(num_living), align="left", font=("Courier", 14, "normal"))


'''def press():
    print("button pressed!")
    return'''

# GUI https://compucademy.net/python-turtle-graphics-and-tkinter-gui-programming/
'''def show_alpha_v_1_values():
    print(alpha_v_1_scale.get())
    alpha_v_1 = alpha_v_1_scale.get() / 100
    return
def show_alpha_v_2_values():
    print(alpha_v_2_scale.get())
    alpha_v_2 = alpha_v_2_scale.get() / 100
    return


canvas2 = w.getcanvas()

text = tk.Label(master=canvas2.master, text="parameters for the flys speed and direction:")
text.pack()

frame_v_1 = tk.LabelFrame(master=canvas2.master, text="don't fly into neighbours", )
frame_v_1.pack()
alpha_v1_button = tk.Button(master=frame_v_1, text="click me", command=show_alpha_v_1_values)
alpha_v_1_scale = tk.Scale(master=frame_v_1, from_=0, to=100, length=300, orient="horizontal")
alpha_v_1_scale.pack(side="left")
alpha_v1_button.pack(side="right")

frame_v_2 = tk.LabelFrame(master=canvas2.master, text="fly towards world center")
frame_v_2.pack()
alpha_v2_button = tk.Button(master=frame_v_2, text="click me", command=show_alpha_v_2_values)
alpha_v_2_scale = tk.Scale(master=frame_v_2, from_=0, to=100, length=300, orient="horizontal")
alpha_v_2_scale.pack(side="left")
alpha_v2_button.pack(side="right")'''


'''screen2 = turtle.Screen()
screen2.bgcolor("cyan")
canvas = screen2.getcanvas()
button = tk.Button(canvas.master, text="Press me", command=press)
canvas.create_window(-200, -200, window=button)'''

def run_loop(particle_system: ParticleSys, countdown:int, start_time):
    living_start_time = start_time
    while countdown > 0:
        w.update()

        now_time = time.process_time()
        # update countdown (every second)
        if now_time >= start_time + 1.0:
            countdown -= 1
            update_timer(countdown)
            start_time = time.process_time()
        # update energy (every 0.1 sedonds)
        if now_time >= living_start_time + 0.1:
            ps.live()
            update_num_living(len(ps.particles))
            living_start_time = time.process_time()

        # update position
        ps.update_pos()
        ps.set_weight_center()
        ps.update_vel()

        update_num_living(len(particle_system.particles))

if __name__ == '__main__':

    ps = ParticleSys(num_particle_a=20, num_particle_b=20, num_foodsource=5)

    print("WELCOME TO 20 SECOND SWARM INTELLIGENCE!!")
    print("You can control the swarms behavior by changing these parameters:")
    print("I recommend scaling them somewhere between 0.001 (weak) and 0.5 (very strong).")

    # main loop:
    count_down = 20
    reference_time = time.process_time()
    #tk.mainloop()
    run_loop(particle_system=ps, countdown=count_down, start_time=reference_time)

    #w.bye()
