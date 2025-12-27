from object import Body, CircleObject

class Bullet(Body, CircleObject):

    def __init__(self, x, y, vx, vy, weight):
        super().__init__(x=x, y=y, vx=vx, vy=vy, ax=0, ay=0)
        self.weight = weight

    def display(self):
        raise NotImplementedError


class ClassicBullet(Bullet):

    def __init__(self, x, y, vx, vy):
        Bullet.__init__(self, x, y, vx, vy, weight=0.5)

    def display(self):
        self.draw_circle()
        self.draw_circle(color=(0, 0, 0), width=2)