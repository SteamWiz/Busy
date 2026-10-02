from unittest import TestCase
from unittest.mock import Mock

from busy.command.describe_command import DescribeCommand
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandDescribe(BusyTestCase):

    def test_show(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = DescribeCommand(a)
        n = c.execute()
        self.assertEqual(n, 'a')

    def test_show_empty(self):
        o = TodoCollection()
        a = Mock()
        a.storage.get_collection.return_value = o
        c = DescribeCommand(a)
        n = c.execute()
        self.assertIsNone(n)
        self.assertEqual(c.status, "")

    def test_show_multiple(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = DescribeCommand(s, filter=[1, 3])
        n = c.execute()
        self.assertEqual(n.splitlines(), ['a', 'c'])
