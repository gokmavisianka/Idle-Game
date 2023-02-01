from threading import Thread
from random import randint, choice
from time import time, perf_counter, sleep
import pygame

pygame.init()
ON = True


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y


class Velocity:
    def __init__(self, x, y):
        self.x, self.y = x, y


velocity_map = {("left", "up"): Velocity(-1, -1),
                ("left", "middle"): Velocity(-1, 0),
                ("left", "down"): Velocity(-1, 1),
                ("middle", "up"): Velocity(0, -1),
                ("middle", "middle"): Velocity(0, 0),
                ("middle", "down"): Velocity(0, 1),
                ("right", "up"): Velocity(1, -1),
                ("right", "middle"): Velocity(1, 0),
                ("right", "down"): Velocity(1, 1)}


def find_corners(element):
    A = Point(element.x, element.y)
    B = Point(element.x + element.width, element.y)
    C = Point(element.x, element.y + element.height)
    D = Point(element.x + element.width, element.y + element.height)
    corners = (A, B, C, D)
    return corners


def is_in_rectangle(point, element):
    if (element.x <= point.x <= (element.x + element.width)) and (element.y <= point.y <= element.y + element.height):
        return True
    else:
        return False


def check_collision(K, J):
    A, B, C, D = find_corners(K)
    if is_in_rectangle(A, J) or is_in_rectangle(B, J) or is_in_rectangle(C, J) or is_in_rectangle(D, J):
        return True
    else:
        return False


def find_distance(K, J):
    x = find_difference(K, J, axis="x")
    y = find_difference(K, J, axis="y")
    hypotenuse = (x ** 2 + y ** 2) ** 0.5
    return hypotenuse


def find_difference(K, J, axis):
    if axis == "x":
        difference = (K.x + K.width / 2) - (J.x + J.width / 2)
    elif axis == "y":
        difference = (K.y + K.height / 2) - (J.y + J.height / 2)
    else:
        raise ValueError(f"axis must be 'x' or 'y' but '{axis}' is given instead.")
    return difference


def find_direction(K, J, axis):
    difference = find_difference(K, J, axis)
    if axis == "x":
        if difference > 0:
            direction = "left"
        elif difference < 0:
            direction = "right"
        else:
            direction = "middle"
    elif axis == "y":
        if difference > 0:
            direction = "up"
        elif difference < 0:
            direction = "down"
        else:
            direction = "middle"
    else:
        raise ValueError(f"axis must be 'x' or 'y' but '{axis}' is given instead.")
    return direction


def find_velocity(K, J):
    direction_x = find_direction(K, J, axis="x")
    direction_y = find_direction(K, J, axis="y")
    velocity = velocity_map[(direction_x, direction_y)]
    return velocity


def move(K, J, coefficient=1):
    velocity = find_velocity(K, J)
    K.x += velocity.x * coefficient
    K.y += velocity.y * coefficient


def _draw_(element):
    pygame.draw.rect(game.display, element.color, (element.x, element.y, element.width, element.height))


def _draw_all_(elements):
    for element in elements:
        element.draw()


def _terminate_all_(elements):
    for element in elements:
        element.terminate()


class Floor:
    def __init__(self, level=0):
        self.level = level
        self.x, self.y = 0, 0
        self.width, self.height = 0, 0
        self.operate = True
        self.occupied = False
        self.exists = False
        self.color = (0, 125, 0)
        self.chance = 50
        self.child = None
        self.spawnables = spawnables.dictionary[level]

    def create(self, position, size):
        floors.elements.append(self)
        self.x, self.y = position
        self.width, self.height = size
        self.exists = True

    def destroy(self):
        floors.elements.remove(self)
        self.occupied = False
        self.child.destroy()
        self.exists = False

    def spawn(self):
        if not self.occupied and self.exists:
            variable = randint(0, 999)
            if variable < self.chance:
                spawnable = choice(self.spawnables).duplicate()
                center = (self.x + (self.width / 2), self.y + (self.height / 2))
                position = (center[0] - (spawnable.width / 2), center[1] - (spawnable.height / 2))
                spawnable.create(self, position)

    def draw(self):
        if self.exists:
            _draw_(self)

    def terminate(self):
        self.operate = False


class Floors:
    def __init__(self):
        self.elements = []
        self.operate = True

    def draw_all(self):
        for element in self.elements:
            element.draw()

    def terminate_all(self):
        _terminate_all_(self.elements)
        self.operate = False

    def spawn_all(self):
        def function():
            for element in self.elements:
                element.spawn()

        def thread():
            while self.operate:
                function()
                sleep(1)

        Thread(target=thread, args=()).start()


class Spawnables:
    def __init__(self):
        self.dictionary = {0: [Grass()]}
        self.operate = True
        self.elements = []

    def draw_all(self):
        for element in self.elements:
            element.draw()

    def terminate_all(self):
        _terminate_all_(self.elements)
        self.operate = False


