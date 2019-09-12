import os
import sys

from mco_agent.agent import Agent
from mco_agent.exceptions import InvalidRequest, ImproperlyConfigured, InactiveAgent, UnknownProtocol
from mco_agent.protocol import ExternalRequestHeader, ExternalActivationCheckHeader, ProtocolMessage, Reply


def dispatch(agent_cls):
    """ Processes an agent, parsing a request from stdin and marshalling the response back to stdout

    If agent is specified, bypasses plugin discovery and directly runs the action on the agent

    :param agent_cls: Agent Subclass of Agent which implements actions
    :return:
    """

    protocol_name = os.environ.get('CHORIA_EXTERNAL_PROTOCOL', None)
    if not protocol_name:
        print("Unknown protocol", file=sys.stderr)
        exit(1)

    protocol = ProtocolMessage.get_protocol(protocol_name)
    reply = protocol.create_reply()

    try:
        if not issubclass(agent_cls, Agent):
            raise ImproperlyConfigured("Object {0} is not an Agent subclass".format(agent_cls.__class__.__name__))

        if 'CHORIA_EXTERNAL_REQUEST' in os.environ:
            with open(os.environ['CHORIA_EXTERNAL_REQUEST'], 'r') as fp:
                request_data = fp.read()
        else:
            request_data = sys.stdin.read()

        request = protocol.from_json(request_data)

        if isinstance(request, ExternalActivationCheckHeader):
            agent = agent_cls(
                request=None,
                reply=reply
            )
            reply.activate = agent.should_activate() is True

        elif isinstance(request, ExternalRequestHeader):
            agent = agent_cls(
                request=request.body,
                reply=reply
            )

            if not agent.should_activate():
                raise InactiveAgent()

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

    output_file = os.environ.get('CHORIA_EXTERNAL_REPLY', None)
    if output_file:
        with open(output_file, 'w') as fp:
            fp.write(reply.to_json())
    else:
        print(reply.to_json())

    if not reply.successful:
        exit(1)