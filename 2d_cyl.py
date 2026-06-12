import numpy as np
import matplotlib.pyplot as plt
# plt.switch_backend("Qt5Agg")
from math import sqrt
from numpy.typing import NDArray
import trimesh
from sys import exit
import os
"""
UNITS ARE IN mm (millimeter)
"""

def dist(P1, P2):
    return np.linalg.norm(np.array(P2) - np.array(P1))

# Ray-circle intersection
def ray_cylinder_intersection(V : NDArray, d : NDArray, R : float):
    """
    Computes ray and cylinder intersection.
    Inputs:
        V : viewpoint coordinates
        d : unit vector from V to A (incident ray) A being the virtual image point
        R : radius of cylinder centered at origin
    Outputs:
        None if there is no possible intersection
        NDArray containing the point of intersection
    """
    # have to neglect z component as the cylinder is infinite
    # if we include z it becomes ray and sphere intersection
    Vx, Vy, Vz = V
    dx, dy, dz = d

    a = dx**2 + dy**2
    b = 2 * (Vx*dx + Vy*dy)
    c = Vx**2 + Vy**2 - R**2

    D = b**2 - 4*a*c
    if D < 0:
        return None

    t1 = (-b - sqrt(D)) / (2*a)
    t2 = (-b + sqrt(D)) / (2*a)

    t_vals = [t for t in [t1, t2] if t > 0]
    if not t_vals:
        return None

    t = min(t_vals)
    return V + t * d

# Reflection using vector formula
def reflect(d : NDArray, n : NDArray) -> NDArray:
    """
    Returns reflected unit vector given incident and normal unit vectors
    """
    return d - 2 * np.dot(d, n) * n

def mesh_within_circle(vertices, r : float) -> bool:
    r2 = r*r
    for x,y,z in vertices:
        if x*x + y*y > r2:
            return False
    return True

def move_mesh_inside_circle(mesh : trimesh.Trimesh, R : float):
    """
    The function moves the mesh such that the point farthest from the origin is made to
    lie on a circle centered at origin with radius R\n
    Inputs:
        mesh : trimesh instance
        R : radius of circle centered at origin
    Returns:
        ValueError if the mesh bounding radius is bigger than R
        None if no problemo
    """
    bounding_radius = mesh.bounding_cylinder.primitive.radius
    c_x, c_y = mesh.bounding_cylinder.primitive.transform[:2, 3]
    print(f"Bounding cylinder radius {bounding_radius}")
    print(f"Bounding cylinder centre {c_x}, {c_y}")
    print(f"Old bounds {mesh.bounds}")
    
    if bounding_radius > R:
        return ValueError("*** The mesh is too big for the mirror. Increase mirror radius, or decrease mesh size ***")
    
    d = np.linalg.norm([c_x, c_y])
    delta = d + bounding_radius - R
    dx = -(c_x / d) * delta
    dy = -(c_y / d) * delta
    mesh.apply_translation([dx, dy, 0.0])
    print("*** Mesh has been shifted to fit within mirror circle ***")
    print(f"New bounds {mesh.bounds}")
    
# Setup
# %%
delta = np.deg2rad(0)
rho = 300.
R = 50
C = np.array([0.0, 0.0, 0.0])   # center
# V = np.array([rho*np.cos(delta), rho*np.cos(delta), 300.0])  # viewpoint
V = np.array([300., 0., 600.])

A_points = []
reflected_points = []

# load mesh from file
f_mesh = trimesh.load_mesh("model_examples//eiffel_tower.stl")
f_mesh.units = 'mm'
# use os module and generate good path instead of concatenating
output_dir_name = "output"
if not os.path.exists(output_dir_name):
    os.makedirs(output_dir_name)
f_name = os.path.join(output_dir_name, "ana_"+f_mesh.metadata['name']) # the metadata dict gets cleared after copying (idk why)

if not mesh_within_circle(f_mesh.vertices, R):
    print("Mesh not within cylinder. Trying to shift it...")
    move_mesh_inside_circle(f_mesh, R)

"""Change this based on requirement"""
no_subdivisions = 0
if no_subdivisions > 0:
    f_mesh = f_mesh.subdivide(iterations = no_subdivisions)

f_mesh_vertices = f_mesh.vertices
print("Mesh within circle T/F: ", mesh_within_circle(f_mesh_vertices, R))

# print(f_mesh_vertices, '\n')
for A in f_mesh_vertices:
    # Ray from V to A
    d = A - V
    d = d / np.linalg.norm(d)

    # Step 2: Intersection with cylinder
    I = ray_cylinder_intersection(V, d, R)
    if I is None:
        continue
    
    # normal isnt simply I-C, since the cylinder is invariant in z
    # the z component must be forced to 0
    # adding z component is sphere normal
    n = np.array([I[0]-C[0], I[1]-C[1], 0.0])
    n = n / np.linalg.norm(n)  # normalize normal

    r = reflect(d, n)

    d_AI = np.linalg.norm(A - I)
    P_ref = I + d_AI * r

    reflected_points.append(P_ref)
print("Number of vertices in output mesh: ", len(reflected_points))

# generate mesh for stl export
new_mesh = f_mesh.copy(include_cache=True)
new_mesh.vertices = reflected_points
new_mesh.show(viewer = 'gl')

new_mesh.export(f_name)

# ------------------------
# Plot
# ------------------------
to_plot = False
if not to_plot:
    exit("Not plotting")

bounding_radius = f_mesh.bounding_cylinder.primitive.radius
bounding_circle_centre = f_mesh.bounding_cylinder.primitive.transform[:2, 3]

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# Circle
theta = np.linspace(0, 2*np.pi, 100)
x_c = R*np.cos(theta)
y_c = R*np.sin(theta)
z_c = np.zeros_like(theta)

x_b = bounding_circle_centre[0] + bounding_radius*np.cos(theta)
y_b = bounding_circle_centre[1] + bounding_radius*np.sin(theta)
z_b = np.zeros_like(theta)

ax.plot(x_c, y_c, z_c)
ax.plot(x_b, y_b, z_b)

ax.scatter([i[0] for i in f_mesh_vertices], [i[1] for i in f_mesh_vertices], [i[2] for i in f_mesh_vertices])
ax.scatter([i[0] for i in reflected_points], [i[1] for i in reflected_points], [i[2] for i in reflected_points])

# viewpoint
ax.scatter(V[0], V[1], V[2], color='black')

ax.set_aspect('equal')
ax.view_init(90, -90, 0) # see XY plane
plt.show()