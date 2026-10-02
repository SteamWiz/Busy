from datetime import date
from unittest import TestCase
from unittest.mock import Mock
from wizlib.config_handler import ConfigHandler

from busy import BusyApp
from busy.command.list_command import ListCommand
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestValue(BusyTestCase):

    def test_multiplier_config(self):
        config = {'busy': {'multiplier': 1.6}}
        a = BusyApp(config=config)
        m = a.config.get('busy-multiplier')
        self.assertEqual(1.6, m)

    def test_item_multiplies(self):
        i = Item.from_markup('a !e10')
        self.assertEqual(10, i.elapsed_minutes)

    def test_list_value(self):
        config = {'busy': {'multiplier': 1.5}}
        a = BusyApp(config=config)
        i = Item.from_markup('b !e30', state='done',
                             done_date=date(2023, 12, 31))
        d = DoneCollection([i])
        a.storage = self.mock_storage(TodoCollection(), PlanCollection(), d)
        c = ListCommand(a, collection_state='done')
        c.execute()
        self.assertEqual(c.status, '1 item (0h45m)')
