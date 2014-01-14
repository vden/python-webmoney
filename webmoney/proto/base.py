import urllib2
from lxml import etree
from datetime import datetime
from abc import ABCMeta, abstractmethod

from ..request import HTTPSHandler
from ..exceptions import WMProtoException, WMClientException
from ..wmsigner import WMSigner


class BaseWMRequest(object):
    __metaclass__ = ABCMeta

    url = None
    counter = 0

    def __init__(self, wmid, key_file, key_password):
        assert self.url is not None, "URL should be overridden in implementation"

        self.connection = urllib2.build_opener(HTTPSHandler)
        self.signer = WMSigner(wmid, key_password, key_file=key_file)
        self.wmid = wmid

    @abstractmethod
    def get_sign_string(self, reqn, data):
        """ Returns string to be signed in request """
        raise NotImplementedError

    @abstractmethod
    def request(self, *args, **kwargs):
        """ Make request to service """
        raise NotImplementedError

    def send(self, operation, data):
        self.counter += 1
        if self.counter >= 10000: self.counter = 0

        root = etree.Element("w3s.request")
        _reqn = etree.SubElement(root, "reqn")
        _reqn.text = reqn = "%s%04d" % (datetime.now().strftime("%s"), self.counter)

        _wmid = etree.SubElement(root, "wmid")
        _wmid.text = self.wmid

        _sign = etree.SubElement(root, "sign")
        _sign.text = self.signer.sign(self.get_sign_string(reqn, data))

        _op = etree.SubElement(root, operation)
        for key, value in data.iteritems():
            _el = etree.SubElement(_op, key)
            _el.text = value

        data = etree.tostring(root, pretty_print=True)
        print data
        req = urllib2.Request(self.url, data=data)
        try:
            result = self.connection.open(req).read()
        except urllib2.HTTPError, e:
            raise WMProtoException("HTTP Error: %s" % e.read())
        except Exception, e:
            raise WMProtoException(str(e))

        try:
            xml = etree.fromstring(result)
        except Exception, e:
            raise WMClientException(str(e))

        retval = xml.find("retval").text
        if retval != "0":
            raise WMProtoException(
                "Error %s: %s" % (retval, xml.find("retdesc").text)
            )

        return xml