from datetime import date
from unittest import TestCase
from unittest.mock import Mock

from busy import BusyApp
from busy.command.list_command import ListCommand
from busy.error import BusyError
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestStateOption(BusyTestCase):

    def test_state(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        d = DoneCollection(
            [Item.from_markup('d', state='done', done_date=date(2023, 1, 1))])
        p = PlanCollection([
            Item.from_markup('e', state='plan', plan_date=date(2023, 6, 7)),
            Item.from_markup('f', state='plan', plan_date=date(2023, 6, 8))])
        a = BusyApp()
        a.storage = self.mock_storage(o, p, d)
        with self.patchout() as o, self.patcherr():
            a.parse_run('simple', '--state', 'done')
        o.seek(0)
        self.assertEqual('d', o.read())

    def test_multi_states_fails_with_index_filter(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        d = DoneCollection(
            [Item.from_markup('d', state='done', done_date=date(2023, 1, 1))])
        p = PlanCollection([
            Item.from_markup('e', state='plan', plan_date=date(2023, 6, 7)),
            Item.from_markup('f', state='plan', plan_date=date(2023, 6, 8))])
        a = BusyApp()
        a.storage = self.mock_storage(o, p, d)
        with self.patchout(), self.patcherr(), \
                self.assertRaises(BusyError):
            a.parse_run('view', '1-', '--state', 'multi')

    def test_multi_states_returns_all_with_no_filter(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        d = DoneCollection(
            [Item.from_markup('d', state='done', done_date=date(2023, 1, 1))])
        p = PlanCollection([
            Item.from_markup('e', state='plan', plan_date=date(2023, 6, 7)),
            Item.from_markup('f', state='plan', plan_date=date(2023, 6, 8))])
        a = BusyApp()
        a.storage = self.mock_storage(o, p, d)
        with self.patchout() as o, self.patcherr():
            a.parse_run('view', '--state', 'multi')
        o.seek(0)
        result = o.readlines()
        self.assertEqual(6, len(result))

    def test_multi_states_with_filter(self):
        a, b, c = Item.from_markup('a #x'), Item.from_markup(
            'b'), Item.from_markup('c #x')
        o = TodoCollection([a, b, c])
        d = DoneCollection(
            [Item.from_markup('d #x', state='done',
                              done_date=date(2023, 1, 1))])
        p = PlanCollection(
            [Item.from_markup(
                'e', state='plan', plan_date=date(2023, 6, 7)),
             Item.from_markup(
                 'f #x', state='plan', plan_date=date(2023, 6, 8))])
        a = BusyApp()
        a.storage = self.mock_storage(o, p, d)
        with self.patchout() as o, self.patcherr():
            a.parse_run('view', 'x', '--state', 'multi')
        o.seek(0)
        result = o.readlines()
        self.assertEqual(4, len(result))
