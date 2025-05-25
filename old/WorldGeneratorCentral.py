from noise import pnoise2
from ursina import *
from perlin_noise import PerlinNoise
import math
from random import random

from world.BiomeGenerator import BiomeGenerator


class WorldGeneratorCentral(Entity):
    def __init__(self, map_size=200, seed=145278745):
        super().__init__()
        self.block_map = set()
        self.map_size = map_size
        self.seed = seed

        self.biome_gen = BiomeGenerator(map_size=self.map_size, seed=self.seed)

        self.biome_params = {
            'forest': {'scale': 80, 'octaves': 5, 'min_h': 0, 'max_h': 15},
            'field': {'scale': 70, 'octaves': 4, 'min_h': 0, 'max_h': 10},
            'mountain': {'scale': 50, 'octaves': 6, 'min_h': 0, 'max_h': 200},
            'lake': {'scale': 100, 'octaves': 1, 'min_h': 0, 'max_h': 0},
        }

        self.vertices = []
        self.triangles = []
        self.colors = []

        self.generate_terrain()
        self.create_mesh()

    def get_color_by_biome(self, biome, height):
        params = self.biome_params[biome]
        if biome == 'forest':
            return hsv(120, 0.5, 0.2 + (height / params['max_h']))
        elif biome == 'mountain':
            return hsv(0, 0, 0.2 + (height / params['max_h']))
        elif biome == 'lake':
            return hsv(180, 0.5, 0.5)
        elif biome == 'field':
            return hsv(127, 1, 0.5 + (height / params['max_h']))
        return hsv(0, 0, 0)

    def generate_terrain(self):
        index = 0
        loadPerSent = 0
        biome_types = list(self.biome_params.keys())

        for x in range(self.map_size):
            if loadPerSent < int(x / self.map_size * 100):
                loadPerSent = int(x / self.map_size * 100)
                print("Генерация:", loadPerSent, "%")
            for z in range(self.map_size):
                i1, i2, d1, d2 = self.biome_gen.get_biome_blend_info(x, z)
                b1 = biome_types[i1 % len(biome_types)]
                b2 = biome_types[i2 % len(biome_types)]

                w1 = 1 / (d1 + 0.001)
                w2 = 1 / (d2 + 0.001)
                total = w1 + w2
                w1 /= total
                w2 /= total

                p1 = self.biome_params[b1]
                p2 = self.biome_params[b2]

                n1 = pnoise2(x / p1['scale'], z / p1['scale'], octaves=p1['octaves'])
                n2 = pnoise2(x / p2['scale'], z / p2['scale'], octaves=p2['octaves'])

                h1 = p1['min_h'] + n1 * (p1['max_h'] - p1['min_h'])
                h2 = p2['min_h'] + n2 * (p2['max_h'] - p2['min_h'])

                c1 = self.biome_gen.biome_centers[i1]
                c2 = self.biome_gen.biome_centers[i2]
                dist1 = math.sqrt((x - c1.x)**2 + (z - c1.y)**2)
                dist2 = math.sqrt((x - c2.x)**2 + (z - c2.y)**2)
                max_dist = self.map_size / self.biome_gen.num_biomes

                norm1 = max(0.0, 1 - dist1 / max_dist)
                norm2 = max(0.0, 1 - dist2 / max_dist)

                if b1 == 'mountain':
                    peak_factor1 = max(0.0, 1 - (dist1 / (max_dist * 0.5)))
                    h1 *= 1 + peak_factor1 * 3.0  # пиковое усиление в центре
                else:
                    h1 *= norm1

                if b2 == 'mountain':
                    peak_factor2 = max(0.0, 1 - (dist2 / (max_dist * 0.5)))
                    h2 *= 1 + peak_factor2 * 3.0
                else:
                    h2 *= norm2

                height = int(h1 * w1 + h2 * w2)
                if height < min(p1['min_h'], p2['min_h']):
                    height = min(p1['min_h'], p2['min_h']) - 1

                color_val = self.get_color_by_biome(b1 if w1 > w2 else b2, height)

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

                    if y >= height - 2:
                        surface_pos = Vec3(x + 0.5, height - 1, z + 0.5)
                        if b1 == 'forest' and random() < 0.02:
                            tree = Entity(model='cube', color=color.brown, scale=(1, 3, 1), position=surface_pos + Vec3(0, 1.5, 0))
                            crown = Entity(model='sphere', color=color.green, scale=4, position=surface_pos + Vec3(0, 3.5, 0))
                        elif b1 == 'field' and random() < 0.03:
                            flower = Entity(model='cube', color=color.blue, scale=0.5, position=surface_pos)
                        elif b1 == 'field' and random() < 0.04:
                            flower = Entity(model='cube', color=color.red, scale=0.5, position=surface_pos)
                        elif b1 == 'field' and random() < 0.05:
                            flower = Entity(model='cube', color=color.yellow, scale=0.5, position=surface_pos)

    def create_mesh(self):
        mesh = Mesh(
            vertices=self.vertices,
            triangles=self.triangles,
            colors=self.colors,
            mode='triangle'
        )
        self.model = mesh
        self.texture = None
