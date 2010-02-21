import cPickle
from server import Server
from twisted.internet import defer, protocol, reactor

SERVERS_FILE = 'servers.txt'

def getServerList():
    d = defer.Deferred()
    try:    getServerListFromFile(d, SERVERS_FILE)
    except: getServerListFromMaster(d, 'sauerbraten.org')
    return d

def getServerListFromFile(d, filename):
    with open(filename) as f:
        servers = dict(((i[0], i[1]), Server(i[0], i[1])) for i in cPickle.load(f))
        servers[('85.214.66.181', 20000)] = Server('85.214.66.181', 20000)
        reactor.callWhenRunning(lambda: d.callback(servers))

class MasterServerProtocol(protocol.Protocol):
    
    def connectionMade(self):
        self.transport.write('list\n')

    def dataReceived(self, data):
        self.factory.data.append(data)

class MasterServerFactory(protocol.ClientFactory):
    
    protocol = MasterServerProtocol
    servers, data = [], []

    def __init__(self, d):
        self.d = d

    def clientConnectionLost(self, connector, reason):
        L = {}
        for i in ''.join(self.data[:-1]).split('\n'):
            k = i.split()
            if k and len(k) > 2:
                L[k[1], int(k[2])] = Server(k[1], int(k[2]))
        self.d.callback(L)

def getServerListFromMaster(d, addr):
    reactor.connectTCP(addr, 28787, MasterServerFactory(d))

def writeServerList(L):
    with open(SERVERS_FILE, 'wb') as f:
        cPickle.dump(L, f, cPickle.HIGHEST_PROTOCOL)
    return L

