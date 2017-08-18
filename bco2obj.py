from BCOllider import RacetrackCollision, read_uint16

def create_col(f, mkdd_collision):
    for v_x, v_y, v_z in mkdd_collision.vertices:
        f.write("v {0} {1} {2}\n".format(v_x, v_y, v_z))

    lasttype = None

    for v1, v2, v3, rest in mkdd_collision.triangles:

        floor_type = read_uint16(rest, 0x16-0xC)

        if lasttype != floor_type:
            f.write("usemtl Roadtype_0x{0:04X}\n".format(floor_type))
            lasttype = floor_type

        f.write("f {0} {1} {2}\n".format(v1+1,v2+1,v3+1))

if __name__ == "__main__":
    with open("mkddcol/luigi_course.bco", "rb") as f:
        col = RacetrackCollision()
        col.load_file(f)

    with open("test.obj", "w") as f:
        create_col(f, col)