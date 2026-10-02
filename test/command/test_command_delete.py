from unittest import TestCase
from unittest.mock import Mock

from busy.command.delete_command import DeleteCommand
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandDelete(BusyTestCase):

    def test_delete_no_filter(self):
        o = TodoCollection([Item.from_markup('a'), Item.from_markup('b')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = DeleteCommand(s)
        c.yes = True
        c.execute()
        self.assertEqual([str(x) for x in o], ['b'])
        self.assertTrue(o.changed)
        self.assertEqual(c.status, "b")

    def test_delete_multiple(self):
        o = TodoCollection([Item.from_markup(i) for i in 'abcde'])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = DeleteCommand(s, filter=[2, 4])
        c.yes = True
        c.execute()
        self.assertEqual([str(x) for x in o], ['a', 'c', 'e'])
        self.assertTrue(o.changed)
        self.assertEqual(c.status, "a")

    # def test_not_confirmed(self):
    #     o = TodoCollection([Item.from_markup('a'), Item.from_markup('b')])
    #     s = Mock()
    #     s.storage.get_collection.return_value = o
    #     c = DeleteCommand(s)
    #     c.yes = False
    #     c.execute()
    #     self.assertEqual(c.status, "Delete command canceled")
    #     self.assertEqual([str(x) for x in o], ['a', 'b'])

    # def test_handle_vals_confirms(self):
    #     o = TodoCollection([Item.from_markup('a'), Item.from_markup('b')])
    #     s = Mock()
    #     s.storage.get_collection.return_value = o
    #     s.ui = u = Mock()
    #     c = DeleteCommand(s)
    #     c.handle_vals()
    #     u.get_option.assert_called_with(intro="Delete 1 item?", default="ok")
