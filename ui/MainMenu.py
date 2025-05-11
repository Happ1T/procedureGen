# main_menu.py
from ursina import *
from random import randint
from player.camera_controller import Player
from world.WordlGeneratorObjects import WorldGeneratorObjects

class MainMenu(Entity):

    def __init__(self):
        super().__init__()
        mouse.locked = False
        mouse.visible = True

        self.ui_elements = []

        self.bg = Entity(parent=camera.ui, model='quad', scale=(1.8, 1), color=color.rgba(0, 0, 0, 150), z=1)
        self.ui_elements.append(self.bg)
        self.text_size = Text("Размер мира", parent=camera.ui, x=0.45, y=0.25, origin=(0, 0), scale=1.5)
        self.world_size_input = InputField(default_value='200', limit_content_to='1234567890')
        self.world_size_input.scale = (0.5, 0.05)
        self.world_size_input.x = 0.45
        self.world_size_input.y = 0.2
        self.ui_elements.append(self.world_size_input)

        self.text_sid = Text("Сид мира", parent=camera.ui, x=-0.45, y=0.25, origin=(0, 0), scale=1.5)
        self.seed_input = InputField(default_value= '', limit_content_to='1234567890')
        self.seed_input.scale = (0.5, 0.05)
        self.seed_input.x = -0.45
        self.seed_input.y = 0.2
        self.ui_elements.append(self.seed_input)

        self.random_button = Button(text='Случайный мир', scale=(0.3, 0.1), y=0, on_click=self.generate_random)
        self.seed_button = Button(text='Мир по сиду', scale=(0.3, 0.1), y=-0.15, on_click=self.generate_from_seed)
        self.exit_button = Button(text='Выход', scale=(0.3, 0.1), y=-0.3, on_click=application.quit)
        self.ui_elements += [self.random_button, self.seed_button, self.exit_button]

    def generate_random(self):
        size = int(self.world_size_input.text)
        seed = randint(0, 99999999)
        self.destroyUI()
        self.start_world(size, seed)

    def generate_from_seed(self):
        size = int(self.world_size_input.text)
        if self.seed_input.text:
            seed = int(self.seed_input.text)
            self.destroyUI()
            self.start_world(size, seed)
        else:
            self.generate_random()

    def start_world(self, size, seed):
        self.gen = WorldGeneratorObjects(map_size=size, seed=seed)
        self.player = Player(on_exit_to_menu=self.return_to_menu)

    def destroyUI(self):
        for e in self.ui_elements:
            destroy(e)
        destroy(self.text_size)
        destroy(self.text_sid)
        destroy(self)


    def return_to_menu(self):
        self.gen.cleanup()
        destroy(self.gen)
        destroy(self.player)
        mouse.locked = False
        mouse.visible = True
        MainMenu()
