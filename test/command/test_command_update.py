from unittest.mock import Mock

from busy import BusyApp
from busy.command.update_command import UpdateCommand
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandUpdate(BusyTestCase):

    def test_add_tag_to_one_item(self):
        o = TodoCollection([
            Item.from_markup('a'),
            Item.from_markup('b'),
        ])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=[1], add_tags=['x'])
        c.execute()
        self.assertIn('x', o[0].tags)
        self.assertNotIn('x', o[1].tags)
        self.assertTrue(o.changed)

    def test_add_tag_already_present(self):
        o = TodoCollection([Item.from_markup('a #x')])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=[1], add_tags=['x'])
        c.execute()
        self.assertEqual(o[0].tags, {'x'})
        self.assertTrue(o.changed)

    def test_add_multiple_tags(self):
        o = TodoCollection([Item.from_markup('a')])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=[1], add_tags=['x', 'y'])
        c.execute()
        self.assertIn('x', o[0].tags)
        self.assertIn('y', o[0].tags)
        self.assertTrue(o.changed)

    def test_add_tag_to_filtered_items(self):
        o = TodoCollection([
            Item.from_markup('a #p'),
            Item.from_markup('b'),
            Item.from_markup('c #p'),
        ])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=['p'], add_tags=['q'])
        c.execute()
        self.assertIn('q', o[0].tags)
        self.assertNotIn('q', o[1].tags)
        self.assertIn('q', o[2].tags)
        self.assertTrue(o.changed)

    def test_from_app_add_tag(self):
        tc = TodoCollection([
            Item.from_markup('a'),
            Item.from_markup('b'),
        ])
        a = BusyApp()
        a.storage = self.mock_storage(tc, Mock())
        with self.patchout(), self.patcherr():
            a.parse_run('update', '--add-tag', 'x', '1')
        self.assertIn('x', tc[0].tags)
        self.assertNotIn('x', tc[1].tags)

    def test_remove_tag_from_one_item(self):
        o = TodoCollection([
            Item.from_markup('a #x'),
            Item.from_markup('b #x'),
        ])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=[1], remove_tags=['x'])
        c.execute()
        self.assertNotIn('x', o[0].tags)
        self.assertIn('x', o[1].tags)
        self.assertTrue(o.changed)

    def test_remove_tag_not_present(self):
        o = TodoCollection([Item.from_markup('a')])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=[1], remove_tags=['x'])
        c.execute()
        self.assertNotIn('x', o[0].tags)
        self.assertTrue(o.changed)

    def test_remove_tag_from_filtered_items(self):
        o = TodoCollection([
            Item.from_markup('a #p #x'),
            Item.from_markup('b #x'),
            Item.from_markup('c #p #x'),
        ])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=['p'], remove_tags=['x'])
        c.execute()
        self.assertNotIn('x', o[0].tags)
        self.assertIn('x', o[1].tags)
        self.assertNotIn('x', o[2].tags)
        self.assertTrue(o.changed)

    def test_from_app_remove_tag(self):
        tc = TodoCollection([
            Item.from_markup('a #x'),
            Item.from_markup('b #x'),
        ])
        a = BusyApp()
        a.storage = self.mock_storage(tc, Mock())
        with self.patchout(), self.patcherr():
            a.parse_run('update', '--remove-tag', 'x', '1')
        self.assertNotIn('x', tc[0].tags)
        self.assertIn('x', tc[1].tags)

    def test_set_val_on_one_item(self):
        o = TodoCollection([
            Item.from_markup('a'),
            Item.from_markup('b'),
        ])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=[1], set_vals=['x42'])
        c.execute()
        self.assertEqual(o[0].vals.get('x'), '42')
        self.assertNotIn('x', o[1].vals)
        self.assertTrue(o.changed)

    def test_set_val_overwrites_existing(self):
        o = TodoCollection([Item.from_markup('a %x10')])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=[1], set_vals=['x99'])
        c.execute()
        self.assertEqual(o[0].vals.get('x'), '99')
        self.assertTrue(o.changed)

    def test_set_multiple_vals(self):
        o = TodoCollection([Item.from_markup('a')])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=[1], set_vals=['x1', 'y2'])
        c.execute()
        self.assertEqual(o[0].vals.get('x'), '1')
        self.assertEqual(o[0].vals.get('y'), '2')
        self.assertTrue(o.changed)

    def test_set_val_to_filtered_items(self):
        o = TodoCollection([
            Item.from_markup('a #p'),
            Item.from_markup('b'),
            Item.from_markup('c #p'),
        ])
        a = Mock()
        a.storage.get_collection.return_value = o
        c = UpdateCommand(a, filter=['p'], set_vals=['x5'])
        c.execute()
        self.assertEqual(o[0].vals.get('x'), '5')
        self.assertNotIn('x', o[1].vals)
        self.assertEqual(o[2].vals.get('x'), '5')
        self.assertTrue(o.changed)

    def test_from_app_set_val(self):
        tc = TodoCollection([
            Item.from_markup('a'),
            Item.from_markup('b'),
        ])
        a = BusyApp()
        a.storage = self.mock_storage(tc, Mock())
        with self.patchout(), self.patcherr():
            a.parse_run('update', '--set-val', 'x42', '1')
        self.assertEqual(tc[0].vals.get('x'), '42')
        self.assertNotIn('x', tc[1].vals)
