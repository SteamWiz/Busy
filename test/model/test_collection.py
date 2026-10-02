from datetime import date
from io import StringIO
from unittest import TestCase

from busy.error import BusyError
from busy.model.collection import Collection, CollectionError
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item


class TestCollection(TestCase):

    def test_acts_as_list(self):
        c = Collection.family_member('state', 'todo')()
        i = Item.from_markup('f')
        c.append(i)

    def test_all_states_exist(self):
        mx = Collection.family_members('state')
        sx = {m.state for m in mx}
        self.assertEqual(sx, {'todo', 'plan', 'done'})

    def test_only_add_my_state(self):
        c = Collection.family_member('state', 'todo')()
        d = c + [Item.from_markup('d'), Item.from_markup('e')]
        i2 = Item.from_markup('b', state='plan')
        with self.assertRaises(CollectionError):
            c[0] = i2
        with self.assertRaises(CollectionError):
            c += [i2]
        with self.assertRaises(CollectionError):
            c.append(i2)
        with self.assertRaises(CollectionError):
            c = c + [i2]
        with self.assertRaises(CollectionError):
            c.extend([i2])

    def test_instantiate(self):
        c = TodoCollection([Item.from_markup('a'), Item.from_markup('b')])
        self.assertEqual(len(c), 2)

    def test_instantiate_check_state(self):
        with self.assertRaises(CollectionError):
            c = TodoCollection([Item.from_markup('b', state='plan')])

    def test_select(self):
        c = TodoCollection([Item.from_markup('a'), Item.from_markup('b #c')])
        ix = c.selection('c')
        self.assertEqual(ix[0][0], 1)

    def test_replace_one(self):
        c = TodoCollection(
            [Item.from_markup('a'),
             Item.from_markup('b'),
             Item.from_markup('c')])
        c.replace([1], [Item.from_markup('d')])
        self.assertEqual(c[1].markup, 'd')
        self.assertEqual(c[2].markup, 'c')

    def test_replace_multi(self):
        c = TodoCollection([Item.from_markup(x) for x in 'abcd'])
        c.replace([1, 2], [Item.from_markup(x) for x in '12'])
        self.assertEqual([str(x) for x in c], ['a', '1', '2', 'd'])

    def test_replace_extra_index(self):
        c = TodoCollection([Item.from_markup(x) for x in 'abcd'])
        c.replace([1, 2], [Item.from_markup('1')])
        self.assertEqual([str(x) for x in c], ['a', '1', 'd'])

    def test_delete(self):
        c = TodoCollection([Item.from_markup(x) for x in 'abcd'])
        d = c.delete([0, 2])
        self.assertEqual([str(x) for x in c], ['b', 'd'])
        self.assertEqual([str(y) for y in d], ['a', 'c'])

    def test_select_range(self):
        c = TodoCollection([Item.from_markup(x) for x in 'abcd'])
        s = c.selection('2-3')
        self.assertEqual([i for i, t in s], [1, 2])

    def test_select_combination(self):
        c = TodoCollection(
            [Item.from_markup('b #x'),
             Item.from_markup('c #x'),
             Item.from_markup('d #y')])
        s = c.selection('2-3', 'x')
        self.assertEqual(s[0][0], 1)

    def test_select_range_2_tags(self):
        c = TodoCollection([Item.from_markup('b #x'), Item.from_markup('c #x'),
                            Item.from_markup('d #y'), Item.from_markup('e')])
        s = c.selection('2-4', 'x', 'y')
        self.assertEqual([i for i, t in s], [1, 2])

    def test_select_range_and_tags(self):
        c = TodoCollection(
            [Item.from_markup('b #x'),
             Item.from_markup('c #x #y'),
             Item.from_markup('d #y'),
             Item.from_markup('e')])
        s = c.selection('x+y')
        self.assertEqual([1], [i for i, t in s])

    def test_changed_not(self):
        c = TodoCollection([Item.from_markup(x) for x in 'abcd'])
        self.assertFalse(c.changed)

    def test_write(self):
        c = TodoCollection([Item.from_markup(x) for x in 'abcd'])
        f = StringIO()
        c.write_items(f)
        f.seek(0)
        s = f.readlines()
        self.assertEqual([m.strip() for m in s], [c for c in 'abcd'])

    def test_write_some(self):
        c = TodoCollection([Item.from_markup(x) for x in 'abcd'])
        f = StringIO()
        c.write_items(f, [0, 2])
        f.seek(0)
        s = f.readlines()
        self.assertEqual([m.strip() for m in s], [c for c in 'ac'])

    def test_read_all(self):
        c = TodoCollection()
        f = StringIO()
        f.write("a\nb")
        f.seek(0)
        c.read_items(f)
        self.assertEqual([str(x) for x in c], ['a', 'b'])

    def test_read_all_plans(self):
        c = PlanCollection()
        f = StringIO()
        f.write("2023-05-01|a\n2023-06-01|b")
        f.seek(0)
        c.read_items(f)
        self.assertEqual(c[0].plan_date, date(2023, 5, 1))

    def test_read_all_done(self):
        c = DoneCollection()
        f = StringIO()
        f.write("2023-05-01|a\n2023-06-01|b")
        f.seek(0)
        c.read_items(f)
        self.assertEqual(c[0].done_date, date(2023, 5, 1))

    def test_changes_on_del(self):
        c = TodoCollection([Item.from_markup('a'), Item.from_markup('b')])
        del c[1]
        self.assertEqual([str(i) for i in c], ['a'])
        self.assertTrue(c.changed)

    def test_del_range(self):
        c = TodoCollection([Item.from_markup(i) for i in 'abcd'])
        del c[1:3]
        self.assertEqual([str(i) for i in c], ['a', 'd'])
        self.assertTrue(c.changed)

    def test_del_range_assignment_syntax(self):
        c = TodoCollection([Item.from_markup(i) for i in 'abcd'])
        c[1:3] = []
        self.assertEqual([str(i) for i in c], ['a', 'd'])
        self.assertTrue(c.changed)

    def test_pop_changed(self):
        c = TodoCollection([Item.from_markup(i) for i in 'abcd'])
        c.pop(1)
        self.assertEqual([str(i) for i in c], ['a', 'c', 'd'])
        self.assertTrue(c.changed)

    def test_pipe_fails(self):
        c = Collection.family_member('state', 'todo')()
        d = c + [Item.from_markup('d'), Item.from_markup('e')]
        i2 = Item.from_markup('b|r')
        with self.assertRaises(CollectionError):
            c[0] = i2
        with self.assertRaises(CollectionError):
            c += [i2]
        with self.assertRaises(CollectionError):
            c.append(i2)
        with self.assertRaises(CollectionError):
            c = c + [i2]
        with self.assertRaises(CollectionError):
            c.extend([i2])

    def test_function_criterium(self):
        c = Collection.family_member('state', 'done')()
        c.append(
            Item.from_markup(
                'c', state='done', done_date=date(2024, 6, 1)))
        c.append(
            Item.from_markup(
                'd', state='done', done_date=date(2024, 7, 1)))

        def func(i): return i.done_date >= date(2024, 7, 1)
        s = c.selection(func)
        self.assertEqual([1], [i for i, t in s])

    def test_hyphen_in_criteria(self):
        c = TodoCollection([Item.from_markup('a'), Item.from_markup('b #c9')])
        ix = c.selection('c9')
        self.assertEqual([i for i, t in ix], [1])

    def test_invalid_criteria(self):
        c = TodoCollection([Item.from_markup('a'), Item.from_markup('b #c9')])
        with self.assertRaises(BusyError):
            c.selection('9f')

    def test_exclusion_tag(self):
        """Items without the excluded tag are returned"""
        c = TodoCollection([
            Item.from_markup('a #tag-a'),
            Item.from_markup('b #tag-a #tag-b'),
            Item.from_markup('c #tag-b'),
        ])
        s = c.selection('~tag-b')
        self.assertEqual([i for i, t in s], [0])

    def test_exclusion_tag_with_inclusion(self):
        """Inclusion AND exclusion: tag-a but not tag-b"""
        c = TodoCollection([
            Item.from_markup('a #tag-a'),
            Item.from_markup('b #tag-a #tag-b'),
            Item.from_markup('c #tag-b'),
            Item.from_markup('d'),
        ])
        s = c.selection('tag-a', '~tag-b')
        self.assertEqual([i for i, t in s], [0])

    def test_multiple_exclusions(self):
        """Multiple exclusion filters are all applied (AND'd)"""
        c = TodoCollection([
            Item.from_markup('a #x'),
            Item.from_markup('b #x #y'),
            Item.from_markup('c #x #y #z'),
        ])
        s = c.selection('~y', '~z')
        self.assertEqual([i for i, t in s], [0])

    def test_exclusion_no_match_returns_all(self):
        """Excluding a tag not present in any item returns all items"""
        c = TodoCollection([
            Item.from_markup('a #x'),
            Item.from_markup('b #y'),
        ])
        s = c.selection('~absent')
        self.assertEqual([i for i, t in s], [0, 1])
