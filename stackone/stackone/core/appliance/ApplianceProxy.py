class ApplianceProxy:
    def getProxyIntegration(self):
        return None

    # Callback 
    def executeOp(self, context, opcode):
        raise Exception("Appliance operation not implemented ", opcode)


