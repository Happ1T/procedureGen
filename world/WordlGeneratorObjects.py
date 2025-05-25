from noise import pnoise2
from ursina import *
from perlin_noise import PerlinNoise
import math
from random import random

from world.BiomeGenerator import BiomeGenerator


class WorldGeneratorObjects(Entity):
    def __init__(self, map_size=200, seed=23131):
        super().__init__()

        self.seed_text = Text(
            text=f'Сид: {seed}',
            position=(-0.7, 0.45),
            origin=(0, 0),
            scale=1.5,
            color=color.azure,
            background=True
        )
        self.generated_entities = []
        self.block_map = set()
        self.map_size = map_size
        self.seed = seed

        self.biome_gen = BiomeGenerator(map_size=self.map_size, seed=self.seed)

        self.biome_params = {
            'forest': {'scale': 80, 'octaves': 5, 'min_h': 1, 'max_h': 15},
            'field': {'scale': 70, 'octaves': 4, 'min_h': 1, 'max_h': 10},
            'mountain': {'scale': 50, 'octaves': 6, 'min_h': 0, 'max_h': 150},
            'lake': {'scale': 100, 'octaves': 1, 'min_h': 0, 'max_h': 0},
        }

        self.vertices = []
        self.triangles = []
        self.colors = []

        self.generate_terrain()
        self.create_mesh()

    def get_color_by_biome(self, biome, height, x=None, z=None):
        # Определяем цвет в зависимости от высоты в биоме
        params = self.biome_params[biome]
        if biome == 'forest':
            v = 0.3+(height/params['max_h'])
            s = 1
            if v > 1:
                s -= 1-v
            return hsv(105, s, v)
        elif biome == 'mountain':
            # Горы: серый цвет с регулировкой яркости
            return hsv(0, 0, 0.2+(height/params['max_h']))
        elif biome == 'lake':
            if x is not None and z is not None:
                # Рассчитаем расстояние до ближайшего озера
                lake_centers = [center for i, center in enumerate(self.biome_gen.biome_centers)]

                # Если есть центры озер
                if lake_centers:
                    dists = [math.sqrt((x - center.x) ** 2 + (z - center.y) ** 2) for center in lake_centers]
                    min_dist = min(dists)  # Минимальное расстояние до центра озера
                    max_dist = self.map_size / self.biome_gen.num_biomes

                    v = 0.9 - ( (self.map_size/self.biome_gen.num_biomes)/min_dist)

                    return hsv(180, 1, max(v,0.4) )  # Темнеем к центру озера
            return hsv(180, 1, 0.5)  # Стандартный цвет для озера
        elif biome == 'field':
            # Поле: ярко-зеленый цвет с регулировкой яркости
            v = 0.3 + (height / params['max_h'])
            s = 1
            if v > 1:
                s -= 1 - v
            return hsv(127, s, v)
        return hsv(0, 0, 0)  # Черный по умолчанию



    def generate_terrain(self):
        index = 0
        loadPerSent = 0
        count_of_boat = 0
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
                color_val = self.get_color_by_biome(biome, height,x,z)

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

                    self.colors += [color_val] * 8
                    index += 1

                # Объекты на поверхности
                    if y >= height - 2:
                        surface_pos = Vec3(x + 0.5, height - 1, z + 0.5)
                        if biome == 'forest' and random() < 0.02:
                            tree = Entity(model='cube', color=color.brown, scale=(1, 3, 1), position=surface_pos + Vec3(0, 1.5, 0))
                            crown = Entity(model='sphere', color=color.rgb(0,153,0), scale=4, position=surface_pos + Vec3(0, 3.5, 0))
                            self.generated_entities.append(tree)
                            self.generated_entities.append(crown)
                        elif biome == 'field' and random() < 0.01:
                            flower = Entity(model='cube', color=color.blue, scale=0.5, position=surface_pos)
                            self.generated_entities.append(flower)
                        elif biome == 'field' and random() < 0.02:
                            flower = Entity(model='cube', color=color.red, scale=0.5, position=surface_pos)
                            self.generated_entities.append(flower)
                        elif biome == 'field' and random() < 0.03:
                            flower = Entity(model='cube', color=color.yellow, scale=0.5, position=surface_pos)
                            self.generated_entities.append(flower)
                        if biome == 'lake' and random() < 0.01 and count_of_boat == 0:
                            lake_centers = [center for i, center in enumerate(self.biome_gen.biome_centers)]
                            if lake_centers:
                                dists = [math.sqrt((x - center.x) ** 2 + (z - center.y) ** 2) for center in
                                         lake_centers]
                                min_dist = min(dists)  # Минимальное расстояние до центра озера
                            if min_dist < 10:
                                count_of_boat = 1
                                ship = Entity(
                                    model='models/source/ship.fbx',
                                    texture = 'models/source/ship.fbm/dutch_ship_medium_rigging_diff_4k',
                                    double_sided = True,
                                    scale=0.01,
                                    position=surface_pos + Vec3(0, 0, 0),
                                    rotation_y=random() * 360
                                )
                                self.generated_entities.append(ship)

    def cleanup(self):
        for e in self.generated_entities:
            destroy(e)
        destroy(self.seed_text)
    def create_mesh(self):
        mesh = Mesh(
            vertices=self.vertices,
            triangles=self.triangles,
            colors=self.colors,
            mode='triangle'
        )
        self.model = mesh
        self.texture = None
