import struct

def varargsCount(f):
    def wrapper(self, count=0):
        if not count:
            return f(self)
        return [f(self) for i in range(count)]
    return wrapper

class BSReader(str):
    
    position = 0

    def __init__(self, s=''):
        str.__init__(s)

    def __str__(self):
        return ' '.join('%02x' % ord(i) for i in self)

    @varargsCount
    def read_char(self):
        self.position += 1
        return struct.unpack('<b', self[self.position-1:self.position])[0]

    @varargsCount
    def read_uchar(self):
        self.position += 1
        return struct.unpack('<B', self[self.position-1:self.position])[0]

    @varargsCount
    def read_int(self):
        c = self.read_char()
        v = {-128: ('<h', 2), -127: ('<i', 4)}
        if c in v:
            self.position += v[c][1]
            return struct.unpack(v[c][0], self[self.position-v[c][1]:self.position])[0]
        return c

    @varargsCount
    def read_string(self):
        start, self.position = self.position, self.index('\x00', self.position)+1
        return self[start:self.position-1]

    @varargsCount
    def read_ushort_c(self):
        self.position += 2
        return struct.unpack('<H', self[self.position-2:self.position])[0]

    @varargsCount
    def read_uint_c(self):
        self.position += 4
        return struct.unpack('<I', self[self.position-4:self.position])[0]

    def sub_buffer(self, len):
        self.position += len
        return BSReader(self[self.position-len:self.position-1])

class BSWriter(object):

    def __init__(self, *data):
        self.data = []
        if data:
            for i in data:
                self.write_int(i)

    def __str__(self):
        return ''.join(self.data)

    def write_int(self, i):
        if -0x7F < i < 0x80:
            self.data.append(struct.pack('b', i))
        elif -0x8000 < i < 0x8000:
            self.data.append('\x80' + struct.pack('<h', i))
        else:
            self.data.append('\x81' + struct.pack('<i', i))

