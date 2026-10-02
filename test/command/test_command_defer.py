from datetime import date

from unittest import TestCase
from unittest.mock import Mock, patch

from busy.command.defer_command import DeferCommand
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandDefer(BusyTestCase):

    def test_defer(self):
        o = TodoCollection([Item.from_markup('a'), Item.from_markup('b')])
        p = PlanCollection([
            Item.from_markup('c', state='plan', plan_date=date(2023, 6, 7)),
            Item.from_markup('d', state='plan', plan_date=date(2023, 6, 7))])
        a = Mock()
        a.storage = self.mock_storage(o, p)
        c = DeferCommand(a, when='tomorrow', yes=True)
        with patch('busy.util.date_util.today', lambda: date(2019, 2, 11)):
            c.execute()
        self.assertEqual([str(x) for x in o], ['b'])
        self.assertEqual([str(x) for x in p], ['c', 'd', 'a'])
        self.assertTrue(o.changed)
        self.assertTrue(p.changed)
        self.assertEqual(c.status, "b")

    def test_defer_respond_nothing(self):
        """Conform defer command doesn't fail if nothing to defer"""
        o = TodoCollection()
        p = PlanCollection([
            Item.from_markup('c', state='plan', plan_date=date(2023, 6, 7)),
            Item.from_markup('d', state='plan', plan_date=date(2023, 6, 7))])
        a = Mock()
        a.storage = self.mock_storage(o, p)
        c = DeferCommand(a)
        c.yes = True
        with patch('busy.util.date_util.today', lambda: date(2019, 2, 11)):
            c.execute()
        self.assertEqual(len(o), 0)
        self.assertEqual([str(x) for x in p], ['c', 'd'])
        self.assertFalse(o.changed)
        self.assertFalse(p.changed)
        self.assertEqual(c.status, "")

    def test_handle_vals_confirms(self):
        u = Mock()
        u.get_option.return_value = True
        u.get_text.return_value = 'tomorrow'
        o = TodoCollection([Item.from_markup('a'), Item.from_markup('b')])
        p = PlanCollection([
            Item.from_markup('c', state='plan', plan_date=date(2023, 6, 7)),
            Item.from_markup('d', state='plan', plan_date=date(2023, 6, 7))])
        s = Mock()
        s.storage = self.mock_storage(o, p)
        s.ui = u
        c = DeferCommand(s, when='tomorrow')
        with patch('busy.util.date_util.today', lambda: date(2023, 4, 30)):
            c.handle_vals()
        u.get_option.assert_called()

    def test_handle_vals_other(self):
        u = Mock()
        # u.get_chooser.return_value = Chooser()
        u.get_option.side_effect = [Mock(), True]
        u.get_text.return_value = '2'
        o = TodoCollection([Item.from_markup('a'), Item.from_markup('b')])
        p = PlanCollection([
            Item.from_markup('c', state='plan', plan_date=date(2023, 6, 7)),
            Item.from_markup('d', state='plan', plan_date=date(2023, 6, 7))])
        s = Mock()
        s.storage = self.mock_storage(o, p)
        s.ui = u
        c = DeferCommand(s)
        with patch('busy.util.date_util.today', lambda: date(2019, 2, 11)):
            c.handle_vals()
        u.get_text.assert_called()
