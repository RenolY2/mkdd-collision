# BCOnvert.py v0.1 by Yoshi2

import time
import argparse
import os
import subprocess
from re import match
from struct import pack, unpack
from math import floor, ceil

def read_vertex(v_data):
    split = v_data.split("/")
    if len(split) == 3:
        vnormal = int(split[2])
    else:
        vnormal = None
    v = int(split[0])
    return v, vnormal

def read_obj(objfile):

    vertices = []
    faces = []
    face_normals = []
    normals = []

    floor_type = 0x100

    smallest_x = smallest_z = biggest_x = biggest_z = None


    for line in objfile:
        line = line.strip()
        args = line.split(" ")

        if len(args) == 0 or line.startswith("#"):
            continue
        cmd = args[0]

        if cmd == "v":
            #print(args)
            for i in range(args.count("")):
                args.remove("")

            x,y,z = map(float, args[1:4])
            vertices.append((x,y,z))

            if smallest_x is None:
                # Initialize values
                smallest_x = biggest_x = x
                smallest_z = biggest_z = z
            else:
                if x < smallest_x:
                    smallest_x = x
                elif x > biggest_x:
                    biggest_x = x
                if z < smallest_z:
                    smallest_z = z
                elif z > biggest_z:
                    biggest_z = z

        elif cmd == "f":
            # if it uses more than 3 vertices to describe a face then we panic!
            # no triangulation yet.
            if len(args) != 4:
                raise RuntimeError("Model needs to be triangulated! Only faces with 3 vertices are supported.")
            v1, v2, v3 = map(read_vertex, args[1:4])

            faces.append((v1,v2,v3, floor_type))

        elif cmd == "vn":
            nx,ny,nz = map(float, args[1:4])
            normals.append((nx,ny,nz))

        elif cmd == "usemtl":
            assert len(args) >= 2

            matname = " ".join(args[1:])

            floor_type_match = match("^(.*?)(0x[0-9a-fA-F]{4})(.*?)$", matname)

            if floor_type_match is not None:
                floor_type = int(floor_type_match.group(2), 16)
            else:
                floor_type = 0x100

            #print("Found material:", matname, "Using floor type:", hex(floor_type))




    #objects.append((current_object, vertices, faces))
    return vertices, faces, normals, (smallest_x, smallest_z, biggest_x, biggest_z)

def collides(face_v1, face_v2, face_v3, box_mid_x, box_mid_z, box_size_x, box_size_z):
    min_x = min(face_v1[0], face_v2[0], face_v3[0]) - box_mid_x
    max_x = max(face_v1[0], face_v2[0], face_v3[0]) - box_mid_x

    min_z = min(face_v1[2], face_v2[2], face_v3[2]) - box_mid_z
    max_z = max(face_v1[2], face_v2[2], face_v3[2]) - box_mid_z

    half_x = box_size_x / 2.0
    half_z = box_size_z / 2.0

    if max_x < -half_x or min_x > +half_x:
        return False
    if max_z < -half_z or min_z > +half_z:
        return False

    return True

def calc_middle(vertices, v1, v2, v3):
    x1, y1, z1 = vertices[v1]
    x2, y2, z2 = vertices[v2]
    x3, y3, z3 = vertices[v3]

    return (x1+x2+x3)/3.0, (y1+y2+y3)/3.0, (z1+z2+z3)/3.0

def calc_middle_of_2(vertices, v1, v2):
    x1, y1, z1 = vertices[v1]
    x2, y2, z2 = vertices[v2]

    return (x1+x2)/2.0, (y1+y2)/2.0, (z1+z2)/2.0

def normalize_vector(v1):
    n = (v1[0]**2 + v1[1]**2 + v1[2]**2)**0.5
    return v1[0]/n, v1[1]/n, v1[2]/n

def create_vector(v1, v2):
    return v2[0]-v1[0],v2[1]-v1[1],v2[2]-v1[2]

