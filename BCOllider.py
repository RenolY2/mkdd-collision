# Python 3 necessary

from struct import unpack_from

def read_array(buffer, offset, length):


def read_float(buffer, offset):
    return unpack_from(">I", buffer, offset)[0]

def read_uint32(buffer, offset):
    return unpack_from(">I", buffer, offset)[0]

def read_uint16(buffer, offset):
    return unpack_from(">H", buffer, offset)[0]

def read_uint8(buffer, offset):
    return unpack_from("B", buffer, offset)[0]

class RacetrackCollision(object):
    def __init__(self):
        self.header = b"0003"
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

        self.grids = []
        self.triangles = []
        self.vertices = []

    def load_file(self, f):
        data = f.read()
        if data[:0x4] != b"0003":
            raise RuntimeError("Expected header start 0003, but got {0}. "
                               "Likely not MKDD collision!".format(data[:0x4]))


