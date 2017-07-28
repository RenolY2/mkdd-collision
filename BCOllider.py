# Python 3 necessary

from struct import unpack_from

def read_array(buffer, offset, length):
    return buffer[offset:offset+length]

def read_float(buffer, offset):
    return unpack_from(">I", buffer, offset)[0]

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



if __name__ == "__main__":
    collision = RacetrackCollision()
    with open("mkddcol/babyluigi_course.bco", "rb") as f:
        collision.load_file(f)

    for i in (collision.gridsoffset, collision.trianglesoffset, collision.verticesoffset, collision.unknownoffset):
        print(hex(i))
    print(hex(len(collision._data)))