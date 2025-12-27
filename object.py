from math import sin, cos, pi
from utils import dist
import pygame

RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
WHITE = 255, 255, 255
BLACK = 0, 0, 0
GRAY = 128, 128, 128
LIGHTGRAY = 190, 190, 190
DARKGRAY = 80, 80, 80

class Object:

    game: "GameClass" = None
    tol = 1E-3

    def __init__(self, x:float = None, y:float =None, **kwargs):
        print("Initializing object")
        if x is not None and y is not None:
            self.x = x
            self.y = y

    @classmethod
    def set_game(cls, game):
        cls.game = game

    @property
    def pos(self):
        return self.x, self.y

    def display(self):
        raise NotImplementedError

    def contact(self, obj):
        raise NotImplementedError

    def distance(self, other):
        return dist(self.pos, other.pos)


class CircleObject(Object):

    def __init__(self, x:float, y:float, radius:float, **kwargs):
        print("Initializing circle object")
        super().__init__(x, y, **kwargs)
        self.radius = radius

    def contact(self, obj):
        if isinstance(obj, CircleObject):
            return self.distance(obj) < self.radius + obj.radius
        else:
            raise NotImplementedError

    def draw_circle(self, color=RED, pos=None, radius=None, width=0):
        radius = self.radius if radius is None else radius
        pos = self.pos if pos is None else pos
        pygame.draw.circle(self.game.screen, color, self.game.view(pos), radius*self.game.zoom, int(width*self.game.zoom))



class Body(Object):

    friction = 0.97

    def __init__(self, x:float, y:float, vx:float, vy:float, ax:float, ay:float, mass, **kwargs):
        print("Initializing moving object")
        super().__init__(x, y, **kwargs)

        self.mass = mass
        self.inv_mass = 0 if mass == float("inf") else 1 / mass

        self.angle = 0.0
        self.omega = 0.0  # vitesse angulaire

        self.inertia = 1.0
        self.inv_inertia = 1 / self.inertia if self.inertia > 0 else 0

        self.vx = vx
        self.vy = vy
        self.ax = ax
        self.ay = ay
        self.moving: bool = True

    def update_speed(self):
        self.vx += self.ax * self.game.dtime #- self.vx * (1 - self.friction)
        self.vy += self.ay * self.game.dtime #- self.vy * (1 - self.friction)
        self.vx *= self.friction
        self.vy *= self.friction
        if abs(self.vx) < self.tol and abs(self.vy) < self.tol:
            self.moving = False
            self.vx = 0
            self.vy = 0
        elif not self.moving:
            self.moving = True

    def update_pos(self):
        if self.moving:
            self.x += self.vx * self.game.dtime
            self.y += self.vy * self.game.dtime


    def update(self):
        self.update_speed()
        self.update_pos()

    def resolve_collision(self, normal, penetration, restitution=0.7):
        nx, ny = normal

        # correction position
        self.x += nx * penetration
        self.y += ny * penetration

        # réflexion vitesse
        vn = self.vx * nx + self.vy * ny
        if vn < 0:
            self.vx -= (1 + restitution) * vn * nx
            self.vy -= (1 + restitution) * vn * ny
