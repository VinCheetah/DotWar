from object import Object
from math import cos, sin
import bulletClass

class Pipe(Object):

    def __init__(self, dot, angle, bullet, power, reload):
        Object.__init__(self)
        self._angle = angle
        self.bullet = bullet
        self.power = power
        self.dot = dot
        self.last_shot = 0.
        self.reload = reload

    @property
    def angle(self):
        return self._angle + self.dot.angle

    @property
    def x(self):
        return self.dot.x + self.dot.size * sin(self.angle)

    @property
    def y(self):
        return self.dot.y + self.dot.size * cos(self.angle)

    def shoot(self):
        if self.game.time - self.last_shot > self.reload:
            self.last_shot = self.game.time
            self.shoot_bullet()

    def shoot_bullet(self):
        self.game.new_bullet(self.bullet.fire(self.pos, self.power, self.angle, ))

    def display(self):
        pass



class ClassicPipe(Pipe):

    def __init__(self, dot, angle):
        Pipe.__init__(self, dot, angle, bulletClass.ClassicBullet, 3, 0.5)

    def shoot(self):
        ...
