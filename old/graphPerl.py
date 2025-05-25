from perlin_noise import PerlinNoise
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Параметры генерации
terrain_width = 500
period = 200
amp = 6
octaves = 4
noise = PerlinNoise(octaves=octaves, seed=42132)

# Генерация высот
landscale = np.zeros((terrain_width, terrain_width))
for x in range(terrain_width):
    for z in range(terrain_width):
        y = noise([x/period, z/period]) * amp
        landscale[x][z] = y

# Визуализация в 3D
X = np.arange(terrain_width)
Z = np.arange(terrain_width)
X, Z = np.meshgrid(X, Z)
Y = landscale[X, Z]

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Z, Y, cmap='terrain')

ax.set_title("3D визуализация сгенерированной карты")
ax.set_xlabel("X")
ax.set_ylabel("Z")
ax.set_zlabel("Высота")
plt.show()
