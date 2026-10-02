import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from busy.model.item import Item
from busy.storage.file_storage import FileStorage


class TestFileStorage(TestCase):

    def test_dir_provided(self):
        with TemporaryDirectory() as t:
            s = FileStorage(t)
            self.assertIsInstance(s.directory, Path)
            self.assertEqual(str(s.directory), t)

    def test_read_collection(self):
        with TemporaryDirectory() as t:
            with open(Path(t) / 'tasks.todo.psv', 'w') as f:
                f.write('a\nb\n')
            s = FileStorage(t)
            c = s.get_collection('tasks')
            self.assertEqual(c[0].markup, 'a')

    def test_write_collection(self):
        with TemporaryDirectory() as t:
            s = FileStorage(t)
            c = s.get_collection('tasks')
            c.append(Item.from_markup('b'))
            s.save()
            with open(Path(t) / 'tasks.todo.psv', 'r') as f:
                x = f.read()
            self.assertEqual(x.strip(), 'b')

    def test_exists(self):
        with TemporaryDirectory() as t:
            with open(Path(t) / 'tasks.todo.psv', 'w') as f:
                f.write('a\nb\n')
            s = FileStorage(t)
            self.assertTrue(s.queue_exists('tasks'))

    def test_exists_not(self):
        with TemporaryDirectory() as t:
            with open(Path(t) / 'foo.plan.psv', 'w') as f:
                f.write('')
            s = FileStorage(t)
            self.assertFalse(s.queue_exists('foo'))
