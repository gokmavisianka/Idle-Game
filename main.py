"""
MIT License
Copyright (c) 2023 Rasim Mert YILDIRIM
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from threading import Thread
from random import randint, choice
from time import time, perf_counter, sleep
import json
import pygame

pygame.init()
ON = True


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y


class Velocity:
    def __init__(self, x, y):
        self.x, self.y = x, y


class Texts:
    def __init__(self):
        self.elements = []

    def update_and_draw_all(self):
        for text in self.elements:
            text.update()
            text.draw()


class Text:
    def __init__(self, string, color, function, base_x, base_y, max_width, max_height):
        self.font = pygame.font.SysFont("Monospace", 32)
        self.base_x, self.base_y, self.max_width, self.max_height = base_x, base_y, max_width, max_height
        self.function = function
        self.string = string
        self.color = color
        self.length = len(self.string)
        self.width = self.length * 19
        self.text = self.font.render(self.string, True, self.color)
        self.position = Point(0, 0)
        self.position.y = self.base_y + (self.max_height - 38) / 2
        self.is_full = False
        texts.elements.append(self)

    def update(self):
        if not self.is_full:
            variable = self.function()
            string = self.string + str(variable) + "$"
        else:
            string = self.string + "(Full)"
        self.length = len(string)
        self.width = self.length * 19
        self.text = self.font.render(string, True, self.color)
        self.position.x = self.base_x + (self.max_width - self.width) / 2

    def draw(self):
        game.display.blit(self.text, (self.position.x, self.position.y))


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


def move(K, J):
    speed = workers.speed_map[workers.level]
    velocity = find_velocity(K, J)
    K.x += velocity.x * speed
    K.y += velocity.y * speed


def _draw_(element):
    pygame.draw.rect(game.display, element.color, (element.x, element.y, element.width, element.height))


def _draw_all_(elements):
    for element in elements:
        element.draw()


def _terminate_all_(elements):
    for element in elements:
        element.terminate()


class Floor:
    def __init__(self):
        self.x, self.y = 0, 0
        self.width, self.height = 0, 0
        self.time_to_next = 100
        self.operate = True
        self.occupied = False
        self.grown = False
        self.exists = False
        self.color = (0, 125, 0)
        self.chance = 1000
        self.child = None

    def create(self, position, size):
        floors.elements.append(self)
        self.x, self.y = position
        self.width, self.height = size
        self.exists = True
        self.set_time()

    def destroy(self):
        floors.elements.remove(self)
        self.occupied = False
        self.child.destroy()
        self.exists = False

    def set_time(self):
        self.time_to_next = perf_counter() + randint(1, 300 - spawnables.cooldown_reduction * 10) / 10

    def spawn(self):
        if not self.occupied and not self.grown and self.exists:
            if perf_counter() > self.time_to_next:
                spawnable = Spawnable()
                center = (self.x + (self.width / 2), self.y + (self.height / 2))
                position = (center[0] - (spawnable.width / 2), center[1] - (spawnable.height / 2))
                spawnable.create(self, position)
                self.grown = True
                self.set_time()

    def check_occupation(self):
        condition = False
        for worker in workers.elements:
            if check_collision(worker, self):
                condition = True
                break
        if condition is True:
            self.occupied = True
        else:
            self.occupied = False

    def draw(self):
        if self.exists:
            pygame.draw.rect(game.display, floors.colors[spawnables.level], (self.x, self.y, self.width, self.height))

    def terminate(self):
        self.operate = False


class Floors:
    def __init__(self, frame_color=(0, 0, 0)):
        self.colors = {1: (0, 125, 0), 2: (105, 105, 105), 3: (48, 25, 52)}
        self.frame_position = Point(0, 0)
        self.frame_color = frame_color
        self.frame_size = 0
        self.level = 1
        self.update_frame_position_size()
        self.elements = []
        self.operate = True

    def draw_all(self):
        self.draw_frame()
        for element in self.elements:
            element.draw()

    def update_frame_position_size(self):
        self.frame_position.x = (game.width / 2) - (100 * self.level) - 470 - 5
        self.frame_position.y = (game.height / 2) - (100 * self.level) - 50 - 5
        self.frame_size = 100 + (2 * self.level * 100) + 10

    def draw_frame(self):
        x, y = self.frame_position.x, self.frame_position.y
        width = height = self.frame_size
        pygame.draw.rect(game.display, self.frame_color, (x, y, width, height))

    def terminate_all(self):
        _terminate_all_(self.elements)
        self.operate = False

    def all_check_occupation(self):
        for floor in self.elements:
            floor.check_occupation()

    def get_level(self):
        return self.level

    def increase_level(self):
        self.level += 1
        self.create_all()
        self.update_frame_position_size()

    def destroy_all(self):
        for floor in self.elements:
            floor.operate = False
            floor.exists = False
        self.elements = []

    def create_all(self):
        self.destroy_all()
        self.update_frame_position_size()
        self.draw_frame()
        length = 100
        for row in range(0, 1 + (2 * self.level)):
            for column in range(0, 1 + (2 * self.level)):
                x = (game.width / 2) - (length / 2) - (100 * self.level) + (100 * row) - 420
                y = (game.height / 2) - (length / 2) - (100 * self.level) + (100 * column)
                floor = Floor()
                floor.create(position=(x, y), size=(length, length))
                self.elements.append(floor)

    def spawn_all(self):
        def function():
            for floor in self.elements:
                floor.check_occupation()
                floor.spawn()

        def thread():
            while self.operate:
                function()
                sleep(0.1)

        Thread(target=thread, args=()).start()


class Spawnables:
    def __init__(self):
        self.colors = {1: (0, 185, 0), 2: (145, 145, 145), 3: (98, 75, 102)}
        self.level = 1
        self.cooldown_reduction = 0
        self.operate = True
        self.elements = []

    def draw_all(self):
        for element in self.elements:
            element.draw()

    def terminate_all(self):
        _terminate_all_(self.elements)
        self.operate = False

    def get_cooldown_reduction(self):
        return self.cooldown_reduction

    def get_level(self):
        return self.level

    def increase_cooldown_reduction(self):
        self.cooldown_reduction += 1

    def increase_level(self):
        self.level += 1


class Spawnable:
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
        self.parent.grown = True
        self.parent.child = self
        self.exists = True

    def destroy(self):
        spawnables.elements.remove(self)
        self.parent.grown = False
        self.parent.child = None
        self.exists = False

    def draw(self):
        pygame.draw.rect(game.display, spawnables.colors[spawnables.level], (self.x, self.y, self.width, self.height))

    def terminate(self):
        self.operate = False


class Workers:
    def __init__(self):
        self.speed_map = {1: 1, 2: 2, 3: 5, 4: 10, 5: 20, 6: 25, 7: 50, 8: 100}
        self.color_map = {1: (255, 252, 0), 2: (255, 216, 0), 3: (255, 180, 0), 4: (158, 155, 0),
                          5: (255, 108, 0), 6: (255, 72, 0), 7: (255, 36, 0), 8: (255, 0, 0)}
        self.elements = []
        self.operate = True
        self.amount = 1
        self.level = 1

    def draw_all(self):
        _draw_all_(self.elements)

    def fix_position_all(self):
        for worker in self.elements:
            worker.fix_position()

    def create(self):
        length = 30
        x = (game.width / 2) - (length / 2) - 420
        y = (game.height / 2) - (length / 2)
        worker = Worker(position=(x, y), size=(length, length))
        self.elements.append(worker)
        Thread(target=worker.harvest, args=()).start()

    def create_all(self):
        for n in range(self.amount):
            self.create()

    def terminate_all(self):
        _terminate_all_(self.elements)
        self.operate = False

    def get_amount(self):
        return self.amount

    def get_level(self):
        return self.level

    def increase_amount(self):
        self.amount += 1
        self.create()

    def increase_level(self):
        self.level += 1
        self.fix_position_all()


class Worker:
    def __init__(self, position, size):
        self.previous_target = None
        self.velocity = Velocity(0, 0)
        self.x, self.y = position
        self.width, self.height = size
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

    def fix_position(self):
        length = 30
        self.x = (game.width / 2) - (length / 2) - 420
        self.y = (game.height / 2) - (length / 2)

    def harvest(self):
        while self.operate:
            target = self.choose_target(case="closest")
            while self.operate:
                sleep(1 / 30)
                for spawnable in spawnables.elements:
                    if check_collision(self, spawnable):
                        spawnable.destroy()
                        game.money += spawnables.level * 10
                if target is not None:
                    if target.exists:
                        move(self, target)
                    else:
                        break
                else:
                    break

    def draw(self):
        pygame.draw.rect(game.display, workers.color_map[workers.level], (self.x, self.y, self.width, self.height))

    def terminate(self):
        self.harvesting = False
        self.operate = False


class Buttons:
    def __init__(self):
        self.elements = []

    def draw_all(self):
        for button in self.elements:
            button.draw()

    def check(self, mouse_position):
        for button in self.elements:
            if is_in_rectangle(mouse_position, button):
                button.on_click()

    @staticmethod
    def create_all():
        Button((1085, 90), (740, 98), "Expand ", 0, (155, 155, 155), (0, 0, 0),
               (0, 0, 0), 250, 4, floors.get_level, floors.increase_level)
        Button((1085, 90 * 2 + 108 + 5), (740, 98), "Hire a Worker ", 0, (155, 155, 155), (0, 0, 0),
               (0, 0, 0), 100, 9, workers.get_amount, workers.increase_amount)
        Button((1085, 90 * 3 + 108 * 2 + 5), (740, 98), "Increase Speed of Workers ", 0, (155, 155, 155), (0, 0, 0),
               (0, 0, 0), 40, 8, workers.get_level, workers.increase_level)
        Button((1085, 90 * 4 + 108 * 3 + 5), (740, 98), "Reduce the Max Time to Grow ", 10, (155, 155, 155),
               (0, 0, 0), (0, 0, 0), 10, 29, spawnables.get_cooldown_reduction, spawnables.increase_cooldown_reduction)
        Button((1085, 90 * 5 + 108 * 4 + 10), (740, 98), "Evolve the Map ", 0, (155, 155, 155), (0, 0, 0),
               (0, 0, 0), 1000, 3, spawnables.get_level, spawnables.increase_level)


class Button:
    def __init__(self, position, size, base_text, base_value, color, frame_color, text_color, multiplier, limit, f, g):
        buttons.elements.append(self)
        self.font = pygame.font.SysFont("Monospace", 32)
        self.function_to_get_data = f
        self.upgrade_function = g
        self.x, self.y = position
        self.frame_position = Point(0, 0)
        self.frame_position.x = self.x - 5
        self.frame_position.y = self.y - 5
        self.width, self.height = size
        self.text = Text(base_text, text_color, self.get_price, self.x, self.y, self.width, self.height)
        self.base_value = base_value
        self.color, self.text_color = color, text_color
        self.multiplier = multiplier
        self.limit = limit
        current_level = self.function_to_get_data()
        self.price = current_level * self.multiplier + self.base_value
        self.frame_color = frame_color
        self.update()

    def update(self):
        current_level = self.function_to_get_data()
        if current_level == self.limit:
            self.text.is_full = True
            self.text.update()

    def on_click(self):
        current_level = self.function_to_get_data()
        if game.money >= self.price and current_level < self.limit:
            self.upgrade_function()
            game.money -= self.price
            if current_level == (self.limit - 1):
                self.text.is_full = True
            else:
                self.price = (current_level + 1) * self.multiplier + self.base_value
        self.text.update()

    def get_price(self):
        return self.price

    def draw(self):
        pygame.draw.rect(game.display, self.frame_color,
                         (self.frame_position.x, self.frame_position.y, self.width + 10, self.height + 10))
        pygame.draw.rect(game.display, self.color, (self.x, self.y, self.width, self.height))
        self.text.draw()


class DataManager:
    def __init__(self):
        self.data = {}

    def update_data(self):
        self.data["floors.level"] = floors.level
        self.data["spawnables.level"] = spawnables.level
        self.data["spawnables.cooldown_reduction"] = spawnables.cooldown_reduction
        self.data["workers.level"] = workers.level
        self.data["workers.amount"] = workers.amount
        self.data["game.money"] = game.money

    def update_variables(self):
        floors.level = self.data["floors.level"]
        spawnables.level = self.data["spawnables.level"]
        spawnables.cooldown_reduction = self.data["spawnables.cooldown_reduction"]
        workers.level = self.data["workers.level"]
        workers.amount = self.data["workers.amount"]
        game.money = self.data["game.money"]

    def write_data(self):
        data = json.dumps(self.data)
        file = None
        try:
            file = open("save.json", "x")
        except FileExistsError:
            file = open("save.json", "w")
        finally:
            if file is not None:
                file.write(data)
                file.close()

    def read_data(self):
        try:
            file = open("save.json", "r")
            self.data = json.loads(file.read())
            self.update_variables()
        except FileNotFoundError:
            self.update_data()
            self.write_data()


class Game:
    def __init__(self, window_size=(1920, 1080)):
        self.width, self.height = window_size
        self.display = pygame.display.set_mode(window_size)
        self.font = pygame.font.SysFont("Monospace", 32)
        self.background_color = (50, 50, 50)
        self.objects_to_draw = []
        self.operate = True
        self.money = 0

    def setup(self):
        data_manager.read_data()
        floors.create_all()
        floors.spawn_all()
        workers.create_all()
        buttons.create_all()
        texts.update_and_draw_all()
        Thread(target=self.draw_and_update).start()

    def draw_and_update(self):
        time_interval = 1 / 30
        sleep(0.25)
        while self.operate:
            self.display.fill(self.background_color)
            self.draw_and_update_all()
            sleep(time_interval)
            text_money = self.font.render(f"Money: {self.money}$", True, (255, 0, 0))
            self.display.blit(text_money, (game.width - 159 - (19 * len(str(self.money))), 0))
            pygame.display.flip()

    @staticmethod
    def draw_and_update_all():
        floors.draw_all()
        spawnables.draw_all()
        workers.draw_all()
        buttons.draw_all()
        data_manager.update_data()
        data_manager.write_data()

    def terminate(self):
        self.operate = False

    def terminate_all(self):
        floors.terminate_all()
        spawnables.terminate_all()
        workers.terminate_all()
        self.terminate()


game = Game()
texts = Texts()
buttons = Buttons()
spawnables = Spawnables()
floors = Floors()
workers = Workers()
data_manager = DataManager()
game.setup()
mouse = Point(0, 0)
previous_state = False

while ON:
    sleep(0.04)
    mouse.x, mouse.y = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed(num_buttons=3)[0]
    if clicked and previous_state is False:
        buttons.check(mouse)
    previous_state = clicked
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
