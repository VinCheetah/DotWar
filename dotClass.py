from canonClass import PipeCanon
from object import CircleObject, Body
from math import cos, sin


class Dot(Body, CircleObject):

    def __init__(self, x, y, vx, vy, radius):
        super().__init__(x=x, y=y, radius=radius, vx=vx, vy=vy, ax=0, ay=0)
        self.canon = None

    def shoot(self):
        self.canon.shoot()

    def set_canon(self, canon):
        self.canon = canon

    def accelerate(self, direction, power):
        self.ax = cos(direction) * power
        self.ay = sin(direction) * power

    def add_acceleration(self, direction, power):
        self.ax += cos(direction) * power
        self.ay += sin(direction) * power



class ClassicDot(Dot):

    def __init__(self, x, y):
        Dot.__init__(self, x, y, 0, 0, 30)
        self.set_canon(PipeCanon(self))

    def display(self):
        self.canon.display()
        self.draw_circle(color=(0, 0, 255))
        self.draw_circle(color=(0, 0, 0), width=3)