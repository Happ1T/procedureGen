from ursina import *                         # Импортируем всё из библиотеки Ursina
from perlin_noise import PerlinNoise        # Импортируем генератор Перлин шума
import math                                  # Математические функции, например sqrt

# Класс генерации мира, наследуется от Entity, чтобы сразу стать объектом сцены
class WorldGenerator(Entity):
    def __init__(self, map_size=80, perlin_scale=35, max_height=12, seed=23125):
        super().__init__()                   # Инициализируем родительский класс Entity
        self.map_size = map_size             # Размер карты (ширина и глубина)
        self.perlin_scale = perlin_scale     # Масштаб шума (чем больше — тем плавнее)
        #self.max_height = max_height         # Максимальная высота блоков
        self.seed = seed                     # Сид для воспроизводимого шума
        self.noise = PerlinNoise(octaves=4, seed=self.seed)  # Инициализируем шум Перлина
        self.center = self.map_size // 2     # Центр карты, используется для маски расстояния

        # Цвета блоков в зависимости от высоты
        self.block_colors = {
            'water': color.rgb(30, 120, 250),      # Низкие области — вода
            'shore': color.rgb(80, 200, 80),       # Берег
            'hills': color.rgb(100, 160, 60),      # Холмы
            'mountains': color.rgb(120, 120, 120)  # Горы
        }

        # Списки для меша
        self.vertices = []                 # Вершины (точки в пространстве)
        self.triangles = []               # Треугольники (составляют полигоны)
        self.colors = []                  # Цвета вершин

        self.generate_terrain()          # Генерируем данные для меша
        self.create_mesh()               # Создаём меш из сгенерированных данных

    def distance_mask(self, x, z):
        """Уменьшает высоту по мере удаления от центра карты"""
        dist = math.sqrt((x - self.center) ** 2 + (z - self.center) ** 2)  # Расстояние от центра
        max_dist = math.sqrt(2 * (self.center ** 2))                      # Максимальное возможное расстояние
        return 1 - (dist / max_dist)                                      # Маска от 1 в центре до 0 по краям

    def get_color(self, height):
        """Возвращает цвет в зависимости от высоты"""
        if height < 2:
            return self.block_colors['water']       # Низко — вода
        elif height < 3:
            return self.block_colors['shore']       # Немного выше — берег
        elif height < 6:
            return self.block_colors['hills']       # Средняя высота — холмы
        else:
            return self.block_colors['mountains']   # Высоко — горы

    def generate_terrain(self):
        """Генерация вершин, цветов и треугольников"""
        index = 0                                    # Индекс блока
        for x in range(self.map_size):               # Перебираем координаты X
            for z in range(self.map_size):           # Перебираем координаты Z
                # Вычисляем шумовую высоту + маску расстояния
                noise_val = self.noise([x / self.perlin_scale, z / self.perlin_scale])
                masked_val = (noise_val + 1) / 2 * self.distance_mask(x, z)
                height = int(masked_val * self.max_height)         # Итоговая высота
                color_val = self.get_color(height)                 # Цвет блока по высоте

                for y in range(height):                            # Добавляем блоки по высоте
                    pos = Vec3(x, y, z)                            # Позиция блока

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
