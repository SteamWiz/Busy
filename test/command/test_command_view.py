from datetime import date
from tempfile import NamedTemporaryFile
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

JINJA = '''o
{% for item in items %}- {{ item.base }}
{% endfor %}x'''


class TestCommandView(BusyTestCase):

    def test_view_all_fields(self):
        a, b, c = Item.from_markup(
            'a #f @g > 1d'), Item.from_markup('b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = ViewCommand(a, filter=['1'])
        n = c.execute()
        self.assertEqual(n, 'a')

    def test_view_everyone(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = ViewCommand(a, filter=['1-'])
        n = c.execute()
        self.assertEqual(n, 'a\nb\nc')

    def test_unknown_field(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = ViewCommand(a, fixed='x')
        with self.assertRaises(BusyError):
            c.execute()

    def test_from_run(self):
        a, b, c = Item.from_markup('a %g7'), Item.from_markup(
            'b %g9'), Item.from_markup('c %g3')
        o = TodoCollection([a, b, c])
        a = BusyApp()
        a.storage = self.mock_storage(o, PlanCollection(), DoneCollection())
        with self.patchout() as o:
            a.parse_run('view', '--fixed', 'val.g')
        o.seek(0)
        self.assertEqual('7\n9\n3', o.read())

    def test_view_val(self):
        a, b, c = Item.from_markup('a %g7'), Item.from_markup(
            'b %g9'), Item.from_markup('c %g3')
        o = TodoCollection([a, b, c])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = ViewCommand(a, fixed='val.g', filter=['1'])
        n = c.execute()
        self.assertEqual(n, '7')

    def test_blank_if_no_val(self):
        a, b, c = Item.from_markup('a %g7'), Item.from_markup(
            'b %g9'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = ViewCommand(a, fixed='val.g', filter=['1-'])
        n = c.execute()
        self.assertEqual(n, '7\n9\n')

    def test_view_url(self):
        a, b, c = Item.from_markup(
            'a #f @g > 1d'), Item.from_markup('b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = ViewCommand(a, fixed='url', filter=['1'])
        n = c.execute()
        self.assertEqual(n, 'g')

    def test_view_2_fields(self):
        a, b, c = Item.from_markup('a %g1 %j5'), Item.from_markup(
            'b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = ViewCommand(a, fixed='val.g,val.j', filter=['1'])
        n = c.execute()
        self.assertEqual(n, '1 5')

    def test_checkboxes(self):
        o = TodoCollection([Item.from_markup('a')])
        d = DoneCollection(
            [Item.from_markup('d', state='done', done_date=date(2023, 1, 1))])
        p = PlanCollection([
            Item.from_markup('f', state='plan', plan_date=date(2023, 6, 8))])
        a = BusyApp()
        a.storage = self.mock_storage(o, p, d)
        with self.patchout() as o, self.patcherr():
            a.parse_run('view', '--state', 'multi',
                        '--fixed', 'checkbox,base')
        o.seek(0)
        self.assertEqual('- [x] d\n- [ ] a\n- [ ] f', o.read())

    def test_view_named_tag(self):
        a, b, c = Item.from_markup('a #f'), Item.from_markup(
            'b #g'), Item.from_markup('c #f #g')
        o = TodoCollection([a, b, c])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = ViewCommand(a, fixed='tag.f')
        n = c.execute()
        self.assertEqual(n, 'f\n\nf')

    def test_defuzz(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b'), Item.from_markup('a (f)')
        o = TodoCollection([a, b, c])
        a = BusyApp()
        a.storage = self.mock_storage(o, PlanCollection(), DoneCollection())
        with self.patchout() as o:
            a.parse_run('view', '--unique')
        o.seek(0)
        self.assertEqual('b\na (f)', o.read())

    def test_view_num(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b'), Item.from_markup('c')
        o = TodoCollection([a, b, c])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = ViewCommand(a, fixed='num')
        n = c.execute()
        self.assertEqual(n, '1\n2\n3')

    def test_format(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b %g9'), Item.from_markup('c %g3')
        o = TodoCollection([a, b, c])
        a = BusyApp()
        a.storage = self.mock_storage(o, PlanCollection(), DoneCollection())
        with self.patchout() as o:
            a.parse_run('view', '--format', 'x{base}')
        o.seek(0)
        self.assertEqual('xa\nxb\nxc', o.read())

    def test_jinja(self):
        a, b, c = Item.from_markup('a'), Item.from_markup(
            'b %g9'), Item.from_markup('c %g3')
        o = TodoCollection([a, b, c])
        a = BusyApp()
        a.storage = self.mock_storage(o, PlanCollection(), DoneCollection())
        with NamedTemporaryFile(mode='w+', delete=True) as f:
            f.write(JINJA)
            f.seek(0)
            with self.patchout() as o:
                a.parse_run('view', '--jinja', f.name)
        o.seek(0)
        self.assertEqual('o\n- a\n- b\n- c\nx', o.read())

    def test_view_no_change(self):
        a = Item.from_markup('a')
        o = TodoCollection([a])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = ViewCommand(a)
        n = c.execute()
        self.assertFalse(o.changed)
