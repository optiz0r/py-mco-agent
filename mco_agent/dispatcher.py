from __future__ import print_function

import logging
import os
import sys

from mco_agent.agent import Agent
from mco_agent.exceptions import ImproperlyConfigured, InactiveAgent, RPCAborted, AgentException
from mco_agent.protocol import ExternalRPCRequest, ExternalActivationRequest, ProtocolMessage


def dispatch(agent_cls):
    """ Processes an agent, parsing a request from stdin and marshalling the response back to stdout

    If agent is specified, bypasses plugin discovery and directly runs the action on the agent

    :param agent_cls: Agent Subclass of Agent which implements actions
    :return:
    """
    setup_logger(enable_debug=os.environ.get('CHORIA_EXTERNAL_DEBUG', '0'))

    protocol_name = os.environ.get('CHORIA_EXTERNAL_PROTOCOL', None)
    if not protocol_name:
        print("Unknown protocol", file=sys.stderr)
        exit(1)

    protocol = ProtocolMessage.get_protocol(protocol_name)
    reply = protocol.create_reply()

    try:
        if not issubclass(agent_cls, Agent):
            raise ImproperlyConfigured("Object {0} is not an Agent subclass".format(agent_cls.__class__.__name__))

        request = read_request(protocol, os.environ.get('CHORIA_EXTERNAL_REQUEST', None))

        agent = agent_cls(
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
                agent.run()
            except Exception as e:
                raise RPCAborted(str(e))

    except AgentException as e:
        reply.fail(e.statuscode, '{0}: {1}'.format(e.description, str(e)))

    write_reply(os.environ.get('CHORIA_EXTERNAL_REPLY', None), reply)

    if not reply.successful:
        exit(1)


def setup_logger(enable_debug=False):
    """ Configures logging for the agent

    By default, info logging is sent to stdout (displayed on request),
    warning and errors are sent to stdout (displayed always).

    To minimise output from other libraries, logging is disabled for all but
    the mcorpc hierarchy.

    Agents should log to 'mcorpc.agentname'
    """
    class InfoFilter(logging.Filter):
        """ Filters out events more serious than INFO so that only low-severity messages are recordsd
        """
        def filter(self, rec):
            return rec.levelno <= logging.INFO

    # Disable all logging from other libraries by default
    root_logger = logging.getLogger('.')
    root_logger.setLevel(100)

    logger = logging.getLogger('mcorpc')
    logger.setLevel(logging.DEBUG)

    info = logging.StreamHandler(sys.stdout)
    info.addFilter(InfoFilter())
    if enable_debug != '0':
        info.setLevel(logging.DEBUG)
    else:
        info.setLevel(logging.INFO)

    warn = logging.StreamHandler(sys.stderr)
    warn.setLevel(logging.WARNING)

    root_logger.addHandler(info)
    root_logger.addHandler(warn)


def read_request(protocol, request_file):
    """ Reads in the request

    Supports:
    - Reading request from a file specified by command line argument
    - Reading request from a file specified by environment variable
    - Reading request from stdin

    :param protocol: ProtocolMessage
    :param request_file:
    :return:
    """
    if request_file:
        with open(request_file, 'r') as fp:
            request_data = fp.read()
    else:
        request_data = sys.stdin.read()

    request = protocol.from_json(request_data)

    return request


def write_reply(reply_file, reply):
    if reply_file:
        with open(reply_file, 'w') as fp:
            fp.write(reply.to_json())
    else:
        print(reply.to_json())
