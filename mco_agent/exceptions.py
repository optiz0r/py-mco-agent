class AgentException(Exception):
    """ Base exception"""
    pass


class ImproperlyConfigured(AgentException):
    pass


class UnknownProtocol(AgentException):
    pass


class InactiveAgent(AgentException):
    pass


class InvalidRequest(AgentException):
    pass
