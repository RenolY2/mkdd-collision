from BCOllider import RacetrackCollision, read_uint16, read_uint8, read_uint32

def create_col(f, soundfile, mkdd_collision):
    f.write("o somecustomtrack\n")
    for v_x, v_y, v_z in mkdd_collision.vertices:
        f.write("v {0} {1} {2}\n".format(v_x, v_y, v_z))

    lasttype = None
    """for ix in range(mkdd_collision.grid_xsize):
        for iz in range(mkdd_collision.grid_zsize):
            index = ix + iz*mkdd_collision.grid_xsize

            offset = index*8

            tricount = read_uint8(mkdd_collision._data, mkdd_collision.gridtable_offset + offset + 0x00)
            trioffset = read_uint32(mkdd_collision._data, mkdd_collision.gridtable_offset + offset + 0x04) * 2
            f.write("g {:04}-{:04}\n".format(ix, iz))
            for i in range(tricount):
                triindex = read_uint16(mkdd_collision._data, mkdd_collision.triangles_indices_offset + trioffset + i*2)
                v1,v2,v3,rest = mkdd_collision.triangles[triindex]
                f.write("f {0} {1} {2}\n".format(v1+1,v2+1,v3+1))"""
    i = 1
    floortypes = {}
    
    #with open("neighbours2.txt", "w") as fasd:
    if True:
        for v1, v2, v3, rest in mkdd_collision.triangles:

            floor_type = read_uint16(rest, 0x16-0xC)
            unk = read_uint32(rest, 0x20-0xC)
            unk1, unk2, unk3 = read_uint16(rest, 0x1A-0xC),read_uint16(rest, 0x1C-0xC),read_uint16(rest, 0x1E-0xC)
            for val in (unk1, unk2, unk3):
                assert val == 65535 or val < len(mkdd_collision.triangles)
            #if floor_type in (0x1200, 0x200, 0x201):
            #if True:
            #print(i, hex(floor_type),unk1+1,unk2+1,unk3+1, len(mkdd_collision.triangles))
            #fasd.write("{0} {1} {2} {3} {4} {5} {6}\n".format(i, hex(floor_type),unk1+1,unk2+1,unk3+1, len(mkdd_collision.triangles), (v1,v2,v3)))
            if lasttype != floor_type:
                if floor_type not in floortypes:
                    for entry in mkdd_collision.matentries:
                        if floor_type>>8 == entry[0] and floor_type & 0xFF == entry[1]:
                            floortypes[floor_type] = entry[2:]

                f.write("usemtl Roadtype_0x{0:04X}\n".format(floor_type, unk2))
                lasttype = floor_type

            f.write("f {0} {1} {2}\n".format(v1+1,v2+1,v3+1))
            i += 1
    
    for floortype in sorted(floortypes.keys()):
        matdata = floortypes[floortype]
        
        soundfile.write("0x{:04X}=0x{:X}, 0x{:X}, 0x{:X}\n".format(floortype, *matdata))
            
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("input",
                        help="Filepath to bco file to be converted to obj")
    parser.add_argument("output", default=None, nargs = '?',
                        help="Output path of the created collision file")
                        
    args = parser.parse_args()
    
    #with open("F:/Wii games/MKDDModdedFolder/P-GM4E/files/Course/luigi2/luigi_course.bco", "rb") as f:
    with open(args.input, "rb") as f:
        #with open("F:/Wii games/MKDDModdedFolder/P-GM4E/files/Course/daisy/daisy_course.bco", "rb") as f:
        col = RacetrackCollision()
        col.load_file(f)
    print("Collision loaded")
    if args.output is None:
        output = args.input + ".obj"
    else:
        output = args.output
        
    with open(output, "w") as f:
        with open(output+"_sound.txt", "w") as g: 
            create_col(f, g, col)
    print("Written obj to", output)