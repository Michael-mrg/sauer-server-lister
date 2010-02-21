import time
from stream import BSReader
from twisted.internet import defer, protocol

class ServerPinger(protocol.DatagramProtocol):
    
    def __init__(self, server):
        self.server = server
        self.d = defer.Deferred()

    def startProtocol(self):
        self.transport.connect(self.server.addr, self.server.port + 1)
        self.transport.write('1111111111')
        self.sent_time = time.time()

    def datagramReceived(self, data, host):
        self.server.ping = (time.time() - self.sent_time) * 1000
        p = BSReader(data)
        p.read_char(10)
        self.server.num_players = p.read_int()

        attrs = p.read_int(p.read_int())
        self.server.protocol, self.server.game_mode, self.server.mins_left, self.server.max_players, self.server.master_mode = attrs

        self.server.map_name = p.read_string()
        self.server.description = p.read_string()
        self.d.callback(self.server)

