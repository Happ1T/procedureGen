from noise import pnoise2
from ursina import *                         # Импортируем всё из библиотеки Ursina
from perlin_noise import PerlinNoise        # Импортируем генератор Перлин шума
import math                                  # Математические функции, например sqrt

from world.BiomeGenerator import BiomeGenerator


# Класс генерации мира, наследуется от Entity, чтобы сразу стать объектом сцены
class WorldGeneratorBioms(Entity):
    def __init__(self, map_size=500, seed=14882283374201337):
        super().__init__()                   # Инициализируем родительский класс Entity
        self.block_map = set()  # В __init__, хранит все занятые позиции
        self.map_size = map_size             # Размер карты (ширина и глубина)
        self.seed = seed                     # Сид для воспроизводимого шума

        self.biome_gen = BiomeGenerator(map_size=self.map_size, seed=self.seed)

        self.biome_params = {
            'forest': {'scale': 80, 'octaves': 5, 'min_h': 0, 'max_h': 15},
            'field': {'scale': 70, 'octaves': 3, 'min_h': 0, 'max_h': 10},
            'mountain': {'scale': 50, 'octaves': 6, 'min_h': 0, 'max_h': 200},
            'lake': {'scale': 100, 'octaves': 1, 'min_h': 0, 'max_h': 2},
        }


        # Списки для меша
        self.vertices = []                 # Вершины (точки в пространстве)
        self.triangles = []               # Треугольники (составляют полигоны)
        self.colors = []                  # Цвета вершин

        self.generate_terrain()          # Генерируем данные для меша
        self.create_mesh()               # Создаём меш из сгенерированных данных


    def get_color_by_biome(self, biome, height):
        if biome == 'forest':
            return color.green
        elif biome == 'mountain':
            return color.gray
        elif biome == 'lake':
            return color.azure
        elif biome == 'field':
            return color.lime
        return None
    def generate_terrain(self):
        """Генерация вершин, цветов и треугольников"""

        index = 0  # Индекс блока
        loadPerSent = 0
        for x in range(self.map_size):    # Перебираем координаты X
            if loadPerSent < int(x/self.map_size*100):
                loadPerSent = int(x/self.map_size*100)
                print("Генерация:", loadPerSent, "%")
            for z in range(self.map_size):           # Перебираем координаты Z
                biome = self.biome_gen.get_biome(x, z)
                params = self.biome_params[biome]
                # Генерация высоты
                noise_val = pnoise2(x / params['scale'], z / params['scale'], octaves=params['octaves'])


                height = int(params['min_h'] + noise_val * (params['max_h'] - params['min_h']))
                if height < params['min_h']:
                    height =  params['min_h']-1
                color_val = self.get_color_by_biome(biome, height)




                for y in range(-10, height-1):  # Только самый верхний блок
                    pos = Vec3(x, y, z)                         # Позиция блока

                    # Добавляем 8 вершин куба
                    self.vertices += [
                        pos + Vec3(0, 0, 0), pos + Vec3(1, 0, 0),
                        pos + Vec3(1, 1, 0), pos + Vec3(0, 1, 0),
                        pos + Vec3(0, 0, 1), pos + Vec3(1, 0, 1),
                        pos + Vec3(1, 1, 1), pos + Vec3(0, 1, 1)
                    ]

                    v = index * 8      # Смещение индексов для текущего блока

                    # Добавляем 12 треугольников (2 на каждую из 6 граней куба)
                    self.triangles += [
                        v, v+1, v+2, v, v+2, v+3,     # передняя грань
                        v+1, v+5, v+6, v+1, v+6, v+2, # правая грань
                        v+5, v+4, v+7, v+5, v+7, v+6, # задняя грань
                        v+4, v, v+3, v+4, v+3, v+7,   # левая грань
                        v+3, v+2, v+6, v+3, v+6, v+7, # верхняя грань
                        v+4, v+5, v+1, v+4, v+1, v    # нижняя грань
                    ]

                    self.colors += [color_val] * 8   # Один цвет на все 8 вершин куба
                    index += 1                       # Увеличиваем индекс блока



    def create_mesh(self):
        """Создание единого меша и присвоение его объекту"""
        mesh = Mesh(
            vertices=self.vertices,      # Передаём вершины
            triangles=self.triangles,    # Передаём треугольники
            colors=self.colors,          # Цвета вершин
            mode='triangle'              # Режим отрисовки — треугольники
        )
        self.model = mesh                # Присваиваем меш объекту
        self.texture = None              # Текстура не используется, только цвет вершин
