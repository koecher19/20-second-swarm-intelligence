"""
building a swarm intelligence (based on Swarm Evolve 1.0) for
20 SECONDS GAME JAM 2022 (https://itch.io/jam/20-second-game-jam)
Author: Felix Köcher (https://github.com/koecher19)
"""

import numpy as np
import turtle
import time

# WINDOW
w = turtle.Screen()
w.title("20 Seconds Culture")
w.bgcolor("black")
w.setup(width=500, height=500)
w.tracer(0)


# PARTICLE
class Particle:
    def __init__(self):
        self.turtle = turtle.Turtle()
        self.turtle.speed(0)
        self.turtle.shape("square")
        self.turtle.fillcolor("white")
        self.turtle.penup()
        self.turtle.shapesize(stretch_wid=0.25, stretch_len=0.25)
        self.pos = np.array([0, 0])
        self.vel = np.array([np.random.randint(-10, 10), np.random.randint(-10, 10)])
        self.turtle.goto(self.pos[0], self.pos[1])
        return

    def update_pos(self):
        # bounce off walls
        if 250 <= self.pos[0] or self.pos[0] <= -250:
            self.vel[0] *= -1
        if 250 <= self.pos[1] or self.pos[1] <= -250:
            self.vel[1] *= -1
        # update
        self.pos += self.vel
        self.turtle.setx(self.pos[0])
        self.turtle.sety(self.pos[1])
        return

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
        return


# PARTICLE SYSTEM
class ParticleSys:
    def __init__(self, num_particles: int):
        self.members = [Particle() for i in range(num_particles)]
        return

    def update_pos(self):
        for obj in self.members:
            obj.update_pos()
        return



# TIMER
pen = turtle.Turtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(-250+30, 250-33)
pen.write("20", align="center", font=("Courier", 24, "normal"))


def update_timer(frame_number):
    pen.clear()
    pen.write("{}".format(frame_number), align="center", font=("Courier", 24, "normal"))
    return


if __name__ == '__main__':

    ps = ParticleSys(num_particles=50)

    # main loop:
    frames_per_second = 24
    for frame in range(0, frames_per_second * 20):
        w.update()
        time.sleep(1/frames_per_second)
        update_timer(int(20 - (frame/frames_per_second)))

        # update position
        ps.update_pos()

    w.bye()
