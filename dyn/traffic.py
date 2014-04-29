from dyn.client import DynTrafficClient


class DynTraffic(object):
    def __init__(self, customername, username, password):
        self._client = DynTrafficClient() 

        self._customername = customername
        self._username = username
        self._password = password

        self.session = Session(self, customername, username, password)
        self.record  = Record(self)
        self.zone    = Zone(self)

    def with_zone(self, zone):
        self._zone = zone
        return self

class Session(object):
    def __init__(self, dyn, customername, username, password):
       self._dyn = dyn
       self._customername = customername
       self._username = username
       self._password = password

    def create(self):
        creds = {
            'customer_name': self._customername,
            'user_name': self._username,
            'password': self._password
        }
        return self._dyn._client.execute('/Session', 'POST', creds)

    def destroy(self):
        return self._dyn._client.execute('/Session', 'DELETE')

class Zone(object):
    def __init__(self, dyn):
        self._dyn = dyn

    def publish(self):
        return self._dyn._client.execute('/Zone/' + self._dyn._zone, 'PUT', {'publish':True})

    def freeze(self):
        return self._dyn._client.execute('/Zone/' + self._dyn._zone, 'POST', {'freeze':True})

    def thaw(self):
        return self._dyn._client.execute('/Zone/' + self._dyn._zone, 'POST', {'thaw':True})

class Record(object):
    def __init__(self, dyn):
        self._dyn = dyn

    def create(self, type, fqdn, rdata):
        return self._dyn._client.execute('/' + type + 'Record/' + self._dyn._zone + '/' + fqdn, 'POST', dict({'rdata':rdata}) )

    def list(self):
        return self._dyn._client.execute('/' + type + 'Record/' + self._dyn._zone + '/' + fqdn + '/' + id, 'GET')

    def delete(self, type, fqdn, id):
        return self._dyn._client.execute('/' + type + 'Record/' + self._dyn._zone + '/' + fqdn + '/' + id, 'DELETE')

