from busy.error import BusyError
from busy.model.configured import ConfiguredQueue, ConfiguredTag
from busy.test_case import BusyTestCase


class TestConfigured(BusyTestCase):

    def test_queue_bool(self):
        q = ConfiguredQueue.from_config('a', False)
        self.assertFalse(q.active)

    def test_queue_active(self):
        q = ConfiguredQueue.from_config('a', {'active': False})
        self.assertFalse(q.active)

    def test_queue_active_default(self):
        q = ConfiguredQueue.from_config('a', {})
        self.assertTrue(q.active)

    def test_queue_active_missing_config(self):
        q = ConfiguredQueue.from_config('a')
        self.assertTrue(q.active)

    def test_queue(self):
        q = ConfiguredQueue('a')
        self.assertTrue(q.active)

    def test_tag(self):
        q = ConfiguredQueue('q')
        t = ConfiguredTag(q, 't')
        self.assertTrue(t.active)

    def test_tag_from_config(self):
        q = ConfiguredQueue('q')
        t = ConfiguredTag.parse_config('t', parent_or_queue=q)
        self.assertTrue(t.active)
        self.assertEqual(t.queue, q)

    def test_config_hierarchy(self):
        q = ConfiguredQueue('q')
        t = ConfiguredTag(q, 't')
        tt = ConfiguredTag.parse_config('tt', parent_or_queue=t)
        self.assertTrue(tt.active)
        self.assertEqual(tt.queue, q)
        self.assertEqual(tt.parent, t)

    def test_tags_in_config(self):
        q = ConfiguredQueue.from_config('q', {'tags': {'t': True}})
        self.assertTrue(q.get_tag('t').active)

    def test_tags_config_hierarchy(self):
        q = ConfiguredQueue.from_config(
            'q', {'tags': {'t': {'tags': {'tt': True}}}})
        self.assertTrue(q.get_tag('tt').active)

    def test_error_on_dupe_config_tags(self):
        with self.assertRaises(BusyError):
            q = ConfiguredQueue.from_config(
                'q', {'tags': {'t': {'tags': {'t': True}}}})

    def test_validate_tags_active(self):
        q = ConfiguredQueue.from_config(
            'q', {'tags': {'t': {'tags': {'a': True, 'b': False}}}})
        q.validate_tags(['t', 'a'])
        with self.assertRaises(BusyError):
            q.validate_tags(['t', 'b'])

    def test_validate_tags_parent_without_child(self):
        q = ConfiguredQueue.from_config(
            'q', {'tags': {'t': {'tags': {'a': True}}}})
        q.validate_tags(['t', 'a'])
        with self.assertRaises(BusyError):
            q.validate_tags(['t'])

    def test_validate_tags_child_without_parent(self):
        q = ConfiguredQueue.from_config(
            'q', {'tags': {'t': {'tags': {'a': True}}}})
        q.validate_tags(['t', 'a'])
        with self.assertRaises(BusyError):
            q.validate_tags(['a'])

    # def test_validate_descenent_tags(self):
        # self.assertTrue(q.get_tag('tt').active)
