import os
import sys

from mco_agent.agent import Agent
from mco_agent.exceptions import InvalidRequest, ImproperlyConfigured, InactiveAgent
from mco_agent.protocol import RequestHeader, Reply


def dispatch(agent_cls):
    """ Processes an agent, parsing a request from stdin and marshalling the response back to stdout

    If agent is specified, bypasses plugin discovery and directly runs the action on the agent

    :param agent_cls: Agent Subclass of Agent which implements actions
    :return:
    """

    reply = Reply()
    try:
        if not issubclass(agent_cls, Agent):
            raise ImproperlyConfigured("Object {0} is not an Agent subclass".format(agent_cls.__class__.__name__))

        if not agent_cls.should_activate():
            raise InactiveAgent()

        # To aid in testing, allow reading input from a file instead of stdin
        if 'MCO_AGENT_REQUEST' in os.environ:
            with open(os.environ['MCO_AGENT_REQUEST'], 'r') as fp:
                request_data = fp.read()
        else:
            request_data = sys.stdin.read()

        request = RequestHeader.from_json(request_data)

        agent = agent_cls(
            request=request.body,
            reply=reply
        )

        try:
            agent.run()
        except Exception as e:
            reply.fail(1, 'Failed to run action: {0}'.format(str(e)))

    except InvalidRequest as e:
        reply.fail(1, 'Invalid request: {0}'.format(str(e)))

    except InactiveAgent:
        reply.fail(1, 'Agent is not active on this host')

    except ImproperlyConfigured:
        reply.fail(1, 'Invalid agent')

    print(reply.to_json())

    if reply.statuscode != 0:
        exit(1)