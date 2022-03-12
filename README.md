# mkdd-collision
Tool for converting between obj and MKDD's bco (collision) files

## mkdd-collision-creator.py
Converts .obj files to .bco. The simplest usage is to drag a .obj file (with compatible material names) onto the .py file, and a .bco file will be created. The .bco will have the same name as the .obj file, but with .bco added onto the end.
Additional options are for:
* specifying an output file
* "--cell_size <int>"  - default of 1000. Size of a single cell in the grid. Bigger size results in smaller grid size but higher amount of triangles in a single cell.
* "--quadtree_depth <int>" - default of 2. Depth of the subdivision of cells in the grid.
* "--max_tri_count <int>" - default of 20. The number of triangles in a cell or quadtree before it is subdivided
* "--remap_file <filepath>" - default of None. This file allows you to set extra settings and sounds to collision flags as well as use non-collision material names in the final .bco

  
 In game, driving into a triangle that is sufficiently steep (around 90 degrees) will cause a bug. Using the following options is not recommended. Instead, all steep faces should be excluded via material name or omitted from the .obj entirely.
* "--steep_faces_as_walls" - If set, steep faces that have no collision type asigned to them will become walls.
* "--steep_face_angle <float>" - default of 89.5. Minimum angle from the horizontal in degrees a face needs to have to count as a steep face. Value needs to be between 0 and 90."
  
## mkdd-collision-reader.py
Converts .bco files to .obj, and gives a _sound.txt file as well with all the sounds. The most basic usage is to drag an .obj file into the .py file, and an .obj file will be created. The .obj will have the same name as the .bco file, but with .obj added to the end.
Additional options are for:
* specifying an output file
