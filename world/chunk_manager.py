from ursina import *
from perlin_noise import PerlinNoise
import math
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from collections import deque


class ChunkManager:
    def __init__(self, map_size=80, chunk_size=16, perlin_scale=35, max_height=12, render_distance=3, seed=23125):
        self.MAP_SIZE = map_size
        self.CHUNK_SIZE = chunk_size
        self.PERLIN_SCALE = perlin_scale
        self.MAX_HEIGHT = max_height
        self.RENDER_DISTANCE = render_distance
        self.noise = PerlinNoise(octaves=5, seed=seed)
        self.loaded_chunks = {}
        self.chunk_queue = deque()
        self.CENTER_X = self.MAP_SIZE // 2
        self.CENTER_Z = self.MAP_SIZE // 2

        # Предварительно вычисленные данные
        self.height_cache = np.zeros((map_size, map_size))
        self._precompute_heights()

        # Оптимизация памяти
        self.block_colors = {
            'water': color.rgb(30, 120, 250),
            'shore': color.rgb(80, 200, 80),
            'hills': color.rgb(100, 160, 60),
            'mountains': color.rgb(120, 120, 120)
        }

    def _precompute_heights(self):
        """Предварительный расчет высот для всей карты"""
        for x in range(self.MAP_SIZE):
            for z in range(self.MAP_SIZE):
                noise_val = self.noise([x / self.PERLIN_SCALE, z / self.PERLIN_SCALE])
                mask_val = 1 - (math.sqrt((x - self.CENTER_X) ** 2 + (z - self.CENTER_Z) ** 2) /
                                math.sqrt((self.MAP_SIZE / 2) ** 2 + (self.MAP_SIZE / 2) ** 2))
                self.height_cache[x, z] = int((noise_val + 1) / 2 * mask_val * self.MAX_HEIGHT)

    def distance_mask(self, x, z):
        """Быстрая маска расстояния с использованием предварительных вычислений"""
        return 1 - (math.sqrt((x - self.CENTER_X) ** 2 + (z - self.CENTER_Z) ** 2) /
                    math.sqrt((self.MAP_SIZE / 2) ** 2 + (self.MAP_SIZE / 2) ** 2))

    def generate_chunk(self, cx, cz):
        if (cx, cz) in self.loaded_chunks:
            return

        chunk_entities = []
        world_x_start = cx * self.CHUNK_SIZE
        world_z_start = cz * self.CHUNK_SIZE

        def generate_blocks(x_start, z_start, x_end, z_end):
            """Генерация части чанка"""
            local_entities = []
            for x in range(x_start, x_end):
                for z in range(z_start, z_end):
                    world_x = world_x_start + x
                    world_z = world_z_start + z

                    if world_x >= self.MAP_SIZE or world_z >= self.MAP_SIZE:
                        continue

                    height = int(self.height_cache[world_x, world_z])

                    if height < 2:
                        block_color = self.block_colors['water']
                    elif height < 3:
                        block_color = self.block_colors['shore']
                    elif height < 6:
                        block_color = self.block_colors['hills']
                    else:
                        block_color = self.block_colors['mountains']

                    for y in range(height):
                        local_entities.append(Entity(
                            model='cube',
                            color=block_color,
                            position=(world_x, y, world_z),
                            scale=1,
                            collider='box'
                        ))
            return local_entities

        # Разделяем чанк на 4 части для параллельной генерации
        half_size = self.CHUNK_SIZE // 2
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(generate_blocks, 0, 0, half_size, half_size),
                executor.submit(generate_blocks, half_size, 0, self.CHUNK_SIZE, half_size),
                executor.submit(generate_blocks, 0, half_size, half_size, self.CHUNK_SIZE),
                executor.submit(generate_blocks, half_size, half_size, self.CHUNK_SIZE, self.CHUNK_SIZE)
            ]

            for future in futures:
                chunk_entities.extend(future.result())

        self.loaded_chunks[(cx, cz)] = chunk_entities

    def destroy_chunk(self, cx, cz):
        if (cx, cz) not in self.loaded_chunks:
            return

        for e in self.loaded_chunks[(cx, cz)]:
            e.disable()
            del e
        del self.loaded_chunks[(cx, cz)]