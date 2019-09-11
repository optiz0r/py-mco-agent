import json
from jsonschema import validate, ValidationError

from mco_agent.exceptions import InvalidRequest


class RequestBody:

    _schema = {
        "type": "object",
        "properties": {
            "agent": {"type": "string"},
            "action": {"type": "string"},
            "data": {"type": "object"},
            "caller": {"type": "string"},
        }
    }

    def __init__(
            self,
            **kwargs,
    ):
        for prop in self._schema["properties"]:
            setattr(self, prop, kwargs.get(prop, None))

    @classmethod
    def from_dict(cls, message):
        try:
            validate(message, cls._schema)
        except ValidationError as e:
            raise InvalidRequest(str(e))

        fields = {}
        for prop in cls._schema["properties"]:
            if prop == "body":
                continue
            fields[prop] = message[prop]

        body = RequestBody(**fields)
        return body

    @classmethod
    def from_json(cls, request):
        message = json.loads(request)
        return cls.from_dict(message)


class RequestHeader:

    # noinspection PyProtectedMember
    _schema = {
        "type": "object",
        "properties": {
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

    def __init__(
            self,
            **kwargs
    ):
        for prop in self._schema["properties"]:
            setattr(self, prop, kwargs.get(prop, None))

    @classmethod
    def from_json(cls, request):
        message = json.loads(request)
        try:
            validate(message, cls._schema)
        except ValidationError as e:
            raise InvalidRequest(str(e))

        fields = {
            "body": RequestBody.from_dict(message["body"])
        }

        for prop in cls._schema["properties"]:
            if prop == "body":
                continue
            fields[prop] = message[prop]

        header = RequestHeader(**fields)
        return header


class Reply:

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
