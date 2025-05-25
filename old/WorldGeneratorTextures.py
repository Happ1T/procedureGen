from ursina import *
from noise import pnoise2
from random import random

from world.BiomeGenerator import BiomeGenerator


class WorldGeneratorTextures(Entity):
    def __init__(self, map_size=200, seed=145278745):
        super().__init__()
        self.map_size = map_size
        self.seed = seed

        self.biome_gen = BiomeGenerator(map_size=self.map_size, seed=self.seed)

        self.biome_params = {
            'forest': {'scale': 80, 'octaves': 5, 'min_h': 0, 'max_h': 15, 'texture': 'forest_texture.png'},
            'field': {'scale': 70, 'octaves': 4, 'min_h': 0, 'max_h': 10, 'texture': 'field_texture.png'},
            'mountain': {'scale': 50, 'octaves': 6, 'min_h': 0, 'max_h': 200, 'texture': 'mountain_texture.png'},
            'lake': {'scale': 100, 'octaves': 1, 'min_h': 0, 'max_h': 0, 'texture': 'lake_texture.png'},
        }

        self.vertices = []
        self.triangles = []
        self.colors = []

        self.generate_terrain()
        self.create_mesh()

    def get_color_by_biome(self, biome, height):
        # Для примера, текстуры могут быть подгружены на основе биома
        return self.biome_params[biome]['texture']

    def generate_terrain(self):
        index = 0
        loadPerSent = 0
        for x in range(self.map_size):
            if loadPerSent < int(x / self.map_size * 100):
                loadPerSent = int(x / self.map_size * 100)
                print("Генерация:", loadPerSent, "%")
            for z in range(self.map_size):
                biome = self.biome_gen.get_biome(x, z)
                params = self.biome_params[biome]

                noise_val = pnoise2(x / params['scale'], z / params['scale'], octaves=params['octaves'])
                height = int(params['min_h'] + noise_val * (params['max_h'] - params['min_h']))
                if height < params['min_h']:
                    height = params['min_h'] - 1

                texture = self.get_color_by_biome(biome, height)

                # Генерация меша для блока
                for y in range(-10, height - 1):
                    pos = Vec3(x, y, z)

                    self.vertices += [
                        pos + Vec3(0, 0, 0), pos + Vec3(1, 0, 0),
                        pos + Vec3(1, 1, 0), pos + Vec3(0, 1, 0),
                        pos + Vec3(0, 0, 1), pos + Vec3(1, 0, 1),
                        pos + Vec3(1, 1, 1), pos + Vec3(0, 1, 1)
                    ]

                    v = index * 8
                    self.triangles += [
                        v, v+1, v+2, v, v+2, v+3,
                        v+1, v+5, v+6, v+1, v+6, v+2,
                        v+5, v+4, v+7, v+5, v+7, v+6,
                        v+4, v, v+3, v+4, v+3, v+7,
                        v+3, v+2, v+6, v+3, v+6, v+7,
                        v+4, v+5, v+1, v+4, v+1, v
                    ]

                    self.colors += [texture] * 8
                    index += 1

    def create_mesh(self):
        mesh = Mesh(
            vertices=self.vertices,
            triangles=self.triangles,
            #colors=self.colors,
            mode='triangle'
        )
        self.model = mesh
        self.texture = None  # Здесь можно добавить наложение текстуры

        # Создаем Entity для каждого биома с текстурой
        for biome in self.biome_params.values():
            texture = biome['texture']
            self.texture = load_texture(texture)  # Загружаем текстуру
            self.model.texture = self.texture  # Применяем текстуру
