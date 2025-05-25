from numpy import floor
from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt

# генерация основного шума и параметризация
noise = PerlinNoise(octaves=4, seed=42132)
amp = 6
period = 200
terrain_width = 500

#генерация матрицы для представления ландшафта
landscale = [[0 for i in range(terrain_width)] for i in range(terrain_width)]

for position in range(terrain_width**2):
   # вычисление высоты y в координатах (x, z)
   x = floor(position / terrain_width)
   z = floor(position % terrain_width)
   y = floor(noise([x/period, z/period])*amp)
   landscale[int(x)][int(z)] = int(y)

plt.imshow(landscale)
plt.show()