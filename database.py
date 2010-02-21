import sqlite3
import os

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class Database(object):
    def __init__(self, filename):
        create = not os.path.exists(filename)
        self.db = sqlite3.connect(filename)
        self.cur = self.db.cursor()
        if create:
            self.skeleton()

    def skeleton(self):
        pass

    def __del__(self):
        self.cur.close()
        self.db.commit()
        self.db.close()
        
@singleton
class NamesDB(Database):

    _rows = None

    def __init__(self):
        Database.__init__(self, 'names.db')

    def skeleton(self):
        self.cur.execute('create table names (name text, ip text)')

    def addEntry(self, name, ip):
        v = (name, '.'.join(str(i) for i in ip))
        self.cur.execute('select * from names where name = ? and ip = ?', v)
        if not self.cur.fetchone():
            self.cur.execute('insert into names values (?,?)', v)

    def findByIP(self, ip):
        self.cur.execute('select * from names where ip like ? order by name asc', (ip, ))
        self._rows = None
    def findByName(self, name):
        self.cur.execute('select * from names where name like ? order by ip asc', (name, ))
        self._rows = None
        
    def readRows(self):
        self._rows = self.cur.fetchall()

    def printRows(self):
        if not self._rows: self.readRows()
        for row in self._rows:
            print '{0:20} {1:>13}'.format(*row)

