from unittest import TestCase
from unittest.mock import Mock

from busy.command.tags_command import TagsCommand
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandTags(BusyTestCase):

    def test_tags(self):
        a = Mock()
        a.storage.get_collection.return_value = o = TodoCollection(
            [Item.from_markup('a #z'), Item.from_markup('c #d #e')])
        c = TagsCommand(a)
        n = c.execute()
        self.assertEqual(n, 'd\ne\nz')
