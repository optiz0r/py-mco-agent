class AgentException(Exception):
    """ Base exception"""
    description = 'Unknown error'
    statuscode = 5

    def __str__(self):
        return '{0}: {1}'.format(self.description, ' '.join(self.args))


class InactiveAgent(AgentException):
    description = "Agent is not activated"
