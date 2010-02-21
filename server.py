from server_pinger import ServerPinger
from server_player_lister import ServerPlayerLister
from twisted.internet import reactor

class Server(object):

    def __init__(self, addr, port):
        self.addr, self.port = addr, port

    def __getstate__(self):
        d = self.__dict__.copy()
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __repr__(self):
        return '{0}({1})'.format(self.addr, self.port)

    def sendPing(self):
        p = ServerPinger(self)
        reactor.listenUDP(0, p)
        def stopProto(i):
            p.stopProtocol()
            return i
        p.d.addCallback(stopProto)
        return p.d

    def getPlayers(self):
        p = ServerPlayerLister(self)
        reactor.listenUDP(0, p)
        def stopProto(i):
            p.stopProtocol()
            return i
        p.d.addCallback(stopProto)
        return p.d

