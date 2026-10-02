from unittest.mock import Mock
from busy.command.view_command import ViewCommand
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestMoreFilters(BusyTestCase):

    def test_data_val(self):
        d = TodoCollection()
        d.append(Item.from_markup('c %x6'))
        d.append(Item.from_markup('d %x4'))
        s = self.mock_storage(d, PlanCollection(), DoneCollection())
        a = Mock()
        a.storage = s
        c = ViewCommand(
            a, filter=['val:x6'])
        n = c.execute()
        self.assertEqual(len(n), 1)
        self.assertEqual(n.splitlines()[0], 'c')

    def test_data_val(self):
        d = TodoCollection()
        d.append(Item.from_markup('c %x6'))
        d.append(Item.from_markup('d %x4'))
        s = self.mock_storage(d, PlanCollection(), DoneCollection())
        a = Mock()
        a.storage = s
        c = ViewCommand(
            a, filter=['val:x6'])
        n = c.execute()
        self.assertEqual(len(n), 1)
        self.assertEqual(n.splitlines()[0], 'c')

    def test_data_val_multi(self):
        d = TodoCollection()
        d.append(Item.from_markup('c %x6 %y2'))
        d.append(Item.from_markup('d %x4 %y2'))
        s = self.mock_storage(d, PlanCollection(), DoneCollection())
        a = Mock()
        a.storage = s
        c = ViewCommand(
            a, filter=['val:x6', 'val:y2'])
        n = c.execute()
        self.assertEqual(len(n), 1)
        self.assertEqual(n.splitlines()[0], 'c')

    def test_grep_filter_match(self):
        d = TodoCollection()
        d.append(Item.from_markup('Reconcile Chase Visa'))
        d.append(Item.from_markup('Buy groceries'))
        s = self.mock_storage(d, PlanCollection(), DoneCollection())
        a = Mock()
        a.storage = s
        c = ViewCommand(a, filter=['grep:reconcile'])
        n = c.execute()
        self.assertEqual(n.splitlines(), ['Reconcile Chase Visa'])

    def test_grep_filter_case_insensitive(self):
        d = TodoCollection()
        d.append(Item.from_markup('Reconcile Chase Visa'))
        d.append(Item.from_markup('Buy groceries'))
        s = self.mock_storage(d, PlanCollection(), DoneCollection())
        a = Mock()
        a.storage = s
        c = ViewCommand(a, filter=['grep:RECONCILE'])
        n = c.execute()
        self.assertEqual(n.splitlines(), ['Reconcile Chase Visa'])

    def test_grep_filter_no_match(self):
        d = TodoCollection()
        d.append(Item.from_markup('Buy groceries'))
        d.append(Item.from_markup('Pay rent'))
        s = self.mock_storage(d, PlanCollection(), DoneCollection())
        a = Mock()
        a.storage = s
        c = ViewCommand(a, filter=['grep:reconcile'])
        n = c.execute()
        self.assertIsNone(n)
