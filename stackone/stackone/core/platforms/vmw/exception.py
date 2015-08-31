class VcenterException(Exception):
    def __init__(self, message=None):
        Exception.__init__(self, message)
        self.message = message



class VCenterDownError(VcenterException):
    def __init__(self, message=None):
        VcenterException.__init__(self, message)



