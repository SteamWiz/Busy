from random import seed
from unittest import TestCase
from unittest.mock import Mock, patch

from busy.command.drop_and_pop_command import DropCommand
from busy.command.drop_and_pop_command import PickCommand
from busy.command.drop_and_pop_command import Pop1Command
from busy.command.drop_and_pop_command import PopCommand
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandDropAndPop(BusyTestCase):

    def test_drop(self):
        o = TodoCollection(
            [Item.from_markup('#a'),
             Item.from_markup('#b'),
             Item.from_markup('#c')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = DropCommand(s)
        c.execute()
        self.assertEqual([str(x) for x in o], ['#b', '#c', '#a'])
        self.assertTrue(o.changed)

    def test_drop_respond_nothing(self):
        o = TodoCollection()
        s = Mock()
        s.storage.get_collection.return_value = o
        c = DropCommand(s)
        c.execute()
        self.assertEqual(c.status, None)

    def test_pop(self):
        o = TodoCollection(
            [Item.from_markup('#a'),
             Item.from_markup('#b'),
             Item.from_markup('#c')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = PopCommand(s)
        c.execute()
        self.assertEqual([str(x) for x in o], ['#c', '#a', '#b'])
        # self.assertTrue(o.changed)

    def test_pick(self):
        o = TodoCollection(
            [Item.from_markup('#a'),
             Item.from_markup('#b'),
             Item.from_markup('#c')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = PickCommand(s, filter=['b', 'c'])
        seed(1)
        c.execute()
        self.assertEqual([str(x) for x in o], ['#b', '#a', '#c'])

    def test_pick_output(self):
        o = TodoCollection(
            [Item.from_markup('#a'),
             Item.from_markup('#b'),
             Item.from_markup('#c')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = PickCommand(s, filter=['b', 'c'])
        o = c.execute()
        self.assertEqual(None, o)

    def test_pop_again(self):
        o = TodoCollection(
            [Item.from_markup('#a'),
             Item.from_markup('x #b'),
             Item.from_markup('y #b')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = PopCommand(s, filter=['b'])
        c.execute()
        self.assertEqual([str(x) for x in o], ['x #b', 'y #b', '#a'])

    def test_drop_again(self):
        o = TodoCollection(
            [Item.from_markup('v #a'),
             Item.from_markup('x #a'),
             Item.from_markup('y #b')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = DropCommand(s, filter=['a'])
        c.execute()
        self.assertEqual([str(x) for x in o], ['y #b', 'v #a', 'x #a'])

    def test_pick_whole_collection(self):
        o = TodoCollection(
            [Item.from_markup('#a'),
             Item.from_markup('#b'),
             Item.from_markup('#c'),
             Item.from_markup('#d')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = PickCommand(s)
        seed(1)
        c.execute()
        self.assertEqual([str(x) for x in o], ['#b', '#a', '#c', '#d'])

    def test_pop1(self):
        o = TodoCollection(
            [Item.from_markup('#a'),
             Item.from_markup('#b'),
             Item.from_markup('#c')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = Pop1Command(s, filter=['b', 'c'])
        c.execute()
        self.assertEqual([str(x) for x in o], ['#b', '#a', '#c'])

    def test_pop1_default_filter(self):
        o = TodoCollection(
            [Item.from_markup('#a'),
             Item.from_markup('#b'),
             Item.from_markup('#c')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = Pop1Command(s)
        c.execute()
        self.assertEqual([str(x) for x in o], ['#a', '#b', '#c'])

    def test_pop1_output(self):
        o = TodoCollection(
            [Item.from_markup('#a'),
             Item.from_markup('#b'),
             Item.from_markup('#c')])
        s = Mock()
        s.storage.get_collection.return_value = o
        c = Pop1Command(s, filter=['b', 'c'])
        result = c.execute()
        self.assertEqual(None, result)
