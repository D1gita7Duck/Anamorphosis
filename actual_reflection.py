import os
from numpy.typing import NDArray
import trimesh
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt

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
    d and n must be unit vectors
    """
    return d - 2 * np.dot(d, n) * n

C = np.array([0., 0., 0.])
R = 50.
V = np.array([300., 0., 300.]) # viewpoint

output_dir = "output"
file_name = "cube.stl"
ana_mesh = trimesh.load_mesh(os.path.join(output_dir, "ana_" + file_name))
ana_mesh.units = "mm"
ana_mesh_vertices = ana_mesh.vertices

og_dir = "model_examples"
og_mesh = trimesh.load_mesh(os.path.join(og_dir, file_name))
og_mesh.units = "mm"
og_mesh_vertices = og_mesh.vertices

virtual_points = []

for P in ana_mesh_vertices:
    # normal vector 
    n = V[:2] + P[:2]
    n = n / np.linalg.norm(n)
    
    # Step 2: Intersection with cylinder
    I = R * n
    if I is None:
        continue
    
    # ir = I - P[:2]
    # ir = ir / np.linalg.norm(ir)
    rr = I - V[:2]
    rr = rr / np.linalg.norm(rr)
    d_PI = np.linalg.norm(P[:2] - I)
    P_ref = I + d_PI * rr
    P_ref = [P_ref[0], P_ref[1], P[2]]

    virtual_points.append(P_ref)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# Circle
theta = np.linspace(0, 2*np.pi, 100)
x_c = R*np.cos(theta)
y_c = R*np.sin(theta)
z_c = np.zeros_like(theta)

# x_b = bounding_circle_centre[0] + bounding_radius*np.cos(theta)
# y_b = bounding_circle_centre[1] + bounding_radius*np.sin(theta)
# z_b = np.zeros_like(theta)

ax.plot(x_c, y_c, z_c)
# ax.plot(x_b, y_b, z_b)

ax.scatter([i[0] for i in ana_mesh_vertices], [i[1] for i in ana_mesh_vertices], [i[2] for i in ana_mesh_vertices])
ax.scatter([i[0] for i in virtual_points], [i[1] for i in virtual_points], [i[2] for i in virtual_points])
ax.scatter([i[0] for i in og_mesh_vertices], [i[1] for i in og_mesh_vertices], [i[2] for i in og_mesh_vertices])

# viewpoint
ax.scatter(V[0], V[1], V[2], color='black')

ax.set_aspect('equal')
ax.view_init(90, -90, 0) # see XY plane
plt.show()