from datetime import date
from unittest import TestCase
from unittest.mock import Mock, patch

from busy import BusyApp
from busy.command.activate_command import ActivateCommand
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandActivate(BusyTestCase):

    def test_activate(self):
        o = TodoCollection([Item.from_markup('a'), Item.from_markup('b')])
        p = PlanCollection([
            Item.from_markup('c', state='plan', plan_date=date(2023, 6, 7)),
            Item.from_markup('d', state='plan', plan_date=date(2023, 6, 8))])
        a = Mock()
        a.storage = self.mock_storage(o, p)
        c = ActivateCommand(a, yes=True, queue_name='r')
        with patch('busy.util.date_util.today', lambda: date(2023, 6, 7)):
            c.execute()
        self.assertEqual([str(x) for x in o], ['a', 'b', 'c'])
        self.assertEqual([str(x) for x in p], ['d'])
        self.assertTrue(o.changed)
        self.assertTrue(p.changed)
        self.assertEqual(c.status, "a")

    def test_filter(self):
        o = TodoCollection([Item.from_markup('a')])
        p = PlanCollection([
            Item.from_markup('c', state='plan', plan_date=date(2023, 6, 7)),
            Item.from_markup('d', state='plan', plan_date=date(2023, 6, 8)),
            Item.from_markup('e', state='plan', plan_date=date(2023, 6, 8))])
        a = Mock()
        a.storage = self.mock_storage(o, p)
        c = ActivateCommand(a, yes=True, filter=[1, '3'], queue_name='s')
        with patch('busy.util.date_util.today', lambda: date(2023, 6, 7)):
            c.execute()
        self.assertEqual([str(x) for x in o], ['a', 'c', 'e'])
        self.assertEqual([str(x) for x in p], ['d'])
        self.assertTrue(o.changed)
        self.assertTrue(p.changed)
        self.assertEqual(c.status, "a")

    def test_none(self):
        o = TodoCollection([Item.from_markup('a')])
        p = PlanCollection([Item.from_markup('c', state='plan',
                                             plan_date=date(2023, 6, 9)),
                            Item.from_markup('e', state='plan',
                                             plan_date=date(2023, 6, 8))])
        a = Mock()
        # a = BusyApp()
        a.storage = self.mock_storage(o, p)
        c = ActivateCommand(a, queue_name='n', yes=True)
        with self.patchday(2023, 6, 7):
            c.execute()
        self.assertEqual([str(x) for x in o], ['a'])
        self.assertEqual([str(x) for x in p], ['c', 'e'])
        self.assertEqual(c.status, "a")
