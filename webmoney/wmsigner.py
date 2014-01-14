import hashlib
from itertools import cycle
import struct
import random

from .exceptions import KeyDataNotFound, KeyCRCFailed

try:
    _ = hashlib.new("md4")
except:
    raise Exception("You need OpenSSL with support of MD4 digest algo.")


class WMSigner(object):
    def __init__(self, wmid, key_password, key_file=None, key_data=None,
                 ekey=None, nkey=None):
        """
        Accepts one of arguments -- key_file or key_data -- to get keyfile
        If keys are already build one can just load them passing ekey/nkey arguments
        """

        self.wmid = wmid

        # load keys if they are already built
        if ekey is not None and nkey is not None:
            self.ekey = ekey
            self.nkey = nkey
            return

        # we have key data from arguments
        if key_data is not None:
            pass
        # or we load data from KWM file
        elif key_file is not None:
            try:
                key_data = open(key_file).read()
            except IOError, e:
                raise KeyDataNotFound(str(e))
        else:
            raise KeyDataNotFound("You should set key_file or key_data parameter")

        # read KWM file by format
        # |reserved|signflag|crc|length|data|
        fmt = "<HH16sL"
        base_size = struct.calcsize(fmt)
        reserved, _, crc, length = struct.unpack(fmt, key_data[:base_size])
        key_buf = key_data[base_size:]

        # build key_fields dict with all KWM data
        key_fields = {"reserved": reserved, "length": length, "crc": crc}
        # transform keydata and create keys in binary form
        key_fields["buf"] = self.__secureKeyByIDPW(key_password, key_buf)
        ekey, nkey = self.__initKeys(key_fields)

        # convert keys to long numbers
        self.ekey = self.__transform_key(ekey)
        self.nkey = self.__transform_key(nkey)

    def __transform_key(self, key):
        return int('0x%s' % key[::-1].encode('hex'), 16)

    def __cycleXor(self, bstr, bkey, shift=0):
        """ """
        # copy input data
        data = list(bstr)

        # we take every byte from bstr and xor it with byte from bkey
        # when bkey is over, it starts from beginning
        # bkey = [A, B]
        # bstr = [1, 2, 3, 4, 5] => [1 ^ A, 2 ^ B, 3 ^ A, 4 ^ B, 5 ^ A]
        source = zip(data[shift:], cycle(bkey))
        data[shift:] = [chr(ord(x) ^ ord(y)) for x, y in source]

        return "".join(data)

    def __shortunswap(self, hex_str):
        if len(hex_str) < 132:
            hex_str = '0'*(132-len(hex_str)) + hex_str

        result = []
        for i in range(len(hex_str) / 4):
            result.append(hex_str[i*4:i*4+4])

        return "".join(result[::-1])

    def __secureKeyByIDPW(self, password, key_buf):
        """ """
        digest = hashlib.new('md4', self.wmid + password).digest()
        return self.__cycleXor(key_buf, digest, 6)

    def __initKeys(self, key_fields):
        """ """

        # build bytestring to check CRC
        data = struct.pack(
            "<HH4LL",
            key_fields['reserved'], 0, 0, 0, 0, 0,
            key_fields['length']
        ) + key_fields['buf']
        crc = hashlib.new('md4', data).digest()
        if crc != key_fields['crc']:
            raise KeyCRCFailed("Checksum failed. Key-data seems corrupted. "
                               "Key password may be wrong.")

        # store data size for ekey data, first part
        fmt1 = "<LH"
        len1 = struct.calcsize(fmt1)
        _, e_len = struct.unpack(fmt1, key_fields['buf'][:len1])

        # store data size before second part, nkey data
        fmt2 = "<LH%dsH" % e_len
        len2 = struct.calcsize(fmt2)

        # read ekey, length of nkey and finally read nkey
        ekey, n_len = struct.unpack("<%dsH" % e_len, key_fields['buf'][len1:len2])
        nkey = key_fields['buf'][len2:]

        return ekey, nkey

    def sign(self, data, debug=False):
        """ """
        plain = [hashlib.new('md4', data).digest(), ]
        for i in range(10):
            pad = random.randint(0, 4294967295) if not debug else 0
            plain.append(struct.pack("<L", pad))
        plain = "".join(plain)
        plain = struct.pack("<H", len(plain)) + plain

        m = self.__transform_key(plain)
        a = pow(m, self.ekey, self.nkey)
        result = self.__shortunswap("%X" % a).lower()

        return result
