import mock
import unittest

from mco_agent.dispatcher import read_request, write_reply


class TestDispatcher(unittest.TestCase):

    @mock.patch('mco_agent.dispatcher.open')
    def test_read_request_file(self, mock_open):
        request_file = '/var/spool/choria/123.json'
        expected_request = {'protocol': '123', 'agent': 'abc'}

        protocol = mock.Mock()
        protocol.from_json.return_value = expected_request

        actual_value = read_request(protocol, request_file)

        mock_open.assert_called_once_with(request_file, 'r')
        self.assertEqual(expected_request, actual_value)

    @mock.patch('mco_agent.dispatcher.sys.stdin')
    def test_read_request_stdin(self, mock_stdin):
        expected_request = {'protocol': '123', 'agent': 'abc'}

        protocol = mock.Mock()
        protocol.from_json.return_value = expected_request

        actual_value = read_request(protocol, None)

        mock_stdin.read.assert_called_once_with()
        self.assertEqual(expected_request, actual_value)

    @mock.patch('mco_agent.dispatcher.open')
    def test_write_reply_file(self, mock_open):
        reply_file = '/var/spool/choria/123.json'
        expected_value = '{"statuscode": 0, "statusmsg": "", "data": "", "disableresponse": false}'

        reply = mock.Mock()
        reply.to_json.return_value = expected_value

        mock_fp = mock.Mock()
        mock_open.return_value.__enter__.return_value = mock_fp

        write_reply(reply_file, reply)

        mock_open.assert_called_once_with(reply_file, 'w')
        mock_fp.write.assert_called_once_with(expected_value)

    @mock.patch('mco_agent.dispatcher.print')
    def test_write_reply_print(self, mock_print):
        expected_value = '{"statuscode": 0, "statusmsg": "", "data": "", "disableresponse": false}'

        reply = mock.Mock()
        reply.to_json.return_value = expected_value

        write_reply(None, reply)

        mock_print.assert_called_once_with(expected_value)