def cross_product(v1, v2):
    cross_x = v1[1]*v2[2] - v1[2]*v2[1]
    cross_y = v1[2]*v2[0] - v1[0]*v2[2]
    cross_z = v1[0]*v2[1] - v1[1]*v2[0]
    return cross_x, cross_y, cross_z

def calc_lookuptable(v1, v2, v3):
    min_x = min_y = max_x = max_z = None

    if v1[0] <= v2[0] and v1[0] <= v3[0]:
        min_x = 0
    elif v2[0] <= v1[0] and v2[0] <= v3[0]:
        min_x = 1
    elif v3[0] <= v1[0] and v3[0] <= v2[0]:
        min_x = 2

    if v1[0] >= v2[0] and v1[0] >= v3[0]:
        max_x = 0
    elif v2[0] >= v1[0] and v2[0] >= v3[0]:
        max_x = 1
    elif v3[0] >= v1[0] and v3[0] >= v2[0]:
        max_x = 2

    if v1[2] <= v2[2] and v1[2] <= v3[2]:
        min_z = 0
    elif v2[2] <= v1[2] and v2[2] <= v3[2]:
        min_z = 1
    elif v3[2] <= v1[2] and v3[2] <= v2[2]:
        min_z = 2

    if v1[2] >= v2[2] and v1[2] >= v3[2]:
        max_z = 0
    elif v2[2] >= v1[2] and v2[2] >= v3[2]:
        max_z = 1
    elif v3[2] >= v1[2] and v3[2] >= v2[2]:
        max_z = 2

    return min_x, min_z, max_x, max_z

def read_int(f):
    val = f.read(0x4)
    return unpack(">I", val)[0]

def read_float_tripple(f):
    val = f.read(0xC)
    return unpack(">fff", val)

def write_uint32(f, val):
    f.write(pack(">I", val))

def write_int32(f, val):
    f.write(pack(">i", val))

def write_ushort(f, val):
    f.write(pack(">H", val))

def write_short(f, val):
    f.write(pack(">h", val))

def write_byte(f, val):
    f.write(pack("B", val))

