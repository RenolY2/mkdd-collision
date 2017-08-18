# obj2grid.py v0.2.0 by Yoshi2

import time
import argparse
import os
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
            if "" in args:
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

            print("Found material:", matname, "Using floor type:", hex(floor_type))




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

def write_float(f, val):
    f.write(pack(">f", val))


if __name__ == "__main__":
    with open("mkddcol/test_col.obj", "r") as f:
        vertices, triangles, normals, minmax_coords = read_obj(f)


    smallest_x, smallest_z, biggest_x, biggest_z = minmax_coords

    cell_size_x = 1000.0
    cell_size_z = 1000.0


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

    for iz in range(grid_size_z):
        for ix in range(grid_size_x):
            print("progress:",ix,iz)
            collided = []

            for i, face in enumerate(triangles):
                v1_index, v2_index, v3_index, floor_type = face

                v1 = vertices[v1_index[0]-1]
                v2 = vertices[v2_index[0]-1]
                v3 = vertices[v3_index[0]-1]

                if collides(v1, v2, v3,
                            grid_start_x + ix*cell_size_x, #+box_size_x//2,
                            grid_start_z + iz*cell_size_z, #+box_size_z//2,
                            cell_size_x,
                            cell_size_z):

                    collided.append((i, face))

            grid.append(collided)

    with open("custom_col.bco", "wb") as f:
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
        write_uint32(f, 0x4567ABCD) # unknown section offset

        print(hex(f.tell()))
        assert f.tell() == 0x2C

        grid_offset = 0x2C

        for entry in grid:
            print(len(entry))