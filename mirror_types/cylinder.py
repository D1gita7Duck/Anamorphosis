import numpy as np
# plt.switch_backend("Qt5Agg")
from math import sqrt
from numpy.typing import NDArray
import trimesh
import os
"""
UNITS ARE IN mm (millimeter)
"""

def dist(P1 : list[float], P2 : list[float]):
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

class CylindricalMirror:
    def __init__(self, file_path : str, viewpoint : list[float], radius : float = 25., no_subdivisions : int = 0, preview_mesh : bool = True):
        if radius <= 0:
            raise ValueError("Radius cannot be zero or negative")
        if len(viewpoint) != 3:
            raise ValueError(f"Received viewpoint array of length {len(viewpoint)} instead of 3")
        if no_subdivisions < 0:
            raise ValueError("Number of subdivisions cannot be less than 0")
        if type(preview_mesh) != bool:
            raise ValueError("Received wrong type for preview_mesh instead of bool")
        self.input_file_path = file_path
        self.R = radius
        self.V = np.array(viewpoint)
        self.no_subdivisions = no_subdivisions
        self.preview_mesh = preview_mesh
        self.generate()

    def generate(self):
        # Setup
        C = np.array([0.0, 0.0, 0.0])   # center
        reflected_points = []
        
        # load mesh from file
        self.f_mesh = trimesh.load_mesh(self.input_file_path)
        self.f_mesh.units = 'mm'
        output_dir_name = "output"
        if not os.path.exists(output_dir_name):
            os.makedirs(output_dir_name)
        output_f_name = os.path.join(output_dir_name, "ana_cyl_"+self.f_mesh.metadata['name']) # the metadata dict gets cleared after copying (idk why)
        
        if not mesh_within_circle(self.f_mesh.vertices, self.R):
            print("Mesh not within cylinder. Trying to shift it...")
            move_mesh_inside_circle(self.f_mesh, self.R)
        
        """Change this based on requirement"""
        self.no_subdivisions = 5
        if self.no_subdivisions > 0:
            self.f_mesh = self.f_mesh.subdivide(iterations = self.no_subdivisions)
        
        f_mesh_vertices = self.f_mesh.vertices
        print("Mesh within circle T/F: ", mesh_within_circle(f_mesh_vertices, self.R))
        
        # print(f_mesh_vertices, '\n')
        for A in f_mesh_vertices:
            # Ray from V to A
            d = A - self.V
            d = d / np.linalg.norm(d)
        
            # Step 2: Intersection with cylinder
            I = ray_cylinder_intersection(self.V, d, self.R)
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
        self.new_mesh = self.f_mesh.copy(include_cache=True)
        self.new_mesh.vertices = reflected_points
        self.new_mesh.export(output_f_name)
        print(f"Anamorphosised mesh has been exported to {output_f_name}")
        if self.preview_mesh:
            self.new_mesh.show(viewer = 'gl')