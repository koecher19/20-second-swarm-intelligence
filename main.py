"""
building a swarm intelligence (based on Swarm Evolve 1.0) for
20 SECONDS GAME JAM 2022 (https://itch.io/jam/20-second-game-jam)
Author: Felix Köcher (https://github.com/koecher19)
"""

import numpy as np
import turtle
import time
import itertools

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
alpha_v_1 = 0.01
alpha_v_2 = 0.01
alpha_v_3 = 0.1
alpha_v_4 = 0.2
alpha_v_5 = 0.001
alpha_v_6 = 0.1
alpha_v_7 = 0.1
dampening_factor = 0.98


# PARTICLE
class Particle:
    def __init__(self):
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.shape("square")
        self.turtle.fillcolor("white")
        self.turtle.penup()
        self.size = 5
        self.turtle.shapesize(stretch_wid=self.size/20, stretch_len=self.size/20)
        self.pos = np.array([0, 0], dtype=float)
        self.vel = np.array([np.random.uniform(-10, 10), np.random.uniform(-10, 10)], dtype=float)
        self.energy = np.random.randint(low=5, high=10)
        self.turtle.goto(self.pos[0], self.pos[1])
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
        self.energy -= 1


class FoodSource:
    def __init__(self):
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.pos = np.random.uniform(low=-240, high=240, size=(2, ))
        self.turtle.setx = self.pos[0]
        self.turtle.sety = self.pos[1]
        self.turtle.shape("circle")
        self.turtle.fillcolor("red")
        self.turtle.penup()
        self.size = 10
        self.turtle.shapesize(stretch_len=self.size/20, stretch_wid=self.size/20)
        self.turtle.goto(self.pos[0], self.pos[1])

# PARTICLE SYSTEM
class ParticleSys:
    def __init__(self, num_particles: int):
        self.members = [Particle() for i in range(num_particles)]
        # (list of members sorted by x and y koordinates in ascending order):
        self.members_sorted_x = sorted(self.members, key=lambda x: x.pos[0], reverse=False)
        self.members_sorted_y = sorted(self.members, key=lambda x: x.pos[1], reverse=False)
        self.interval_size = 5
        self.neighbour_distance = 10
        # system-wide parameters:
        self.weight_center = np.array([0, 0], dtype=float)
        return

    def update_pos(self):
        for obj in self.members:
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
                subset = return_subset(temp_list_x, temp_list_y)
                if len(subset) >= 2:
                    for obj_a, obj_b in itertools.combinations(subset, 2):
                        if self.check_if_neighbouring(obj_a, obj_b):
                            self.neighbour_response(obj_a, obj_b, len(subset))
        return

    def neighbour_response(self, particle_a: Particle, particle_b: Particle, num_neighbours: int):
        # get direction
        direction = particle_a.pos - particle_b.pos
        # normalize vector
        direction = direction / np.linalg.norm(direction)
        particle_a.vel += alpha_v_1 * direction + alpha_v_3/num_neighbours * particle_b.vel       # v_1 + v_3
        particle_b.vel -= alpha_v_1 * direction + alpha_v_3/num_neighbours * particle_a.vel       # v_1 + v_3
        return

    def get_weight_center(self):
        sumx = 0
        sumy = 0
        for obj in self.members:
            sumx += obj.pos[0]
            sumy += obj.pos[1]
        if len(self.members) == 0: return np.array([0, 0])
        center = np.array([sumx / len(self.members), sumy / len(self.members)])
        return center

    def set_weight_center(self):
        self.weight_center = self.get_weight_center()
        return

    def check_if_neighbouring(self, a: Particle, b: Particle):
        if (((a.pos[0] - self.neighbour_distance) <= b.pos[0] <= (a.pos[0] + self.neighbour_distance))
                and ((a.pos[1] - self.neighbour_distance) <= b.pos[1] <= (a.pos[1] + self.neighbour_distance))):
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
        for obj in self.members:
            #obj.vel = [0, 0]
            obj.add_vel(-1 * obj.pos, alpha_v_2)                    # v_2
            obj.add_vel(self.weight_center - obj.pos, alpha_v_4)    # v_4
            obj.add_vel(np.random.random((2, )), alpha_v_5)         # v_5
            self.sweep_and_prune()                                  # v_1 + v_3
            obj.vel *= dampening_factor
        return

    def live(self):
        for particle in self.members:
            particle.use_energy()
            if particle.energy <= 0:
                particle.turtle.hideturtle()
                self.members.remove(particle)


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
pen.goto(-250+30, 250-33)
pen.write("20", align="center", font=("Courier", 24, "normal"))


def update_timer(countdown: int):
    pen.clear()
    pen.write("{}".format(countdown), align="center", font=("Courier", 24, "normal"))
    return


if __name__ == '__main__':

    ps = ParticleSys(num_particles=50)
    fs = FoodSource()
    fs_2 = FoodSource()

    # main loop:
    count_down = 20
    reference_time = time.process_time()

    while count_down > 0:
        w.update()
        now_time = time.process_time()
        if now_time >= reference_time + 1.0:
            count_down -= 1
            update_timer(count_down)
            reference_time = time.process_time()

            ps.live()

        # update position
        ps.update_pos()
        ps.set_weight_center()
        ps.update_vel()

    w.bye()
