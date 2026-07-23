## Overview
This project implements cylindrical mirror anamorphosis for 3D meshes. It takes a 3D mesh as input and generates a geometrically distorted 3D mesh that appears as the original object when viewed through the reflection of a cylindrical mirror.
The transformation is based on the reflection vector geometry of a cylindrical mirror, mapping the original model into an anamorphic form.
The generated mesh may be heavily distorted and can cause slicing issues for 3D printing.

## Usage
Pass path to an .stl file. An anamorphic .stl file will be written to ./output/ana_{file_name}.stl

Currently only cylindrical reflection is implemented. Check todo for pipeline.
# ALWAYS CHECK number of subdivisions before running the file. Can eat up lot of memory and increase computational time.
### actual_reflection.py back calculates the anamorphosis mesh to arrive at the original mesh, and plots them
### compare_stl.py plots both meshes for comparison
### both files should give same output
## Todo
- Refactor code for object oriented behaviour
- Make spherical and conical reflecting bodies
- Generalize reflecting surface to be able to take any random shape
- GUI

## Note: Eiffel tower model is from GrabCad
