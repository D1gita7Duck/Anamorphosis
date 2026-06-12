import os
import matplotlib.pyplot as plt
import trimesh
import numpy as np


R = 50
og_file = "cube.stl"
ana_file = os.path.join("output", "ana_" + og_file)

og_mesh = trimesh.load_mesh(os.path.join("model_examples", og_file))
og_vertices = og_mesh.vertices
ana_mesh = trimesh.load_mesh(ana_file)
ana_vertices = ana_mesh.vertices

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# Circle
theta = np.linspace(0, 2*np.pi, 100)
x_c = R*np.cos(theta)
y_c = R*np.sin(theta)
z_c = np.zeros_like(theta)

ax.plot(x_c, y_c, z_c)

ax.scatter([i[0] for i in og_vertices], [i[1] for i in og_vertices], [i[2] for i in og_vertices])
ax.scatter(og_mesh.centroid[0], og_mesh.centroid[1], og_mesh.centroid[2], color = 'black', depthshade=False)
ax.scatter([i[0] for i in ana_vertices], [i[1] for i in ana_vertices], [i[2] for i in ana_vertices])

# viewpoint
# ax.scatter(O[0], O[1], O[2], color='black')

ax.set_aspect('equal')
ax.view_init(90, -90, 0) # see XY plane
plt.show()
