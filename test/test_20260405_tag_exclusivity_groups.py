from busy.error import BusyError
from busy.model.configured import ConfiguredQueue
from busy.test_case import BusyTestCase


def queue_with_groups():
    return ConfiguredQueue.from_config(
        "q",
        {
            "tags": {
                "work": {"group": "context"},
                "personal": {"group": "context"},
                "hobby": {"group": "context"},
                "urgent": None,
            }
        },
    )


class TestTagExclusivityGroups(BusyTestCase):
    def test_group_parsed(self):
        q = queue_with_groups()
        self.assertEqual(q.get_tag("work").group, "context")

    def test_group_default_none(self):
        q = queue_with_groups()
        self.assertIsNone(q.get_tag("urgent").group)

    def test_group_ignored_on_child_tag(self):
        q = ConfiguredQueue.from_config(
            "q", {"tags": {"foo": {"tags": {"bar": {"group": "g"}}}}}
        )
        self.assertIsNone(q.get_tag("bar").group)

    def test_single_group_tag_valid(self):
        q = queue_with_groups()
        q.validate_tags({"work"})

    def test_no_group_tags_valid(self):
        q = queue_with_groups()
        q.validate_tags({"urgent"})

    def test_two_tags_same_group_raises(self):
        q = queue_with_groups()
        with self.assertRaises(BusyError):
            q.validate_tags({"work", "personal"})

    def test_error_message_content(self):
        q = queue_with_groups()
        with self.assertRaises(BusyError) as ctx:
            q.validate_tags({"work", "personal"})
        self.assertIn("context", str(ctx.exception))
        self.assertIn("'q'", str(ctx.exception))

    def test_three_tags_same_group_raises(self):
        q = queue_with_groups()
        with self.assertRaises(BusyError):
            q.validate_tags({"work", "personal", "hobby"})

    def test_group_tag_with_unrelated_tag_valid(self):
        q = queue_with_groups()
        q.validate_tags({"work", "urgent"})

    def test_multiple_groups_one_each_valid(self):
        q = ConfiguredQueue.from_config(
            "q",
            {
                "tags": {
                    "work": {"group": "context"},
                    "personal": {"group": "context"},
                    "high": {"group": "priority"},
                    "low": {"group": "priority"},
                }
            },
        )
        q.validate_tags({"work", "high"})

    def test_multiple_groups_clash_in_one_raises(self):
        q = ConfiguredQueue.from_config(
            "q",
            {
                "tags": {
                    "work": {"group": "context"},
                    "personal": {"group": "context"},
                    "high": {"group": "priority"},
                    "low": {"group": "priority"},
                }
            },
        )
        with self.assertRaises(BusyError):
            q.validate_tags({"work", "personal", "high"})
