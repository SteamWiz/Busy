from unittest.mock import Mock

from busy.command.view_command import ViewCommand
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestBug205MultipleFilters(BusyTestCase):
    """Regression test for issue #205: grep: filter should be OR'd with tag
    filters (group 2), not AND'd in its own group."""

    def _make_app(self, *items):
        d = TodoCollection()
        for item in items:
            d.append(Item.from_markup(item))
        s = self.mock_storage(d, PlanCollection(), DoneCollection())
        a = Mock()
        a.storage = s
        return a

    def test_combined_tag_and_grep_includes_tag_only_match(self):
        """Items matching the tag filter should appear even if they don't match
        grep, because grep: is OR'd with tag criteria in the same group."""
        a = self._make_app(
            'Draft contract #insurance #internal #main',
            'Iterate on license renewal #admin #internal #main',
            'Unrelated task #other',
        )
        c = ViewCommand(a, filter=['internal+main', 'grep:insurance'])
        with self.patchout(), self.patcherr():
            n = c.execute()
        lines = n.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn('Draft contract', lines)
        self.assertIn('Iterate on license renewal', lines)

    def test_combined_tag_and_grep_includes_grep_only_match(self):
        """Items matching grep but not the tag filter should also appear."""
        a = self._make_app(
            'Draft contract #insurance #internal #main',
            'Iterate on license renewal #admin #internal #main',
            'Insurance policy notes #other',
        )
        c = ViewCommand(a, filter=['internal+main', 'grep:insurance'])
        with self.patchout(), self.patcherr():
            n = c.execute()
        lines = n.splitlines()
        self.assertEqual(len(lines), 3)

    def test_grep_alone_still_filters_by_content(self):
        """A standalone grep: filter still works correctly."""
        a = self._make_app(
            'Draft contract #insurance #internal #main',
            'Unrelated task #other',
        )
        c = ViewCommand(a, filter=['grep:insurance'])
        with self.patchout(), self.patcherr():
            n = c.execute()
        lines = n.splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn('Draft contract', lines)
