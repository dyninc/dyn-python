# Dyn Python SDK - Developer Preview


NOTE: This is a developer preview - we welcome your feedback!
Please reach out via pull request or GitHub issue.


Making DNS Updates as easy as:

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


# API Endpoints Supported

* Session API: create/destroy
* Record API: AAAA A CNAME DNSKEY DS KEY LOC MX NS PTR RP SOA SRV TXT
* Zone API: list/get/publish/freeze/thaw

# Known Issues

* None yet
