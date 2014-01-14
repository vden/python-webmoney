# coding: utf-8

from datetime import datetime

from .base import BaseWMRequest


class WMX3(BaseWMRequest):
    """ Spec at http://wiki.webmoney.ru/projects/webmoney/wiki/Интерфейс_X3 """
    url = "https://w3s.webmoney.ru/asp/XMLOperations.asp"

    def get_sign_string(self, reqn, data):
        return data['purse'] + reqn

    def request(self, purse, datestart, datefinish,
                wmtranid=None, tranid=None, wminvid=None, orderid=None):
        data = {
            "purse": purse,
            "datestart": datestart.strftime("%Y%m%d %H:%M:%S"),
            "datefinish": datefinish.strftime("%Y%m%d %H:%M:%S"),
        }
        if wmtranid is not None:
            data['wmtranid'] = str(wmtranid)
        if tranid is not None:
            data['tranid'] = str(tranid)
        if wminvid is not None:
            data['wminvid'] = str(wminvid)
        if orderid is not None:
            data['orderid'] = str(orderid)

        operations = []
        xml = self.send("getoperations", data)
        for operation in xml.findall("operations//operation"):
            operation_data = {}
            for element in operation.iter():
                operation_data[element.tag] = element.text
            del operation_data['operation']  # remove key for root tag

            operation_data['wmtranid'] = operation.get("id")
            operation_data['ts'] = operation.get("ts")

            if "timelock" in operation_data:
                operation_data["timelock"] = True
            else:
                operation_data["timelock"] = False

            operation_data['datecrt'] = datetime.strptime(
                operation_data['datecrt'],
                '%Y%m%d %H:%M:%S'
            )

            operation_data['dateupd'] = datetime.strptime(
                operation_data['dateupd'],
                '%Y%m%d %H:%M:%S'
            )

            operations.append(operation_data)

        return operations