from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


class Player(FirstPersonController):
    def __init__(self, on_exit_to_menu=None):
        super().__init__()
        self.gravity = 0
        self.cursor.visible = False
        self.speed = 50
        self.on_exit_to_menu = on_exit_to_menu

    def update(self):
        super().update()
        if held_keys['space']:
            self.y += time.dt * 50
        if held_keys['left shift']:
            self.y -= time.dt * 50
        if held_keys['escape'] and self.on_exit_to_menu:
            self.on_exit_to_menu()
