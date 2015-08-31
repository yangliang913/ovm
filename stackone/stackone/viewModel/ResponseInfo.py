class ResponseInfo():
    def __init__(self, data):
        self.data = data

    def toXml(self, xml):
        response_xml = xml.createElement('ResponseInfo')
        response_xml.setAttribute('data', self.data)
        return response_xml



