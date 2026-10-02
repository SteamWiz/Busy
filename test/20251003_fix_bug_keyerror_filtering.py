
from unittest.mock import Mock
from busy.command.view_command import ViewCommand
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestFixBugKeyErrorFiltering(BusyTestCase):

    def test_val_when_some_not_matching(self):
        d = TodoCollection()
        d.append(Item.from_markup('c %x6'))
        d.append(Item.from_markup('d %y4'))
        s = self.mock_storage(d, PlanCollection(), DoneCollection())
        a = Mock()
        a.storage = s
        c = ViewCommand(
            a, filter=['val:x6'])
        n = c.execute()
        self.assertEqual(len(n), 1)
        self.assertEqual(n.splitlines()[0], 'c')
