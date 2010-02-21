from database import NamesDB
from player import Player
from stream import BSReader
from twisted.internet import defer, protocol, reactor

class ServerPlayerLister(protocol.DatagramProtocol):
    
    def __init__(self, server):
        def recordPlayerIPs(i):
            if not i: return
            db = NamesDB()
            for p in i:
                db.addEntry(p.name, p._ip)
            return i

        self.server = server
        self.d = defer.Deferred()
        self.d.addCallback(recordPlayerIPs)
        self.server.players = []
        self.n_players = -1

    def startProtocol(self):
        self.transport.connect(self.server.addr, self.server.port + 1)
        self.transport.write('\0\1\xff')
        reactor.callLater(1, self.timedOut)

    def timedOut(self):
        if self.d.called: return
        self.d.errback(ValueError('Timeout reached.'))

    def datagramReceived(self, data, host):
        p = BSReader(data)
        if p.read_char(6) != [0, 1, -1, -1, 104, 0]:
            self.d.errback(ValueError('Invalid packet received.'))
            return
        v = p.read_char()
        if v == -10:
            self.n_players = len(data) - p.position
        elif v == -11:
            f = Player(self.server)
            f.client_num, f.ping = p.read_int(2)
            f.name, f.team = p.read_string(2)
            f.frags, f.score, f.deaths, f.tks, f.accuracy = p.read_int(5)
            f.health, f.armor, f.weapon, f.priv, f.state = p.read_int(5)
            f._ip = p.read_uchar(3)
            self.server.players.append(f)
        if len(self.server.players) == self.n_players:
            self.d.callback(self.server.players)

