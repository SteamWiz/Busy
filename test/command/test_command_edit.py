from datetime import date
from io import StringIO
from unittest import TestCase
from unittest.mock import Mock, patch

from busy.command.edit_command import EditOneItemCommand
from busy.error import BusyError
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandEdit(BusyTestCase):

    def test_edit(self):
        o = TodoCollection([Item.from_markup('a')])
        a = Mock()
        a.storage.get_collection.return_value = o
        with patch('busy.util.edit.edit_text', lambda s, i: 'b\n'):
            c = EditOneItemCommand(a, queue_name='n')
            c.execute()
        self.assertEqual([str(x) for x in o], ['b'])
        self.assertTrue(o.changed)
        self.assertEqual(c.status, 'b')

    def test_edit_plan_invalid_date(self):
        o = PlanCollection([Item.from_markup(
            'a', state='plan', plan_date='2026-01-01')])
        a = Mock()
        a.storage.get_collection.return_value = o
        with patch('busy.util.edit.edit_text',
                   lambda s, i: 'notadate|foo\n'):
            c = EditOneItemCommand(a, queue_name='n', state='plan')
            with self.assertRaises(BusyError):
                c.execute()
        self.assertEqual([str(x) for x in o], ['a'])
        self.assertEqual(o[0].plan_date, date(2026, 1, 1))
        self.assertFalse(o.changed)
        a.storage.save.assert_not_called()

    def test_edit_plan_valid_date(self):
        o = PlanCollection([Item.from_markup(
            'a', state='plan', plan_date='2026-01-01')])
        a = Mock()
        a.storage.get_collection.return_value = o
        with patch('busy.util.edit.edit_text',
                   lambda s, i: '2026-02-03|foo\n'):
            c = EditOneItemCommand(a, queue_name='n', state='plan')
            c.execute()
        self.assertEqual([str(x) for x in o], ['foo'])
        self.assertEqual(o[0].plan_date, date(2026, 2, 3))
        self.assertTrue(o.changed)

    def test_load_plan_invalid_date_from_storage(self):
        o = PlanCollection()
        o.read_items(StringIO('notadate|foo\n'), from_storage=True)
        self.assertEqual([str(x) for x in o], ['foo'])
        self.assertIsNone(o[0].plan_date)