class Grass:
    def __init__(self):
        self.x, self.y = 0, 0
        self.width, self.height = 50, 50
        self.parent = None
        self.color = (0, 255, 0)
        self.operate = True
        self.exists = False
        self.is_target = False

    def create(self, parent, position):
        self.parent = parent
        self.x, self.y = position
        spawnables.elements.append(self)
        self.parent.occupied = True
        self.parent.child = self
        self.exists = True

    def destroy(self):
        spawnables.elements.remove(self)
        self.parent.occupied = False
        self.parent.child = None
        self.exists = False
        del self

    def draw(self):
        _draw_(self)

    def duplicate(self):
        return Grass()

    def terminate(self):
        self.operate = False


class Farmers:
    def __init__(self):
        self.elements = []
        self.operate = True

    def all_start_harvesting(self):
        def thread():
            while self.operate:
                for element in self.elements:
                    if not element.busy:
                        Thread(target=element.harvest, args=()).start()
                sleep(1 / 30)
        Thread(target=thread, args=()).start()

    def draw_all(self):
        _draw_all_(self.elements)

    def terminate_all(self):
        _terminate_all_(self.elements)
        self.operate = False


class Farmer:
    def __init__(self, position, size):
        self.previous_target = None
        farmers.elements.append(self)
        self.velocity = Velocity(0, 0)
        self.x, self.y = position
        self.width, self.height = size
        self.color = (255, 255, 0)
        self.harvesting = False
        self.operate = True
        self.busy = False

    def choose_target(self, case):
        spawnable = None
        if case == "closest":
            distances = {}
            for element in spawnables.elements:
                if not element.is_target:
                    distance = find_distance(self, element)
                    distances[distance] = element
            if len(distances) != 0:
                shortest_distance = min(distances)
                spawnable = distances[shortest_distance]
                spawnable.is_target = True
                if spawnable is not self.previous_target and self.previous_target is not None:
                    self.previous_target.is_target = False
        else:
            raise ValueError(f"case must be 'closest' but '{case}' is given instead.")
        self.previous_target = spawnable
        return spawnable

    def harvest(self):
        if not self.busy:
            self.busy = True
            target = self.choose_target(case="closest")
            while self.operate:
                sleep(1/60)
                for spawnable in spawnables.elements:
                    if check_collision(self, spawnable):
                        spawnable.destroy()
                        game.money += 1
                if target is not None:
                    if target.exists:
                        move(self, target)
                    else:
                        self.busy = False
                        break
                else:
                    self.busy = False
                    break

    def draw(self):
        _draw_(self)

    def terminate(self):
        self.harvesting = False
        self.operate = False


class Game:
    def __init__(self, window_size=(1000, 1000)):
        self.width, self.height = window_size
        self.display = pygame.display.set_mode(window_size)
        self.font = pygame.font.SysFont("Monospace", 32)
        self.background_color = (0, 255, 255)
        self.objects_to_draw = []
        self.spawnables = []
        self.operate = True
        self.money = 1

    def setup(self):
        self.spawnables.append(Grass())
        for row in range(0, 5):
            for column in range(0, 5):
                position = (250 + (100 * column), 250 + (100 * row))
                size = (100, 100)
                floor = Floor()
                floor.create(position, size)
                floors.elements.append(floor)
        Thread(target=self.draw_and_update).start()
        floors.spawn_all()
        f1, f2, f3 = Farmer((300, 300), (30, 30)), Farmer((700, 300), (30, 30)), Farmer((300, 700), (30, 30))
        farmers.all_start_harvesting()

    def draw_and_update(self):
        time_interval = 1 / 30
        sleep(0.25)
        while self.operate:
            initial_time = perf_counter()
            self.display.fill(self.background_color)
            self.draw_all()
            sleep(time_interval)
            final_time = perf_counter()
            difference = final_time - initial_time
            FPS = round(1 / difference)
            text_FPS = self.font.render(f"FPS: {FPS}", True, (255, 0, 0))
            text_money = self.font.render(f"Money: {self.money}", True, (255, 0, 0))
            self.display.blit(text_FPS, (0, 0))
            self.display.blit(text_money, (840 - (19 * len(str(self.money))), 0))
            pygame.display.flip()

    def draw_all(self):
        floors.draw_all()
        spawnables.draw_all()
        farmers.draw_all()

    def terminate(self):
        self.operate = False

    def terminate_all(self):
        floors.terminate_all()
        spawnables.terminate_all()
        farmers.terminate_all()
        self.terminate()


spawnables = Spawnables()
floors = Floors()
farmers = Farmers()
game = Game()
game.setup()

while ON:
    sleep(0.04)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.terminate_all()
            On = False
            sleep(1.1)
            pygame.quit()
            quit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        game.terminate_all()
        ON = False
        sleep(1.1)
        pygame.quit()
        quit()
