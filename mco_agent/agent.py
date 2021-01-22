import logging

from choria_external.base import ChoriaExternal
from choria_external.config import Config
from choria_external.exceptions import RPCAborted, ChoriaExternalException, UnknownRPCAction

from mco_agent.exceptions import InactiveAgent, AgentException
from mco_agent.protocol import ExternalActivationRequest, ExternalRPCRequest


class Agent(ChoriaExternal):

    _actions = {}

    # noinspection PyUnusedLocal
    @staticmethod
    def should_activate():
        """ Indicates whether the agent should be functional on this host

        Defaults to True which means the agent is unconditionally active. Agent subclasses
        can implement whatever tests are appropriate and return False if the agent should
        not be activated.

        :return: bool
        """
        return True

    def execute(self):
        action_name = self.request.action
        if action_name not in self._actions:
            raise UnknownRPCAction(action_name)

        action_method = self._actions[action_name]
        action_method(self)

    @classmethod
    def dispatch(cls, request, reply):
        """ Executes a request and returns the reply

            Overrides the parent dispatcher method because Agents can be active only in certain circumstances,
            so this method checks to see if the request should be honoured, and handles queries to check the
            activation status.

        :param request: RPC request object
        :param reply: RPC reply object
        :return:
        """
        try:
            agent = cls(
                request=request,
                reply=reply
            )
            agent.load_config()

            if isinstance(request, ExternalActivationRequest):
                reply.activate = agent.should_activate() is True

            elif isinstance(request, ExternalRPCRequest):
                if not agent.should_activate():
                    raise InactiveAgent()

                try:
                    agent.execute()
                except Exception as e:
                    raise RPCAborted(str(e))

        except (ChoriaExternalException, AgentException) as e:
            reply.fail(e.statuscode, '{0}: {1}'.format(e.description, str(e)))


def register_actions(cls):
    """ Registers all marked methods in the agent class

    :param cls: Agent Subclass of Agent containing methods decorated with @action
    """
    for name, method in cls.__dict__.items():
        if hasattr(method, "_register_action"):
            cls._actions[name] = method
    return cls


def action(method):
    """ Marks an agent instance method to be registered as an action

    :param method:
    :return:
    """

    method._register_action = True

    return method
