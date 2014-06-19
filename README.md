# Dyn Python SDK - Developer Preview


NOTE: This is a developer preview - we welcome your feedback!
Please reach out via pull request or GitHub issue.


Making DNS Updates as easy as:

    from dyn.traffic import DynTraffic

    # create a new instance of the API client
    dyn = DynTraffic('customername', 'username', 'password').with_zone('example.com')

    # establish an API connection
    dyn.session.create()


    # create an A record
    dyn.record.create('A', 'www.example.com.', {'address':'1.2.3.4'})

    # create a CNAME record
    dyn.record.create('CNAME', 'www2.example.com.', {'cname':'www.example.com'})


    # delete one A record
    dyn.record.delete('A', 'www.example.com', <record_id>)

    # delete all A record
    dyn.record.delete('A', 'www.example.com')

    # delete a CNAME record
    dyn.record.delete('CNAME', 'www2.example.com')


    # publish changes
    dyn.zone.publish()

    #Get all records from the zone
    dyn.zone.list()

    #Get all records from the node
    dyn.zone.list('www.example.com')


    # log out to finish session
    dyn.session.destroy()


# API Endpoints Supported

* Session API: create/destroy
* Record API: AAAA A CNAME DNSKEY DS KEY LOC MX NS PTR RP SOA SRV TXT
* Zone API: list/get/publish/freeze/thaw

# Known Issues

* None yet
