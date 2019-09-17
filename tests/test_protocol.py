import json
import unittest

from mco_agent.exceptions import InvalidRPCData
from mco_agent.protocol import ProtocolMessage, ExternalRequestHeader, RequestBody, ExternalActivationCheckHeader, \
    ActivationReply, ActionReply


class TestProtocolMessage(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_valid_protocol(self):
        ProtocolMessage._protocols['foo'] = 'protocol object'
        self.assertEqual('protocol object', ProtocolMessage.get_protocol('foo'))

    def test_get_invalid_protocol(self):
        with self.assertRaises(InvalidRPCData) as cm:
            ProtocolMessage.get_protocol('improper_protocol')

        exc = cm.exception
        self.assertEqual('Unsupported message protocol improper_protocol', exc.args[0])

    def test_create_reply_for_base_class(self):
        with self.assertRaises(InvalidRPCData) as cm:
            ProtocolMessage.create_reply()

        exc = cm.exception
        self.assertEqual('Method should only be called for a ProtocolMessage subclass', exc.args[0])

    def test_register_protocol(self):
        protocol_name = 'choria:mcorpc:test:1'
        self.assertNotIn(protocol_name, ProtocolMessage._protocols)

        class TestProtocol(ProtocolMessage):
            _protocol = protocol_name

        ProtocolMessage.register_protocol()(TestProtocol)

        self.assertIn(protocol_name, ProtocolMessage._protocols)

    def test_parse_valid_external_request(self):
        request = ExternalRequestHeader.from_dict({
            'protocol': 'choria:mcorpc:external_request:1',
            'agent': 'testagent',
            'action': 'testaction',
            'requestid': '123',
            'senderid': '123',
            'callerid': '123',
            'collective': 'mcollective',
            'ttl': 30,
            'msgtime': 123,
            'body': {
                'agent': 'testagent',
                'action': 'testaction',
                'data': {},
                'caller': 'testuser.mcollective',
            }
        })

        self.assertIsInstance(request, ExternalRequestHeader)
        self.assertIsInstance(request.body, RequestBody)
        self.assertEqual('testagent', request.agent)
        self.assertEqual('testaction', request.action)
        # noinspection PyUnresolvedReferences
        self.assertEqual('testuser.mcollective', request.body.caller)

    def test_parse_invalid_external_request(self):
        with self.assertRaises(InvalidRPCData):
            ExternalRequestHeader.from_dict({
                'invalid_dict': True,
            })

        with self.assertRaises(InvalidRPCData):
            ExternalRequestHeader.from_dict({
                'protocol': 'choria:mcorpc:external_request:1',
                'agent': 'testagent',
                'action': 'testaction',
                'requestid': '123',
                'senderid': '123',
                'callerid': '123',
                'collective': 'mcollective',
                'ttl': 30,
                'msgtime': 123,
                'body': {
                    'agent': 'testagent',
                    'action': 'testaction',
                    'data': {},
                    'caller': 'testuser.mcollective',
                },
                'extra_field': True,
            })

    def test_parse_valid_activation_check(self):
        request = ExternalActivationCheckHeader.from_dict({
            'protocol': 'choria:mcorpc:external_request:1',
            'agent': 'testagent',
        })

        self.assertIsInstance(request, ExternalActivationCheckHeader)
        self.assertEqual('testagent', request.agent)

    def test_activation_reply_mark_failure(self):
        reply = ActivationReply()
        self.assertTrue(reply.successful())
        self.assertTrue(reply.activate)
        reply.fail()
        self.assertFalse(reply.activate)

    def test_activation_reply_serialisation(self):
        reply = ActivationReply()
        self.assertEqual('{"activate": true}', reply.to_json())

    def test_activation_reply_inactive_serialisation(self):
        reply = ActivationReply()
        reply.activate = False
        self.assertEqual('{"activate": false}', reply.to_json())

    def test_action_reply_reply_serialisation(self):
        reply = ActionReply()
        result = json.loads(reply.to_json())
        self.assertEqual(4, len(result.keys()))
        self.assertIn('statuscode', result)
        self.assertIn('statusmsg', result)
        self.assertIn('data', result)
        self.assertIn('disableresponse', result)

    def test_action_reply_mark_failure(self):
        reply = ActionReply()
        self.assertEqual(0, reply.statuscode)
        self.assertEqual('', reply.statusmsg)
        self.assertTrue(reply.successful())

        reply.fail(1, 'test')
        self.assertEqual(1, reply.statuscode)
        self.assertEqual('test', reply.statusmsg)
        self.assertFalse(reply.successful())
