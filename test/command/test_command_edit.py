from unittest import TestCase
from unittest.mock import Mock, patch

from busy.command.edit_command import EditOneItemCommand
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
