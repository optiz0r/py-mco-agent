from mco_agent.exceptions import UnknownRPCAction


class Agent:

    _actions = {}

    def __init__(self, request, reply):
        self.request = request
        self.reply = reply

    # noinspection PyUnusedLocal
    @staticmethod
    def should_activate():
        """ Indicates whether the agent should be functional on this host

        Defaults to True which means the agent is unconditionally active. Agent subclasses
        can implement whatever tests are appropriate and return False if the agent should
        not be activated.

        :param self:
        :return: bool
        """
        return True

    def run(self):
        action_name = self.request.action
        if action_name not in self._actions:
            raise UnknownRPCAction(action_name)

        action_method = self._actions[action_name]
        action_method(self)


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
