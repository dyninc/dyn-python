
from dyn.traffic import DynTraffic

# create a new instance of the API client
dyn = DynTraffic('customername', 'username', 'password').with_zone('example.com')

# establish an API connection
dyn.session.create()

# create a CNAME record
dyn.record.create('CNAME', 'www.example.com.', {'address':'1.2.3.4'})

# publish changes
dyn.zone.publish()

# log out to finish session
dyn.session.destroy()

