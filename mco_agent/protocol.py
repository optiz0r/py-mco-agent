import json

from choria_external.protocol import ProtocolMessage, Reply


@ProtocolMessage.register_protocol()
class ExternalActivationRequest(ProtocolMessage):

    _protocol = 'io.choria.mcorpc.external.v1.activation_request'

    @staticmethod
    def create_reply():
        return ActivationReply()


@ProtocolMessage.register_protocol()
class ExternalRPCRequest(ProtocolMessage):

    _protocol = 'io.choria.mcorpc.external.v1.rpc_request'

    @staticmethod
    def create_reply():
        return ActionReply()


class ActionReply(Reply):

    _protocol = 'io.choria.mcorpc.external.v1.rpc_reply'

    def __init__(self, statuscode=0, statusmsg='', data=None, disableresponse=False, *args, **kwargs):
        Reply.__init__(self, *args, **kwargs)
        self.statuscode = statuscode
        self.statusmsg = statusmsg
        self.data = data
        self.disableresponse = disableresponse

        if not self.data:
            self.data = {}

    def to_json(self):
        message = json.dumps({
            'statuscode': self.statuscode,
            'statusmsg': self.statusmsg,
            'data': self.data,
        })
        return message

    def fail(self, code, message):
        self.statuscode = code
        self.statusmsg = message

    def successful(self):
        return self.statuscode == 0


class ActivationReply(Reply):

    _protocol = 'io.choria.mcorpc.external.v1.activation_reply'

    def __init__(self, *args, **kwargs):
        Reply.__init__(self, *args, **kwargs)
        self.activate = True

    def fail(self):
        self.activate = False

    def to_json(self):
        message = json.dumps({
            'activate': self.activate,
        })
        return message
