import pygeoip

class Player(object):
    
    gi = pygeoip.GeoIP('GeoIP.dat')
    _countryCode = None

    def __init__(self, server):
        self.server = server

    def ip(self):
        return '{0}.{1}.{2}.255'.format(*self._ip)

    def countryCode(self):
        if not self._countryCode:
            self._countryCode = self.gi.country_code_by_addr(self.ip())
        return self._countryCode

    def __str__(self):
        return '{0:20.20} {1:2} {2:2} {3:3}% {4:2} {5:>15.15}'.format(self.name, self.frags, self.deaths, self.accuracy, self.countryCode(), self.ip())

