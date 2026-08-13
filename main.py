from mirror_types import cylinder, sphere
from sys import exit
import matplotlib.pyplot as plt
import numpy as np

"""
Available types
"""
avail_types = ("cylinder", "sphere")

"""
INPUT ARGUMENTS
Units: mm
"""
input_file : str = "model_examples//cube.stl"
mirror_type : str = "cylinder"
no_subdivisions : int = 0
R = 25
viewpoint = [300., 0., 0.]
to_plot = False

if mirror_type == "cylinder":
    output_object = cylinder.CylindricalMirror(file_path=input_file, viewpoint=viewpoint, radius=R, no_subdivisions=no_subdivisions, preview_mesh=True)
elif mirror_type == "sphere":
    output_object = sphere.SphericalMirror(file_path=input_file, viewpoint=viewpoint, radius=R, no_subdivisions=no_subdivisions, preview_mesh=True)
else:
    raise ValueError(f"Incorrect mirror type. Choose from {avail_types}")

if not to_plot:
    exit("Not plotting")
f_mesh = output_object.f_mesh
f_mesh_vertices = f_mesh.vertices
reflected_points = output_object.new_mesh.vertices
bounding_radius = f_mesh.bounding_cylinder.primitive.radius
bounding_circle_centre = f_mesh.bounding_cylinder.primitive.transform[:2, 3]

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# Circle
theta = np.linspace(0, 2*np.pi, 100)
x_c = output_object.R*np.cos(theta)
y_c = output_object.R*np.sin(theta)
z_c = np.zeros_like(theta)

x_b = bounding_circle_centre[0] + bounding_radius*np.cos(theta)
y_b = bounding_circle_centre[1] + bounding_radius*np.sin(theta)
z_b = np.zeros_like(theta)

ax.plot(x_c, y_c, z_c)
ax.plot(x_b, y_b, z_b)

ax.scatter([i[0] for i in f_mesh_vertices], [i[1] for i in f_mesh_vertices], [i[2] for i in f_mesh_vertices])
ax.scatter([i[0] for i in reflected_points], [i[1] for i in reflected_points], [i[2] for i in reflected_points])

# viewpoint
ax.scatter(output_object.V[0], output_object.V[1], output_object.V[2], color='black')

ax.set_aspect('equal')
if mirror_type == "cylinder":
    ax.view_init(90, -90, 0) # see XY plane
elif mirror_type == "sphere":
    ax.view_init(0, 0, 0)
plt.show()