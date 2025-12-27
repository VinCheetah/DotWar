from object import Body, CircleObject
import pygame
import random
import math

def random_convex_polygon(cx, cy, radius, n=8):
    angles = sorted(random.uniform(0, 2*math.pi) for _ in range(n))
    points = []

    for a in angles:
        r = radius * random.uniform(0.2, 1.0)
        points.append((
            cx + math.cos(a) * r,
            cy + math.sin(a) * r
        ))

    return points
def dot(ax, ay, bx, by):
    return ax*bx + ay*by


def clamp(v, a, b):
    return max(a, min(v, b))


def dist_point_segment(px, py, ax, ay, bx, by):
    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay

    ab_len2 = abx*abx + aby*aby
    if ab_len2 == 0:
        dx = px - ax
        dy = py - ay
        return dx*dx + dy*dy

    t = clamp(dot(apx, apy, abx, aby) / ab_len2, 0, 1)
    cx = ax + abx * t
    cy = ay + aby * t

    dx = px - cx
    dy = py - cy
    return dx*dx + dy*dy

def dot(ax, ay, bx, by):
    return ax * bx + ay * by


def clamp(v, a, b):
    return max(a, min(v, b))


def closest_point_on_segment(px, py, ax, ay, bx, by):
    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay

    ab_len2 = abx*abx + aby*aby
    if ab_len2 == 0:
        return ax, ay

    t = clamp((apx*abx + apy*aby) / ab_len2, 0, 1)
    return ax + abx*t, ay + aby*t


class Obstacle(Body):

    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, 0, 0, 0, 0, **kwargs)

    def draw(self):
        raise NotImplementedError

    def collide_circle(self, circ):
        """
        Collision avec un cercle de centre (x,y) et rayon r
        Retourne True si collision
        """
        raise NotImplementedError

class CircleObstacle(Obstacle, CircleObject):

    def __init__(self, x, y, radius):
        super().__init__(x=x, y=y, radius=radius)

    def display(self):
        self.draw_circle(color=(130, 60, 20))

    def collide_circle(self, circ):
        dx = circ.x - self.x
        dy = circ.y - self.y
        dist = math.hypot(dx, dy)

        min_dist = self.radius + circ.radius
        if dist >= min_dist or dist == 0:
            return False, None, 0

        nx = dx / dist
        ny = dy / dist
        penetration = min_dist - dist

        return True, (nx, ny), penetration



class PolygonObstacle(Obstacle):

    def __init__(self, x, y, r):
        super().__init__(x, y)

        n_points = random.randint(3, 12)
        #self.points = [(self.x + random.uniform(-r, r), self.y + random.uniform(-r, r)) for _ in range(n_points)]
        self.points = random_convex_polygon(x, y, r, n_points)

    def display(self):
        pygame.draw.polygon(
            self.game.screen,
            (90, 90, 90),
            [self.game.view(p) for p in self.points]
        )

    def collide_circle(self, circ):
        closest_dist2 = float("inf")
        closest_normal = None

        n = len(self.points)

        # 1️⃣ distance aux arêtes
        for i in range(n):
            ax, ay = self.points[i]
            bx, by = self.points[(i+1) % n]

            cx, cy = closest_point_on_segment(
                circ.x, circ.y, ax, ay, bx, by
            )

            dx = circ.x - cx
            dy = circ.y - cy
            d2 = dx*dx + dy*dy

            if d2 < closest_dist2:
                closest_dist2 = d2
                dist = math.sqrt(d2) if d2 > 1e-9 else 1e-9
                closest_normal = (dx/dist, dy/dist)

        if closest_dist2 <= circ.radius * circ.radius:
            penetration = circ.radius - math.sqrt(closest_dist2)
            return True, closest_normal, penetration

        # 2️⃣ centre à l’intérieur
        if self.point_inside(circ.x, circ.y):
            # normale approximée : vers le centre du polygone
            cx = sum(p[0] for p in self.points) / n
            cy = sum(p[1] for p in self.points) / n
            dx = circ.x - cx
            dy = circ.y - cy
            dist = math.hypot(dx, dy) or 1e-6
            return True, (dx/dist, dy/dist), circ.radius

        return False, None, 0


    def point_inside(self, x, y):
        inside = False
        n = len(self.points)

        for i in range(n):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i+1) % n]

            if ((y1 > y) != (y2 > y)) and \
               (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1):
                inside = not inside

        return inside


class Map:

    def __init__(self, size, bonus, obstacles):
        self.size = size
        self.bonus = bonus
        self.obstacles = obstacles

    def delete(self):
        ...

    def display(self):
        for obstacle in self.obstacles:
            obstacle.display()


class EmptyMap(Map):

    def __init__(self):
        Map.__init__(self, (100, 100), [], [])

class CircleMap(Map):

    def __init__(self):
        l, L = 2000, 2000
        Map.__init__(self, (l, L), [], [CircleObstacle(random.uniform(-l, l), random.uniform(-L, L), random.uniform(1, 100)) for _ in range(100)])


class PolygonMap(Map):

    def __init__(self):
        l, L = 2000, 2000
        Map.__init__(self, (l, L), [], [PolygonObstacle(random.uniform(-l, l), random.uniform(-L, L), random.uniform(30, 150)) for _ in range(100)])
