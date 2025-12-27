import mapClass
from time import time
from dotClass import ClassicDot
import pygame
from math import pi, atan2, cos, sin, floor
from object import Object


class Game:

    player_power = 3000

    def __init__(self):
        Object.set_game(self)
        self.pressed = dict()
        self.map = None
        self.paused: bool = False
        self.running: bool = False
        self.player = ClassicDot(0, 0)

        self.width = 800
        self.height = 600
        self.view_center_x = 0
        self.view_center_y = 0
        self.screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)


        self.zoom = 1
        self.mouse_direction = 0
        self.fps: float = 60
        self.last_frame_time: float = 0.

        self.time: float = 0
        self.time_speed: float = 1.
        self.dtime: float = 0

        self.dots = {self.player}
        self.bullets = set()

    def start(self):
        self.running = True
        self.get_new_map()
        while self.running:
            self.interactions()
            while (time() - self.last_frame_time) * 1000 < 1 / self.fps and self.running:
                print((time() - self.last_frame_time) / 1000)
                self.interactions()
            self.update()
            self.display()

    def update(self):
        self.dtime = (time() - self.time) * self.time_speed * (not self.paused)
        self.time += self.dtime
        if self.dtime > 0:
            self.player.ax = self.player.ay = 0
            for rot, key in [(0, pygame.K_UP), (-pi / 2, pygame.K_LEFT), (pi, pygame.K_DOWN), (pi / 2, pygame.K_RIGHT)]:
                if self.pressed.get(key):
                    self.player.add_acceleration(self.player_orientation() + rot, self.player_power)
            self.update_dots()
            self.update_bullets()
            for obstacle in self.map.obstacles:
                hit, normal, penetration = obstacle.collide_circle(self.player)
                if hit:
                    self.player.resolve_collision(normal, penetration)

    def interactions(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    self.pressed[event.key] = True

                if event.key == pygame.K_SPACE:
                    self.player_shoot()
                elif event.key == pygame.K_z:
                    self.player_move_front()
                elif event.key == pygame.K_q:
                    self.player_move_left()
                elif event.key == pygame.K_d:
                    self.player_move_right()
                elif event.key == pygame.K_s:
                    self.player_move_back()

                elif event.key == pygame.K_i:
                    self.zoom *= 1.1
                elif event.key == pygame.K_o:
                    self.zoom /= 1.1

                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    self.pressed[event.key] = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen_resize()
            elif event.type == pygame.QUIT:
                self.running = False

    def display(self):
        self.last_frame_time = time()
        self.screen.fill((190, 190, 190))
        self.display_grid()
        self.map.display()
        self.display_dots()
        self.display_bullets()
        x = self.player.x + cos(self.player_orientation()) * 30
        y = self.player.y + sin(self.player_orientation()) * 30
        self.player.draw_circle(pos=(x, y), radius=8)
        self.view_center_x = self.player.x
        self.view_center_y = self.player.y
        pygame.display.flip()

    def player_orientation(self):
        mouse_coord = self.unview(pygame.mouse.get_pos())
        return atan2(mouse_coord[1] - self.player.y, mouse_coord[0] - self.player.x)

    def update_dots(self):
        for dot in self.dots:
            dot.update()

    def update_bullets(self):
        for bullet in self.bullets:
            bullet.update()

    def display_grid(self):
        surface = self.screen
        W, H = surface.get_size()

        zoom = self.zoom
        cx = self.view_center_x
        cy = self.view_center_y

        # ---- visible world bounds ----
        half_w = W / (2 * zoom)
        half_h = H / (2 * zoom)

        world_left = cx - half_w
        world_right = cx + half_w
        world_top = cy - half_h
        world_bottom = cy + half_h

        # ---- adaptive grid spacing ----
        base_grid = 50  # world units
        grid = base_grid

        while grid * zoom < 30:
            grid *= 2
        while grid * zoom > 120:
            grid /= 2

        # ---- vertical lines ----
        x = floor(world_left / grid) * grid
        while x <= world_right:
            sx1, sy1 = self.view((x, world_top))
            sx2, sy2 = self.view((x, world_bottom))

            if abs(x) < 1e-6:
                color = (160, 160, 160)
                width = 2
            else:
                color = (210, 210, 210)
                width = 1

            pygame.draw.line(surface, color, (sx1, sy1), (sx2, sy2), width)
            x += grid

        # ---- horizontal lines ----
        y = floor(world_top / grid) * grid
        while y <= world_bottom:
            sx1, sy1 = self.view((world_left, y))
            sx2, sy2 = self.view((world_right, y))

            if abs(y) < 1e-6:
                color = (160, 160, 160)
                width = 2
            else:
                color = (210, 210, 210)
                width = 1

            pygame.draw.line(surface, color, (sx1, sy1), (sx2, sy2), width)
            y += grid

    def display_dots(self):
        for dot in self.dots:
            dot.display()

    def display_bullets(self):
        for bullet in self.bullets:
            bullet.display()

    def get_new_map(self):
        #self.map = mapClass.EmptyMap()
        self.map =mapClass.CircleMap()
        self.map = mapClass.PolygonMap()

    def player_shoot(self):
        ...

    def player_move_front(self):
        self.player.accelerate(self.mouse_direction, self.player_power)

    def player_move_left(self):
        self.player.accelerate(self.mouse_direction - pi / 2, self.player_power)

    def player_move_right(self):
        self.player.accelerate(self.mouse_direction + pi / 2, self.player_power)

    def player_move_back(self):
        self.player.accelerate(self.mouse_direction + pi, self.player_power)

    def view_x(self, x):
        return int((x - self.view_center_x) * self.zoom + self.width / 2)

    def view_y(self, y):
        return int((y - self.view_center_y) * self.zoom + self.height / 2)

    def view(self, p):
        return self.view_x(p[0]), self.view_y(p[1])

    def unview_x(self, x):
        return (x - self.width / 2) / self.zoom + self.view_center_x

    def unview_y(self, y):
        return (y - self.height / 2) / self.zoom + self.view_center_y

    def unview(self, p):
        return self.unview_x(p[0]), self.unview_y(p[1])

    def actu_dimensions(self):
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h

    def screen_resize(self):
        self.actu_dimensions()
        self.display()
        pygame.display.flip()