from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch

from busy import BusyApp
from busy.command.add_command import AddCommand
from busy.error import BusyError
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase
from busy.util import date_util

# Simple example of how to test command class behaviour directly without having
# to actually parse arguments: Mock the app operations.


class TestCommandAdd(BusyTestCase):

    def test_add(self):
        a = Mock()
        a.storage.get_collection.return_value \
            = o = TodoCollection([Item.from_markup('#a')])
        c = AddCommand(a, markup="jf")
        c.execute()
        self.assertEqual([str(x) for x in o], ['#a', 'jf'])
        self.assertTrue(o.changed)

    def test_add_omitted_markup(self):
        a = Mock()
        a.storage.get_collection.return_value = o = \
            TodoCollection([Item.from_markup('#a')])
        a.ui.get_text.return_value = 'f'
        c = AddCommand(a)
        c.execute()
        self.assertEqual([str(x) for x in o], ['#a', 'f'])
        self.assertTrue(o.changed)

    def test_from_app(self):
        tc = TodoCollection()
        pc = PlanCollection()
        dc = DoneCollection()
        a = BusyApp()
        a.storage = self.mock_storage(tc, pc, dc)
        with \
                self.patchout() as o, self.patcherr() as e, \
                self.patch_ttyin(''):
            a.parse_run('add', 'this')
        self.assertIn('this', tc[-1].markup)

    def test_add_with_when(self):
        tc = TodoCollection([Item.from_markup('#a')])
        pc = PlanCollection()
        a = Mock()
        a.storage.get_collection.side_effect = \
            lambda queue, state: tc if state == 'todo' else pc

        tomorrow = date_util.relative_date('tomorrow')
        c = AddCommand(a, markup="new task", when="tomorrow")
        c.execute()

        # Verify item was not added to todo collection
        self.assertEqual([str(x) for x in tc], ['#a'])

        # Verify item was added to plan collection with correct date
        self.assertEqual(len(pc), 1)
        self.assertEqual(pc[0].markup, "new task")
        self.assertEqual(pc[0].plan_date, tomorrow)
        self.assertEqual(pc[0].state, "plan")

    def test_add_with_invalid_when(self):
        tc = TodoCollection([Item.from_markup('#a')])
        pc = PlanCollection()
        a = Mock()
        a.storage.get_collection.side_effect = \
            lambda queue, state: tc if state == 'todo' else pc
        a.ui = Mock()

        c = AddCommand(a, markup="new task", when="invalid_date")
        c.execute()

        # Verify error was displayed
        a.ui.send.assert_called_once()

        # Verify item was added to todo collection instead of plan
        self.assertEqual(len(pc), 0)
        self.assertEqual(len(tc), 2)
        self.assertEqual(tc[1].markup, "new task")
        self.assertEqual(tc[1].state, "todo")
