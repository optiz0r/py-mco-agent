import json
from jsonschema import validate, ValidationError

from mco_agent.exceptions import InvalidRequest, UnknownProtocol, ImproperlyConfigured


class ProtocolMessage:

    # Maps protocols to the correct ProtocolMessage subclass
    # Filled in by calls to register_protocol
    _protocols = {}

    # To be overridden by subclasses
    _schema = {
        "type": "object",
        "properties": {},
    }

    def __init__(
            self,
            **kwargs,
    ):
        for prop in self._schema["properties"]:
            setattr(self, prop, kwargs.get(prop, None))

    @classmethod
    def get_protocol(cls, protocol_name):
        if protocol_name not in cls._protocols:
            raise UnknownProtocol(protocol_name)

        protocol = cls._protocols[protocol_name]
        return protocol


    @classmethod
    def from_json(cls, request):
        message = json.loads(request)
        return cls.from_dict(message)

    @classmethod
    def from_dict(cls, message):
        """ Cosntructs a ProtocolMessage object from a dictionary of fields

        :param message: dict Message fields received
        """
        try:
            # noinspection PyProtectedMember
            validate(message, cls._schema)
        except ValidationError as e:
            # Use of jsonschema is an implementation detail, so convert this error
            # into our own exception type
            raise InvalidRequest(str(e))

        # Clone the message so as not to modify the original
        fields = message.copy()

        # Allow subclasses to override the fields as required
        cls.parse_message_hook(fields)

        obj = cls(**fields)
        return obj

    @classmethod
    def parse_message_hook(cls, fields):
        """ Hook to override how the message is converted into a protocol object

        Subclasses may override this method in order to customise the arguments to the constructor,
        for example converting a nested object into another ProtocolMessage object

        :param fields: dict Populated list of fields to pass to the ProtocolMessage constructor
        :return: None
        """
        pass

    @staticmethod
    def create_reply():
        """ Returns a reply object appropriate for this protocol

        :return: Reply
        """
        raise ImproperlyConfigured('Method should only be called for a ProtocolMessage subclass')

    @classmethod
    def register_protocol(cls, protocol_name):
        """ Registers the decorated class with the given protocol name so the correct
            ProtocolMessage object can be constructed when a message is received

        :param protocol_name: str Name of the protocol
        :return:
        """
        def decorator(protocol_cls):
            cls._protocols[protocol_name] = protocol_cls
            return protocol_cls

        return decorator


@ProtocolMessage.register_protocol('choria:mcorpc:external_activation_check:1')
class ExternalActivationCheckHeader(ProtocolMessage):

    _schema = {
        "type": "object",
        "properties": {
            "protocol": {"type": "string"},
            "agent": {"type": "string"},
        }
    }

    @staticmethod
    def create_reply():
        return ActivationReply()


class RequestBody(ProtocolMessage):

    _schema = {
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "action": {"type": "string"},
            "data": {"type": "object"},
            "caller": {"type": "string"},
        }
    }


@ProtocolMessage.register_protocol('choria:mcorpc:external_request:1')
class ExternalRequestHeader(ProtocolMessage):

    # noinspection PyProtectedMember
    _schema = {
        "type": "object",
        "properties": {
            "protocol": {"type": "string"},
            "agent": {"type": "string"},
            "action": {"type": "string"},
            "requestid": {"type": "string"},
            "senderid": {"type": "string"},
            "callerid": {"type": "string"},
            "collective": {"type": "string"},
            "ttl": {"type": "number"},
            "msgtime": {"type": "number"},
            "body": RequestBody._schema,
        }
    }

    @classmethod
    def parse_message_hook(cls, fields):
        fields["body"] = RequestBody.from_dict(fields["body"])

    @staticmethod
    def create_reply():
        return ActionReply()


class Reply:

    def successful(self):
        return True


class ActionReply(Reply):

    def __init__(
            self,
            statuscode=0,
            statusmsg='',
            data=None,
            disableresponse=False,
    ):
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
            'disableresponse': self.disableresponse,
        })
        return message

    def fail(self, code, message):
        self.statuscode = code
        self.statusmsg = message

    def successful(self):
        return self.statuscode == 0


class ActivationReply(Reply):

    def __init__(self):
        self.activate = True

    def fail(self):
        self.activate = False

    def to_json(self):
        message = json.dumps({
            'activate': self.activate,
        })
        return message
