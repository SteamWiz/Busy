from datetime import date
from io import StringIO
import os
from busy import BusyApp

from unittest import TestCase
from unittest.mock import Mock, patch

from busy.command.done_command import DoneCommand
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandDone(BusyTestCase):

    def test_done(self):
        o = TodoCollection([Item.from_markup('a'), Item.from_markup('#b')])
        d = DoneCollection(
            [Item.from_markup('c', state='done', done_date=date(2023, 1, 1))])
        a = Mock()
        a.storage = self.mock_storage(o, PlanCollection(), d)
        c = DoneCommand(a, yes=True)
        with self.patchday(2023, 2, 11):
            c.execute()
        self.assertEqual([str(x) for x in o], ['#b'])
        self.assertEqual(d[-1].markup, 'a')
        self.assertEqual(d[-1].done_date, date(2023, 2, 11))
        self.assertTrue(o.changed)
        self.assertTrue(d.changed)

    def test_provided_timing(self):
        o = TodoCollection([Item.from_markup('a'), Item.from_markup('#b')])
        d = DoneCollection(
            [Item.from_markup('c', state='done', done_date=date(2023, 1, 1))])
        a = BusyApp()
        a.storage = self.mock_storage(o, p := PlanCollection(), d)
        with \
                self.patchday(2023, 2, 11), \
                self.patcherr() as t:
            a.parse_run('done', '--yes', '--defer', 'tomorrow')
            t.seek(0)
            r = t.read()
        self.assertEqual([str(x) for x in o], ['#b'])
        self.assertEqual(d[-1].markup, 'a')
        self.assertEqual(d[-1].done_date, date(2023, 2, 11))
        self.assertEqual(p[-1].markup, 'a')
        self.assertEqual(p[-1].plan_date, date(2023, 2, 12))
        self.assertTrue(o.changed)
        self.assertTrue(d.changed)
        self.assertTrue(p.changed)

    def test_confirmation(self):
        o = TodoCollection([Item.from_markup('a'), Item.from_markup('#b')])
        d = DoneCollection(
            [Item.from_markup('c', state='done', done_date=date(2023, 1, 1))])
        a = BusyApp()
        a.storage = self.mock_storage(o, p := PlanCollection(), d)
        with \
                self.patchday(2023, 2, 11), \
                self.patcherr() as t, \
                self.patch_ttyin('\n'):
            a.parse_run('done', '--defer', 'tomorrow')
            t.seek(0)
            r = t.read()
        self.assertEqual([str(x) for x in o], ['#b'])
        self.assertEqual(d[-1].markup, 'a')
        self.assertEqual(d[-1].done_date, date(2023, 2, 11))
        self.assertEqual(p[-1].markup, 'a')
        self.assertEqual(p[-1].plan_date, date(2023, 2, 12))
        self.assertTrue(o.changed)
        self.assertTrue(d.changed)
        self.assertTrue(p.changed)

    def test_confirmation_no_defer(self):
        o = TodoCollection([Item.from_markup('a'), Item.from_markup('#b')])
        p = PlanCollection()
        d = DoneCollection(
            [Item.from_markup('c', state='done', done_date=date(2023, 1, 1))])
        a = BusyApp()
        a.storage = self.mock_storage(o, p, d)
        with \
                self.patchday(2023, 2, 11), \
                self.patcherr() as t, \
                self.patch_ttyin('\n'):
            a.parse_run('done')
        self.assertEqual([str(x) for x in o], ['#b'])
        self.assertEqual(d[-1].markup, 'a')
        self.assertEqual(d[-1].done_date, date(2023, 2, 11))
        self.assertEqual(len(p), 0)
        self.assertTrue(o.changed)
        self.assertTrue(d.changed)
        self.assertIn('Done 1 item?', t.getvalue())
        self.assertIn('(c)ancel', t.getvalue())

    def test_defer_input(self):
        tc = TodoCollection([Item.from_markup('a'), Item.from_markup('#b')])
        pc = PlanCollection()
        dc = DoneCollection(
            [Item.from_markup('c', state='done', done_date=date(2023, 1, 1))])
        a = BusyApp()
        a.storage = self.mock_storage(tc, pc, dc)
        with \
                self.patchday(2023, 2, 11), \
                self.patchout() as o, self.patcherr() as e, \
                self.patch_ttyin('dtomorrow\n'):
            a.parse_run('done')
        self.assertEqual([str(x) for x in tc], ['#b'])
        self.assertEqual(dc[-1].markup, 'a')
        self.assertEqual(dc[-1].done_date, date(2023, 2, 11))
        self.assertEqual(pc[-1].markup, 'a')
        self.assertEqual(pc[-1].plan_date, date(2023, 2, 12))
        self.assertTrue(tc.changed)
        self.assertTrue(dc.changed)
        self.assertTrue(pc.changed)
        self.assertIn('(d)efer', e.getvalue())

    def test_defer_provided_repeat(self):
        tc = TodoCollection(
            [Item.from_markup('a > repeat tomorrow'),
             Item.from_markup('#b')])
        pc = PlanCollection()
        dc = DoneCollection(
            [Item.from_markup('c', state='done', done_date=date(2023, 1, 1))])
        a = BusyApp()
        a.storage = self.mock_storage(tc, pc, dc)
        with \
                self.patchday(2023, 2, 11), \
                self.patchout() as o, self.patcherr() as e, \
                self.patch_ttyin('\n'):
            a.parse_run('done')
        self.assertEqual([str(x) for x in tc], ['#b'])
        self.assertEqual(dc[-1].markup, 'a')
        self.assertEqual(dc[-1].done_date, date(2023, 2, 11))
        self.assertEqual(pc[-1].markup, 'a > tomorrow')
        self.assertEqual(pc[-1].plan_date, date(2023, 2, 12))
        self.assertTrue(tc.changed)
        self.assertTrue(dc.changed)
        self.assertTrue(pc.changed)
        self.assertIn('(o)ther', e.getvalue())

    def test_timing_started_first(self):
        o = TodoCollection([Item.from_markup('a !s202406111212')])
        p = PlanCollection()
        d = DoneCollection()
        a = Mock()
        a.storage = self.mock_storage(o, p, d)
        a.config.get.return_value = None
        c = DoneCommand(a, yes=True)
        with self.patchtime(2024, 6, 11, 12, 15):
            c.execute()
        self.assertEqual(len(o), 0)
        self.assertEqual(d[-1].markup, 'a !e3')
        self.assertTrue(o.changed)
        self.assertTrue(d.changed)

    def test_timing_not_started(self):
        o = TodoCollection([Item.from_markup('a')])
        p = PlanCollection()
        d = DoneCollection()
        a = Mock()
        a.storage = self.mock_storage(o, p, d)
        c = DoneCommand(a, yes=True)
        with self.patchtime(2024, 6, 11, 12, 15):
            c.execute()
        self.assertEqual(len(o), 0)
        self.assertEqual(d[-1].markup, 'a')
        self.assertTrue(o.changed)
        self.assertTrue(d.changed)

    def test_timing_started_with_previous(self):
        o = TodoCollection([Item.from_markup('a !s202406111212 !e4')])
        p = PlanCollection()
        d = DoneCollection()
        a = Mock()
        a.storage = self.mock_storage(o, p, d)
        a.config.get.return_value = None
        c = DoneCommand(a, yes=True)
        with self.patchtime(2024, 6, 11, 12, 15):
            c.execute()
        self.assertEqual(len(o), 0)
        self.assertEqual(d[-1].markup, 'a !e7')
        self.assertTrue(o.changed)
        self.assertTrue(d.changed)

    def test_timing_not_started_with_previous(self):
        o = TodoCollection([Item.from_markup('a !e4')])
        p = PlanCollection()
        d = DoneCollection()
        a = Mock()
        a.storage = self.mock_storage(o, p, d)
        a.config.get.return_value = None
        c = DoneCommand(a, yes=True)
        with self.patchtime(2024, 6, 11, 12, 15):
            c.execute()
        self.assertEqual(len(o), 0)
        self.assertEqual(d[-1].markup, 'a !e4')
        self.assertTrue(o.changed)
        self.assertTrue(d.changed)

    def test_timing_correct_in_handle_vals(self):
        """Confirm the correct elapsed time in the confirmation output"""
        o = TodoCollection([Item.from_markup('a !s202406111210 !e10')])
        p = PlanCollection()
        d = DoneCollection()
        a = BusyApp()
        a.storage = self.mock_storage(o, p, d)
        with self.patchtime(2024, 6, 11, 13, 00), self.patch_ttyin('\n'), \
                self.patcherr() as e:
            a.parse_run('done')
        self.assertIn("(1h0m)?", e.getvalue())
