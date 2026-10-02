from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock

from busy.command.queues_command import QueuesCommand
from busy.storage.file_storage import FileStorage
from busy.test_case import BusyTestCase


class TestCommandQueues(BusyTestCase):

    def test_queues(self):
        with TemporaryDirectory() as t:
            with open(f'{t}/tasks.todo.psv', 'w') as f1:
                f1.writelines(s+'\n' for s in 'ab')
            with open(f'{t}/foo.plan.psv', 'w') as f2:
                f2.write('2024-02-11|c\n')
            with open(f'{t}/foo.done.psv', 'w') as f3:
                f3.write('2021-02-14|d\n')
            a = Mock()
            a.storage = FileStorage(t)
            c = QueuesCommand(a)
            r = c.execute()
            self.assertEqual(r, 'foo\ntasks')
