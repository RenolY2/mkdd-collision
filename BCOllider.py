# Python 3 necessary

from struct import unpack_from

def read_array(buffer, offset, length):
    return buffer[offset:offset+length]

def read_float(buffer, offset):
    return unpack_from(">f", buffer, offset)[0]

def read_int32(buffer, offset):
    return unpack_from(">i", buffer, offset)[0]

def read_uint32(buffer, offset):
    return unpack_from(">I", buffer, offset)[0]

def read_uint16(buffer, offset):
    return unpack_from(">H", buffer, offset)[0]

def read_uint8(buffer, offset):
    return unpack_from("B", buffer, offset)[0]

class RacetrackCollision(object):
    def __init__(self):
        self._data = None
        self.identifier = b"0003"
        self.grid_xsize = 0
        self.grid_zsize = 0
        self.coordinate1_x = 0
        self.coordinate1_z = 0
        self.coordinate2_x = 0
        self.coordinate2_z = 0
        self.entrycount = 0
        self.padding = 0

        self.gridtableoffset = 0
        self.gridsoffset = 0
        self.trianglesoffset = 0
        self.verticesoffset = 0
        self.unknownoffset = 0

        self.grids = []
        self.triangles = []
        self.vertices = []

    def load_file(self, f):
        data = f.read()
        self._data = data
        if data[:0x4] != b"0003":
            raise RuntimeError("Expected header start 0003, but got {0}. "
                               "Likely not MKDD collision!".format(data[:0x4]))

        self.identifier = data[:0x4]


        self.grid_xsize = read_uint16(data, 0x4)
        self.grid_zsize = read_uint16(data, 0x6)

        self.coordinate1_x = read_int32(data, 0x8)
        self.coordinate1_z = read_int32(data, 0xC)
        self.coordinate2_x = read_int32(data, 0x10)
        self.coordinate2_z = read_int32(data, 0x14)

        self.entrycount = read_uint16(data, 0x18)
        self.padding = read_uint16(data, 0x1A)

        self.gridtableoffset = 0x2C
        self.gridsoffset = read_uint32(data, 0x1C)
        self.trianglesoffset = read_uint32(data, 0x20)
        self.verticesoffset = read_uint32(data, 0x24)
        self.unknownoffset = read_uint32(data, 0x28)

        # Parse triangles
        trianglescount = (self.verticesoffset-self.trianglesoffset) // 0x24
        print((self.verticesoffset-self.trianglesoffset)%0x24)

        for i in range(trianglescount):
            v1 = read_int32(data, self.trianglesoffset+i*0x24 + 0x00)
            v2 = read_int32(data, self.trianglesoffset+i*0x24 + 0x04)
            v3 = read_int32(data, self.trianglesoffset+i*0x24 + 0x08)
            rest = read_array(data, self.trianglesoffset+i*0x24 + 0x0C, length=0x24-0xC)

            self.triangles.append((v1,v2,v3,rest))

        # Parse vertices
        vertcount = (self.unknownoffset-self.verticesoffset) // 0xC
        print((self.unknownoffset-self.verticesoffset) % 0xC)

        biggestx = biggestz = -99999999
        smallestx = smallestz = 99999999

        for i in range(vertcount):
            x = read_float(data, self.verticesoffset + i*0xC + 0x00)
            y = read_float(data, self.verticesoffset + i*0xC + 0x04)
            z = read_float(data, self.verticesoffset + i*0xC + 0x08)
            self.vertices.append((x,y,z))

            if x > biggestx:
                biggestx = x
            if x < smallestx:
                smallestx = x

            if z > biggestz:
                biggestz = z
            if z < smallestz:
                smallestz = z
            #print(x,y,z)
        print(biggestx, biggestz, smallestx, smallestz)



if __name__ == "__main__":
    col = RacetrackCollision()
    with open("mkddcol/babyluigi_course.bco", "rb") as f:
        col.load_file(f)

    for i in (col.gridsoffset, col.trianglesoffset, col.verticesoffset, col.unknownoffset):
        print(hex(i))
    print(hex(len(col._data)))

    print(col.coordinate1_x)

    print(col.coordinate1_z)

    print(col.coordinate2_x)

    print(col.coordinate2_z)

    print(hex(col.grid_xsize), hex(col.grid_zsize))