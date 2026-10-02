from datetime import date as Date, datetime
from unittest import TestCase
from unittest.mock import patch

from busy.model.item import Item, ItemStateError
from busy.util.date_util import relative_date
from busy.test_case import BusyTestCase


class TestItem(BusyTestCase):

    def test_markup(self):
        i = Item.from_markup("foo")
        self.assertEqual(i.markup, "foo")

    def test_first_not(self):
        i = Item.from_markup("foo")
        self.assertEqual(i.body, "foo")

    def test_first(self):
        i = Item.from_markup("foo --> bar")
        self.assertEqual(i.body, "foo")

    def test_first_multiple(self):
        i = Item.from_markup("a  > b > c")
        self.assertEqual(i.body, "a")

    def test_tags(self):
        i = Item.from_markup("a #b #c > d #e")
        self.assertEqual(i.tags, {"b", "c"})

    def test_resource(self):
        i = Item.from_markup("a @b #c --> f at g")
        self.assertEqual(i.url, "b")

    def test_resource_not(self):
        i = Item.from_markup("a b --> c @d")
        self.assertEqual(i.url, "")

    def test_resource_real_url(self):
        i = Item.from_markup("a @https://foo.com/gr?ik=%20h --> c @d")
        self.assertEqual(i.url, "https://foo.com/gr?ik=%20h")

    def test_base(self):
        i = Item.from_markup("a @b #c  f --> f at g")
        self.assertEqual(i.base, "a f")

    def test_next(self):
        i = Item.from_markup("a @b #c  f --> f @g")
        self.assertEqual(i.repeat, "f @g")

    def test_current(self):
        i = Item.from_markup("a @b #c  f --> f @g")
        self.assertEqual(i.body, 'a f #c @b')

    def test_repeat(self):
        i = Item.from_markup("a @b #c  f --> repeat foo bar")
        self.assertEqual(i.repeat, "foo bar")

    def test_default_state(self):
        i = Item.from_markup('p')
        self.assertEqual(i.state, 'todo')

    def test_transition_done(self):
        i = Item.from_markup('p')
        i.done(Date(2023, 4, 4))
        self.assertEqual(i.state, 'done')
        self.assertEqual(i.done_date, Date(2023, 4, 4))

    def test_transition_done_state_test(self):
        i = Item.from_markup('p', state='done')
        with self.assertRaises(ItemStateError):
            i.done(Date(2023, 4, 4))

    def test_done_date_attribute(self):
        d = Item.from_markup('g', state='done', done_date=Date(2023, 3, 15))
        self.assertEqual(d.done_date, Date(2023, 3, 15))

    def test_transition_undone_state_test(self):
        d = Item.from_markup('g', done_date=Date(2023, 3, 15))
        with self.assertRaises(ItemStateError):
            d.undone()

    def test_transition_plan(self):
        t = Item.from_markup('j')
        t.plan(Date(2023, 5, 5))
        self.assertEqual(t.state, 'plan')

    def test_transition_unplan(self):
        p = Item.from_markup('h', state='plan', plan_date=Date(2024, 1, 1))
        p.unplan()
        self.assertEqual(p.state, 'todo')

    # def test_follow_date(self):
    #     with patch('busy.util.date_util.today', lambda: Date(2019, 2, 11)):
    #         t = Item.from_markup('a > repeat tomorrow')
    #         self.assertEqual(t.repeat_date, Date(2019, 2, 12))

    # def test_follow_date_garbage(self):
    #     with patch('busy.util.date_util.today', lambda: Date(2019, 2, 11)):
    #         t = Item.from_markup('a > repeat jf')
    #         self.assertIsNone(t.repeat_date)

    # def test_follow_date_not(self):
    #     with patch('busy.util.date_util.today', lambda: Date(2019, 2, 11)):
    #         t = Item.from_markup('a > b > c')
    #         self.assertEqual(t.repeat_date, None)

    def test_done_defer(self):
        t1 = Item.from_markup('l')
        with self.patchday(2019, 2, 11):
            t2 = t1.done(Date(2023, 4, 3), relative_date('tomorrow'))
            self.assertEqual(t2.state, 'plan')
            self.assertEqual(t2.markup, 'l')
            self.assertEqual(t2.plan_date, Date(2019, 2, 12))

    def test_done_defer_keep_default(self):
        t1 = Item.from_markup('k > repeat on 6')
        with self.patchday(2019, 2, 11):
            t2 = t1.done(Date(2023, 4, 3), relative_date('tomorrow'))
            self.assertEqual(t2.state, 'plan')
            self.assertEqual(t2.markup, 'k > 6')
            self.assertEqual(t2.plan_date, Date(2019, 2, 12))

    def test_string(self):
        i = Item.from_markup('foo')
        self.assertEqual(str(i), 'foo')

    def test_plan_date(self):
        i = Item.from_markup('g')
        i.plan_date = Date(2023, 3, 4)
        self.assertEqual(i.plan_date, Date(2023, 3, 4))

    def test_start_time(self):
        i = Item.from_markup('h !s202406092242')
        self.assertEqual(i.start_time, datetime(2024, 6, 9, 22, 42))

    def test_elapsed_time(self):
        i = Item.from_markup('h !e123')
        self.assertEqual(i.elapsed_minutes, 123)

    def test_timeable(self):
        i = Item.from_markup('i')
        self.assertTrue(i.base)

    def test_not_timeable(self):
        i = Item.from_markup('#p @f')
        self.assertFalse(i.base)

    def test_elapse_new(self):
        i = Item.from_markup('i !s202406092240')
        with self.patchtime(2024, 6, 9, 22, 42):
            i.stop_timer()
        self.assertEqual(i.elapsed_minutes, 2)
        self.assertEqual(i.markup, 'i !e2')

    def test_start_timing(self):
        i = Item.from_markup('i')
        with self.patchtime(2024, 6, 9, 22, 42):
            i.start_timer()
        self.assertEqual(i.start_time, datetime(2024, 6, 9, 22, 42))
        self.assertEqual(i.markup, 'i !s202406092242')

    def test_start_timing_with_elapsed(self):
        i = Item.from_markup('i !e4')
        with self.patchtime(2024, 6, 9, 22, 42):
            i.start_timer()
        self.assertEqual(i.start_time, datetime(2024, 6, 9, 22, 42))
        self.assertEqual(i.markup, 'i !e4 !s202406092242')

    def test_done_plan_markup(self):
        t1 = Item.from_markup('l #a @b !e123 !s202403241231 > tomorrow')
        with self.patchday(2019, 2, 11):
            t2 = t1.done(Date(2023, 4, 3), relative_date('tomorrow'))
            self.assertEqual(t2.state, 'plan')
            self.assertEqual(t2.markup, 'l #a @b > tomorrow')
            self.assertEqual(t2.plan_date, Date(2019, 2, 12))

    def test_start_timer_with_repeat(self):
        i = Item.from_markup('i > repeat tomorrow')
        with self.patchtime(2024, 6, 9, 22, 42):
            i.start_timer()
        self.assertEqual(i.start_time, datetime(2024, 6, 9, 22, 42))
        self.assertEqual(i.markup, 'i !s202406092242 > tomorrow')

    def test_elapse_with_repeat(self):
        i = Item.from_markup('i !s202406092240 > repeat 2')
        with self.patchtime(2024, 6, 9, 22, 42):
            i.stop_timer()
        self.assertEqual(i.elapsed_minutes, 2)
        self.assertEqual(i.markup, 'i !e2 > 2')

    def test_data_value(self):
        i = Item.from_markup('p %k88')
        self.assertEqual('88', i.vals['k'])

    def test_fuzzkey(self):
        i = Item.from_markup('Foo -bAR')
        x = i.fuzzkey
        self.assertEqual('foo -bar', x)

    def test_fuzzkey_parentheses(self):
        i = Item.from_markup('Foo (zing)')
        x = i.fuzzkey
        self.assertEqual('foo', x)

    def test_formattable_tags_sorted(self):
        i = Item.from_markup("X #a #b #c")
        self.assertEqual(i.formattable['tags'], 'a b c')

    def test_formattable_tags_sorted_order(self):
        i = Item.from_markup("X #c #a #b")
        self.assertEqual(i.formattable['tags'], 'a b c')

    def test_filter_grep_match(self):
        i = Item.from_markup('Reconcile Chase Visa')
        self.assertTrue(i.filter_grep('reconcile'))

    def test_filter_grep_case_insensitive(self):
        i = Item.from_markup('Reconcile Chase Visa')
        self.assertTrue(i.filter_grep('RECONCILE'))

    def test_filter_grep_no_match(self):
        i = Item.from_markup('Buy groceries')
        self.assertFalse(i.filter_grep('reconcile'))

    def test_filter_grep_partial_match(self):
        i = Item.from_markup('Reconcile Chase Visa')
        self.assertTrue(i.filter_grep('chase'))

    def test_filter_grep_regex(self):
        i = Item.from_markup('Reconcile Chase Visa')
        self.assertTrue(i.filter_grep('Chase.*Visa'))
