## Python-Webmoney

This is library to make requests to WebMoney XML interfaces.

It includes pure python *wmsigner* to sign requests.

Note: library only supports authorization by keys from KWM file with password.

More information about interfaces at http://wiki.wmtransfer.com/wiki/list/XML-Interfaces


### Requirements: 

 * lxml


### Supported request types:

 * X3 -- get information about operations


### Using:

    :::python
    from datetime import datetime

    from webmoney import WMX3

    key_path = "./123456789012.kwm"
    password = "abcdef"
    wmid = "123456789012"

    wmi = WMX3(wmid, key_path, password)
    operations = wmi.request("R123456789123", datetime(2014, 1, 1), datetime.now())

    for operation in operations:
        print operation['amount'], operation['wmtranid']

    filtered = wmi.request("R123456789123", datetime(2014, 1, 1), datetime.now(),
                           wmtranid='100021')

    print filtered
    