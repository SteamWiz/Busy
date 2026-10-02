from unittest import TestCase
from unittest.mock import Mock

from busy.command import QueueCommand
from busy.test_case import BusyTestCase


class TestCommand(BusyTestCase):

    def test_queue_command_execute(self):
        c = QueueCommand(root=Mock())
        c._root = Mock()
        c.execute = lambda: 'a'
        n = Mock()
        n.queue = ['q']
        c._namespace = n
        r = c.execute()
        self.assertEqual(r, 'a')
