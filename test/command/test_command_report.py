from datetime import date
from unittest import TestCase
from unittest.mock import Mock

from busy import BusyApp
from busy.command.view_command import ViewCommand
from busy.error import BusyError
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandReport(BusyTestCase):

    def test_static(self):
        a = Item.from_markup('a')
        o = TodoCollection([a])
        a = BusyApp()
        a.storage = self.mock_storage(o, PlanCollection(), DoneCollection())
        with self.patchout() as o:
            a.parse_run('report', '--line', '-')
        o.seek(0)
        self.assertEqual('-', o.read())

    def test_base(self):
        a = Item.from_markup('a')
        o = TodoCollection([a])
        a = BusyApp()
        a.storage = self.mock_storage(o, PlanCollection(), DoneCollection())
        with self.patchout() as o:
            a.parse_run('report', '--line', '- {{base}}')
        o.seek(0)
        self.assertEqual('- a', o.read())

    def test_multiple_items(self):
        a, b = Item.from_markup('a'), Item.from_markup('b')
        o = TodoCollection([a, b])
        a = BusyApp()
        a.storage = self.mock_storage(o, PlanCollection(), DoneCollection())
        with self.patchout() as o:
            a.parse_run('report', '--line', '- {{base}}')
        o.seek(0)
        self.assertEqual('- a\n- b', o.read())

    def test_with_filter(self):
        a, b = Item.from_markup('a'), Item.from_markup('b')
        o = TodoCollection([a, b])
        a = BusyApp()
        a.storage = self.mock_storage(o, PlanCollection(), DoneCollection())
        with self.patchout() as o:
            a.parse_run('report', '1', '--line', '- {{base}}')
        o.seek(0)
        self.assertEqual('- a', o.read())

    def test_val(self):
        a = Item.from_markup('a %x6')
        o = TodoCollection([a])
        a = BusyApp()
        a.storage = self.mock_storage(o, PlanCollection(), DoneCollection())
        with self.patchout() as o:
            a.parse_run('report', '1', '--line', "- {{val.x}}")
        o.seek(0)
        self.assertEqual('- 6', o.read())
