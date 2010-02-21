#!/bin/env python
import re
import sys
from database import NamesDB
from server_list import getServerList, writeServerList
from twisted.internet import defer, reactor, task

def exit(i):
    reactor.stop()
    db = NamesDB()
    del db

def country(servers):
    
    def findPlayers(i):
        if not i: return
        L = [(p.name, p.countryCode()) for p in i if p.countryCode() in sys.argv[2:]]
        if not L: return
        print i[0].server
        for p in L:
            print '{0}({1})'.format(*p),
        print

    def makeWork(i):
        d = i.getPlayers()
        d.addCallback(findPlayers)
        d.addErrback(lambda i: None)
        return d
    
    coop = task.Cooperator()
    work = (makeWork(i) for i in servers.values())
    dl = defer.DeferredList([coop.coiterate(work) for j in range(4)])
    dl.addCallback(exit)

def match(servers):

    def makeWork(i):
        d = i.getPlayers()
        d.addErrback(lambda i: None)
        return d
    
    coop = task.Cooperator()
    work = (makeWork(i) for i in servers.values())
    dl = defer.DeferredList([coop.coiterate(work) for j in range(4)])
    dl.addCallback(lambda i: tryMatch())
    dl.addCallback(exit)

def tryMatch():
    i = sys.argv[2]
    db = NamesDB()
    by_ip = re.match(r'\d{1,3}[^A-z]*$', i)
    if by_ip:
        db.findByIP(i + '%')
    else:
        db.findByName('%' + i + '%')
    db.readRows()
    if not db._rows: return False

    ip = None
    for row in db._rows:
        if not by_ip and i == row[0]:
            ip = row[1]
        print '{0:20} {1:>13}'.format(*row)

    if ip:
        print
        db.findByIP(ip)
        db.readRows()
        if db._rows:
            db.printRows()

    return True

def search(servers):

    def findPlayers(i, searches):
        if not i: return
        L = []
        for p in i:
            for r in searches:
                if r.search(p.name):
                    L.append('{0}({1})'.format(p.name, p.ip()))
                    continue
        if not L: return
        print i[0].server
        print ' '.join(L)

    def error(i): pass
    
    def makeWork(i, searches):
        d = i.getPlayers()
        d.addCallback(lambda j: findPlayers(j, searches))
        d.addErrback(lambda i: None)
        return d
    
    coop = task.Cooperator()
    searches = [re.compile(i, re.I) for i in sys.argv[2:]]
    work = (makeWork(i, searches) for i in servers.values())
    dl = defer.DeferredList([coop.coiterate(work) for j in range(4)])
    dl.addCallback(lambda j: reactor.stop())

def update(servers):

    def makeWork(i):
        d = i.getPlayers()
        d.addErrback(lambda i: None)
        return d
    
    coop = task.Cooperator()
    work = (makeWork(i) for i in servers.values())
    dl = defer.DeferredList([coop.coiterate(work) for j in range(4)])
    dl.addCallback(exit)
    
if __name__ == '__main__':
    commands = {'search': search, 'country': country, 'match': match, 'update': update}
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print 'Usage: {0} command\n    Commands: {1}'.format(sys.argv[0], ' '.join(sorted(commands.keys())))
        sys.exit(0)
    command = sys.argv[1]

    if command == 'match':
        if tryMatch():
            sys.exit(0)

    d = getServerList()
    d.addCallback(writeServerList)
    d.addCallback(commands[command])
    reactor.run()

