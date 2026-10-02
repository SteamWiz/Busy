from datetime import date
from unittest import TestCase
from unittest.mock import Mock

from busy.command.list_command import ListCommand
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandList(BusyTestCase):

    def test_list(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = ListCommand(s)
        n = c.execute()
        self.assertEqual(n.splitlines()[0], '     1  a')

    def test_list_none(self):
        o = TodoCollection()
        s = Mock()
        s.storage.get_collection.return_value = o
        c = ListCommand(s)
        n = c.execute()
        self.assertIsNone(n)
        self.assertEqual(c.status, "")

    def test_min_done_date(self):
        d = DoneCollection()
        d.append(
            Item.from_markup(
                'c', state='done', done_date=date(2024, 6, 1)))
        d.append(
            Item.from_markup(
                'd', state='done', done_date=date(2024, 7, 1)))
        s = self.mock_storage(TodoCollection(), PlanCollection(), d)
        a = Mock()
        a.storage = s
        c = ListCommand(
            a, filter=['donemin:2024-07-01'], collection_state='done')
        n = c.execute()
        self.assertEqual(n.splitlines()[0], '     2  2024-07-01  d')

    def test_max_done_date(self):
        d = DoneCollection()
        d.append(
            Item.from_markup(
                'c', state='done', done_date=date(2024, 6, 1)))
        d.append(
            Item.from_markup(
                'd', state='done', done_date=date(2024, 7, 1)))
        s = self.mock_storage(TodoCollection(), PlanCollection(), d)
        a = Mock()
        a.storage = s
        c = ListCommand(
            a, filter=['donemax:2024-06-15'], collection_state='done')
        n = c.execute()
        self.assertEqual(n, '     1  2024-06-01  c')

    def test_min_and_max_done_date(self):
        d = DoneCollection()
        d.append(
            Item.from_markup(
                'c', state='done', done_date=date(2024, 6, 1)))
        d.append(
            Item.from_markup(
                'd', state='done', done_date=date(2024, 7, 1)))
        d.append(
            Item.from_markup(
                'e', state='done', done_date=date(2024, 8, 1)))
        s = self.mock_storage(TodoCollection(), PlanCollection(), d)
        a = Mock()
        a.storage = s
        c = ListCommand(a, filter=['donemax:2024-07-15',
                        'donemin:2024-06-15'], collection_state='done')
        n = c.execute()
        self.assertEqual(n, '     2  2024-07-01  d')

    def test_plan_date_filter(self):
        d = PlanCollection()
        d.append(
            Item.from_markup(
                'c', state='plan', plan_date=date(2024, 6, 1)))
        d.append(
            Item.from_markup(
                'd', state='plan', plan_date=date(2024, 7, 1)))
        d.append(
            Item.from_markup(
                'e', state='plan', plan_date=date(2024, 8, 1)))
        s = self.mock_storage(TodoCollection(), d, DoneCollection())
        a = Mock()
        a.storage = s
        c = ListCommand(a, filter=['planmax:2024-07-15',
                        'planmin:2024-06-15'], collection_state='plan')
        n = c.execute()
        self.assertEqual(n, '     2  2024-07-01  d')