def write_float(f, val):
    f.write(pack(">f", val))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("input",
                        help="Filepath of the wavefront .obj file that will be converted into collision")
    parser.add_argument("output", default=None, nargs = '?',
                        help="Output path of the created collision file")
    parser.add_argument("--cell_size", default=1000, type=int,
                        help="Size of a single cell in the grid. Bigger size results in smaller grid size but higher amount of triangles in a single cell.")

    args = parser.parse_args()
    input_model = args.input

    base_dir = os.path.dirname(input_model)

    if args.output is None:
        output = input_model + ".bco"
    else:
        output = args.output


    with open(input_model, "r") as f:
        vertices, triangles, normals, minmax_coords = read_obj(f)
    print(input_model, "loaded")
    if len(triangles) > 2**16:
        raise RuntimeError("Too many triangles: {0}\nOnly <=65536 triangles supported!".format(len(triangles)))

    smallest_x, smallest_z, biggest_x, biggest_z = minmax_coords

    assert args.cell_size > 0

    cell_size_x = args.cell_size #1000.0
    cell_size_z = args.cell_size #1000.0


    grid_start_x = floor(smallest_x / cell_size_x) * cell_size_x
    grid_start_z = floor(smallest_z / cell_size_z) * cell_size_z

    grid_end_x = ceil(biggest_x / cell_size_x) * cell_size_x
    grid_end_z = ceil(biggest_z / cell_size_z) * cell_size_z

    grid_size_x = (grid_end_x - grid_start_x) / cell_size_x
    grid_size_z = (grid_end_z - grid_start_z) / cell_size_z

    print(grid_start_x, grid_start_z, grid_end_x, grid_end_z)
    print(grid_size_x, grid_size_z)

    assert grid_size_x % 1 == 0
    assert grid_size_z % 1 == 0

    grid_size_x = int(grid_size_x)
    grid_size_z = int(grid_size_z)

    grid = []
    children = []
    print("calculating grid")
    for iz in range(grid_size_z):
        print("progress:",iz, "/",grid_size_z)
        for ix in range(grid_size_x):

            collided = []

            for i, face in enumerate(triangles):
                v1_index, v2_index, v3_index, floor_type = face
                assert (v1_index[0]-1) >= 0 and (v2_index[0]-1) >= 0 and (v3_index[0]-1) >= 0
                v1 = vertices[v1_index[0]-1]
                v2 = vertices[v2_index[0]-1]
                v3 = vertices[v3_index[0]-1]

                if collides(v1, v2, v3,
                            grid_start_x + ix*cell_size_x + cell_size_x//2,
                            grid_start_z + iz*cell_size_z + cell_size_z//2,
                            cell_size_x*3,
                            cell_size_z*3):

                    collided.append((i, face))
            collided.sort(key=lambda entry: (vertices[entry[1][0][0]-1][1]+
                                            vertices[entry[1][1][0]-1][1]+
                                            vertices[entry[1][2][0]-1][1])/3.0, reverse=True)
            grid.append(collided)
    print("grid calculated")
    print("writing bco file")

    with open(output, "wb") as f:
        f.write(b"0003")
        write_ushort(f, grid_size_x)
        write_ushort(f, grid_size_z)
        write_int32(f, int(grid_start_x))
        write_int32(f, int(grid_start_z))
        write_uint32(f, int(cell_size_x))
        write_uint32(f, int(cell_size_z))
        write_ushort(f, 0x0000) # Entry count of last section
        write_ushort(f, 0x0000) # Padding?

        # Placeholder values for later
        write_uint32(f, 0x1234ABCD) # Triangle indices offset
        write_uint32(f, 0x2345ABCD) # triangles offset
        write_uint32(f, 0x3456ABCD) # vertices offset
        write_uint32(f, 0x00000000) # unknown section offset

        print(hex(f.tell()))
        assert f.tell() == 0x2C

        grid_offset = 0x2C

        groups = []

        indices_stored = 0

        for entry in grid:
            tricount = len(entry)
            if tricount >= 120:
                raise RuntimeError("Too many triangles in one spot:", tricount)

            write_byte(f, tricount)
            write_byte(f, 0x00)
            write_ushort(f, 0x0000)
            write_uint32(f, indices_stored)

            indices_stored += tricount
            groups.append(entry)

        print("written grid")
        tri_indices_offset = f.tell()

        for trianglegroup in groups:
            for triangle_index, triangle in trianglegroup:
                write_ushort(f, triangle_index)
        print("written triangle indices")
        tri_offset = f.tell()


        neighbours = {}
        for i, triangle in enumerate(triangles):
            v1_index, v1_normindex = triangle[0]
            v2_index, v2_normindex = triangle[1]
            v3_index, v3_normindex = triangle[2]

            indices = [v1_index, v2_index, v3_index] # sort the indices to always have them in the same order
            indices.sort()

            if i == 0xFFFF:
                print("Warning: Your collision has a triangle with index 0xFFFF. "
                      "This might cause unintended side effects related to that specific triangle.")

            """for edge in ((indices[0], indices[1]), (indices[1], indices[2]), (indices[2], indices[0])):
                if edge not in neighbours:
                    neighbours[edge] = [i]
                elif len(neighbours[edge]) == 1:
                    neighbours[edge].append(i)
                else:
                    print("Warning: Edge {0} already has neighbours {1}, but there is an additional "
                          "neighbour {2} that will be ignored.".format(edge, neighbours[edge], i))"""

        for i, triangle in enumerate(triangles):
            v1_index, v1_normindex = triangle[0]
            v2_index, v2_normindex = triangle[1]
            v3_index, v3_normindex = triangle[2]

            floor_type = triangle[3]

            v1 = vertices[v1_index-1]
            v2 = vertices[v2_index-1]
            v3 = vertices[v3_index-1]


            v1tov2 = create_vector(v1,v2)
            v2tov3 = create_vector(v2,v3)
            v3tov1 = create_vector(v3,v1)
            v1tov3 = create_vector(v1,v3)


            cross_norm = cross_product(v1tov2, v1tov3)
            #cross_norm = cross_product(v1tov2, v1tov3)

            if cross_norm[0] == cross_norm[1] == cross_norm[2] == 0.0:
                norm = cross_norm
                print("norm calculation failed")
            else:
                norm = normalize_vector(cross_norm)

            norm_x = int(round(norm[0], 4) * 10000)
            norm_y = int(round(norm[1], 4) * 10000)
            norm_z = int(round(norm[2], 4) * 10000)

            midx = (v1[0]+v2[0]+v3[0])/3.0
            midy = (v1[1]+v2[1]+v3[1])/3.0
            midz = (v1[2]+v2[2]+v3[2])/3.0

            floatval = (-1)*(round(norm[0], 4) * midx + round(norm[1], 4) * midy + round(norm[2], 4) * midz)

            min_x, min_z, max_x, max_z = calc_lookuptable(v1, v2, v3)

            vlist = (v1, v2, v3)
            assert vlist[min_x][0] == min(v1[0], v2[0], v3[0])
            assert vlist[min_z][2] == min(v1[2], v2[2], v3[2])

            assert vlist[max_x][0] == max(v1[0], v2[0], v3[0])
            assert vlist[max_z][2] == max(v1[2], v2[2], v3[2])

            indices = [v1_index, v2_index, v3_index] # sort the indices to always have them in the same order
            indices.sort()

            """local_neighbours = []
            for edge in ((indices[0], indices[1]), (indices[1], indices[2]), (indices[2], indices[0])):
                if edge in neighbours:
                    neighbour = neighbours[edge]
                    if len(neighbour) == 1:
                        local_neighbours.append(0xFFFF)
                    elif i == neighbour[0] and (floor_type & 0xFF00) == (triangles[neighbour[1]][3] & 0xFF00):
                        local_neighbours.append(neighbour[1])
                    elif i == neighbour[1] and (floor_type & 0xFF00) == (triangles[neighbour[0]][3] & 0xFF00):
                        local_neighbours.append(neighbour[0])
                    else:
                        local_neighbours.append(0xFFFF)
                else:
                    local_neighbours.append(0xFFFF)"""

            start = f.tell()

            write_uint32(f, v1_index-1)
            write_uint32(f, v2_index-1)
            write_uint32(f, v3_index-1)

            write_float(f, floatval)

            write_short(f, norm_x)
            write_short(f, norm_y)
            write_short(f, norm_z)

            write_ushort(f,floor_type)

            write_byte(f, (max_z << 6) | (max_x << 4) | (min_z << 2) | min_x) # Lookup table for min/max values
            write_byte(f, 0x01) # Unknown

            write_ushort(f, 0xFFFF)#local_neighbours[0]) # Triangle index, 0xFFFF means no triangle reference
            write_ushort(f, 0xFFFF)#local_neighbours[1]) # Triangle index
            write_ushort(f, 0xFFFF)#local_neighbours[2]) # Triangle index
            write_uint32(f, 0x00000000) # Unknown, padding or value that can be set to 0
            end = f.tell()
            assert (end-start) == 0x24
        vertex_offset = f.tell()
        print("written triangle data")
        for x, y, z in vertices:
            write_float(f, x)
            write_float(f, y)
            write_float(f, z)
        print("written vertices")
        unknown_offset = f.tell()

        f.seek(0x1C)

        write_uint32(f, tri_indices_offset) # Triangle indices offset
        write_uint32(f, tri_offset) # triangles offset
        write_uint32(f, vertex_offset) # vertices offset
        write_uint32(f, unknown_offset) # unknown section offset

    print("done, file written to", output)