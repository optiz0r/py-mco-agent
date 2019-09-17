import mock
import unittest

from mco_agent.config import AgentConfig


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.agent = AgentConfig('testagent')
        self.config_file = '/etc/puppetlabs/mcollective/plugin.d/testagent.cfg'

    def test_constructor(self):
        self.assertEqual('testagent', self.agent.agent_name)
        self.assertEqual(self.config_file, self.agent.config_file)

    @mock.patch('mco_agent.config.os.path.exists')
    def test_config_exists(self, mock_path_exists):
        mock_path_exists.side_effect = [True, False]
        self.assertTrue(self.agent.config_exists())
        mock_path_exists.assert_called_with(self.config_file)

        self.agent.config_file = '/tmp/fake/testagent.cfg'
        self.assertFalse(self.agent.config_exists())
        mock_path_exists.assert_called_with('/tmp/fake/testagent.cfg')

    def test_read_missing_config_file(self):
        self.agent.config_exists = lambda: False
        self.assertEqual(None, self.agent.read_config())

    @mock.patch('mco_agent.config.open')
    def test_read_existing_config_file(self, mock_open):
        expected_value = ['#comment', 'foo=bar']

        mock_fp = mock.Mock()
        mock_open.return_value.__enter__.return_value = mock_fp
        mock_fp.readlines.return_value = expected_value

        self.agent.config_exists = lambda: True
        self.agent.parse_config = mock.Mock()

        self.agent.read_config()

        # noinspection PyUnresolvedReferences
        self.agent.parse_config.assert_called_once_with(expected_value)

    def test_parse_config(self):
        contents = [
            '#comment\n',
            'invalid\n',
            'key=value\n',
            ' whitespaced_key = value\n',
            'other_key=value with trailing whitespace \n',
        ]

        config = AgentConfig.parse_config(contents)

        self.assertEqual(3, len(config.keys()))
        self.assertIn('key', config)
        self.assertIn('whitespaced_key', config)
        self.assertIn('other_key', config)
        self.assertEqual('value', config['key'])
        self.assertEqual('value', config['whitespaced_key'])
        self.assertEqual('value with trailing whitespace ', config['other_key'])

    def test_operators(self):
        self.agent.config = {'key': 'value', 'other_key': 'other_value'}

        self.assertIn('key', self.agent)
        self.assertNotIn('invalid_key', self.agent)
        self.assertEqual('value', self.agent['key'])
        self.assertEqual('value', self.agent.get('key'))
        self.assertEqual(None, self.agent.get('invalid_key'))
        self.assertEqual(123, self.agent.get('invalid_key', 123))
