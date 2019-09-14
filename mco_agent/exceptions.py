class AgentException(Exception):
    """ Base exception"""
    description = 'Unknown error'
    statuscode = 5

    def __str__(self):
        return '{0}: {1}'.format(self.description, ' '.join(self.args))


class RPCAborted(AgentException):
    description = "RPC Aborted"
    statuscode = 1


class UnknownRPCAction(AgentException):
    description = "Unknown RPC Action"
    statuscode = 2


class InvalidRPCData(AgentException):
    description = "Invalid Data"
    statuscode = 4


class ImproperlyConfigured(AgentException):
    description = "RPC Aborted"


class InactiveAgent(AgentException):
    description = "Agent is not activated"
