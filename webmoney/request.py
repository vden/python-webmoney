import os
import httplib
import socket
import ssl
import urllib2


PEM_FILE = os.path.join(os.path.dirname(__file__), 'WebMoneyCA.crt')


class VerifiedHTTPSConnection(httplib.HTTPConnection):
    "Verified connection to SSL host"

    default_port = 443

    def connect(self):
        sock = socket.create_connection(
            (self.host, self.port),
            self.timeout, self.source_address
        )

        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        self.sock = ssl.wrap_socket(sock, ca_certs=PEM_FILE, cert_reqs=ssl.CERT_REQUIRED)


class HTTPSHandler(urllib2.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(VerifiedHTTPSConnection, req)


wm_opener = urllib2.build_opener(HTTPSHandler)
