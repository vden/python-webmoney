class WMException(Exception):
    pass


class WMProtoException(WMException):
    pass


class WMClientException(WMException):
    pass


class KeyDataNotFound(WMClientException):
    pass


class KeyCRCFailed(WMClientException):
    pass
