from ursina import *
from PIL import Image
import numpy as np


class Minimap(Entity):
    def __init__(self, chunk_manager, player):
        super().__init__()
        self.chunk_manager = chunk_manager
        self.player = player

        # Создаем текстуру для миникарты
        self.map_size = 256  # Размер текстуры миникарты
        self.texture = Texture(Image.new('RGB', (self.map_size, self.map_size)))

        # Основной элемент миникарты
        self.minimap = Entity(
            parent=camera.ui,
            model='quad',
            texture=self.texture,
            scale=(0.3, 0.3),
            position=(0.7, 0.4),
            #color=color.white
        )

        # Рамка миникарты
        self.border = Entity(
            parent=self.minimap,
            model=Quad(radius=0.02),
            scale=(1.05, 1.05),
            color=color.black,
            z=0.1
        )

        # Маркер игрока
        self.player_marker = Entity(
            parent=self.minimap,
            model='circle',
            color=color.red,
            scale=(0.05, 0.05),
            z=0.2
        )

        # Сразу генерируем карту
        self.generate_texture()

    def generate_texture(self):
        """Генерирует текстуру карты"""
        world_size = self.chunk_manager.MAP_SIZE
        img_array = np.zeros((self.map_size, self.map_size, 3), dtype=np.uint8)

        # Заливаем фон (вода)
        img_array[:, :] = (30, 120, 250)  # Синий цвет воды

        # Рисуем землю из чанков
        for (cx, cz), chunk in self.chunk_manager.loaded_chunks.items():
            for block in chunk:
                x, z = int(block.x), int(block.z)
                if 0 <= x < world_size and 0 <= z < world_size:
                    px = int(x * self.map_size / world_size)
                    pz = int(z * self.map_size / world_size)

                    # Определяем цвет блока
                    if block.color == color.rgb(80, 200, 80):  # Берег
                        img_array[px, pz] = (80, 200, 80)
                    elif block.color == color.rgb(100, 160, 60):  # Холмы
                        img_array[px, pz] = (100, 160, 60)
                    elif block.color == color.rgb(120, 120, 120):  # Скалы
                        img_array[px, pz] = (120, 120, 120)

        # Конвертируем numpy array в PIL Image
        img = Image.fromarray(img_array, 'RGB')
        self.texture = Texture(img)
        self.minimap.texture = self.texture

    def update(self):
        """Обновляет позицию маркера игрока"""
        if not hasattr(self.player, 'position'):
            return

        # Нормализуем координаты игрока
        norm_x = (self.player.x / self.chunk_manager.MAP_SIZE) * 2 - 1
        norm_z = (self.player.z / self.chunk_manager.MAP_SIZE) * 2 - 1

        # Учитываем масштаб миникарты
        self.player_marker.x = norm_x * 0.9
        self.player_marker.y = norm_z * 0.9