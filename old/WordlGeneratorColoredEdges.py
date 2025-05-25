from ursina import *
from noise import pnoise2
from random import random
from world.BiomeGenerator import BiomeGenerator


class WorldGeneratorColoredEdges(Entity):
    def __init__(self, map_size=100, seed=14882283374201337):
        super().__init__()
        self.block_map = set()
        self.map_size = map_size
        self.seed = seed

        self.biome_gen = BiomeGenerator(map_size=self.map_size, seed=self.seed)

        self.biome_params = {
            'forest': {'scale': 80, 'octaves': 5, 'min_h': 0, 'max_h': 15},
            'field': {'scale': 70, 'octaves': 3, 'min_h': 0, 'max_h': 10},
            'mountain': {'scale': 50, 'octaves': 6, 'min_h': 0, 'max_h': 200},
            'lake': {'scale': 100, 'octaves': 1, 'min_h': 0, 'max_h': 2},
        }

        self.vertices = []
        self.triangles = []
        self.colors = []  # Список цветов для каждой вершины
        self.uvs = []

        self.generate_terrain()
        self.create_mesh()

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

                for y in range(-10, height - 1):
                    pos = Vec3(x, y, z)

                    # Вершины для обычного блока
                    self.vertices += [
                        pos + Vec3(0, 0, 0), pos + Vec3(1, 0, 0),
                        pos + Vec3(1, 1, 0), pos + Vec3(0, 1, 0),
                        pos + Vec3(0, 0, 1), pos + Vec3(1, 0, 1),
                        pos + Vec3(1, 1, 1), pos + Vec3(0, 1, 1)
                    ]

                    v = index * 8
                    # Треугольники для обычного блока
                    self.triangles += [
                        v, v+1, v+2, v, v+2, v+3,  # front
                        v+1, v+5, v+6, v+1, v+6, v+2,  # right
                        v+5, v+4, v+7, v+5, v+7, v+6,  # back
                        v+4, v, v+3, v+4, v+3, v+7,  # left
                        v+3, v+2, v+6, v+3, v+6, v+7,  # top
                        v+4, v+5, v+1, v+4, v+1, v  # bottom
                    ]

                    # Цвет для обычных вершин блока
                    block_color = color.white
                    self.colors += [block_color] * 8  # Белый цвет для центра

                    # Добавляем обводку (черный цвет для граней)
                    self.add_edge_outline(v)

                    index += 1

    def add_edge_outline(self, v):
        # Цвет для обводки
        outline_color = color.black

        # Список треугольников для добавления черной обводки
        # Эти индексы указывают на грани блока, которые мы хотим выделить черной обводкой
        outline_triangles = [
            v, v+1, v+2, v, v+2, v+3,  # front edge
            v+1, v+5, v+6, v+1, v+6, v+2,  # right edge
            v+5, v+4, v+7, v+5, v+7, v+6,  # back edge
            v+4, v, v+3, v+4, v+3, v+7,  # left edge
            v+3, v+2, v+6, v+3, v+6, v+7,  # top edge
            v+4, v+5, v+1, v+4, v+1, v  # bottom edge
        ]

        # Добавляем обводку черным цветом
        self.triangles += outline_triangles
        self.colors += [outline_color] * len(outline_triangles)  # Все грани в черный

    def create_mesh(self):
        mesh = Mesh(
            vertices=self.vertices,
            triangles=self.triangles,
            colors=self.colors,  # Цвета для каждой вершины
            mode='triangle'
        )
        self.model = mesh
