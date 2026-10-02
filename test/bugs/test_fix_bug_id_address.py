from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from busy import BusyApp
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.storage.file_storage import FileStorage
from busy.test_case import BusyTestCase

# We thought it was a bug! But actually working as expected. Still the extra
# testing helps.

# Note the new better way to run an app-level test with config


class TestAdvancedConfig(BusyTestCase):

    def test_fix(self):
        with TemporaryDirectory() as dir:
            with self.patchout(), self.patcherr():
                with NamedTemporaryFile(mode='w') as config:
                    yaml = f"busy:\n  storage:\n    directory: {dir}\n"
                    config.write(yaml)
                    config.seek(0)
                    app = BusyApp(config=config.name)
                    app.parse_run('add', 'x')
                    with open(Path(dir) / 'tasks.todo.psv') as todo:
                        x = todo.read()
                    self.assertEqual('?000001', x[:7])

    def test_fix_extra_id(self):
        with TemporaryDirectory() as dir:
            with self.patchout(), self.patcherr():
                with NamedTemporaryFile(mode='w') as config:
                    yaml = f"busy:\n  storage:\n    directory: {dir}\n"
                    config.write(yaml)
                    config.seek(0)
                    app = BusyApp(config=config.name)
                    app.parse_run('add', 'x')
                    app.parse_run('list')
                    with open(Path(dir) / 'tasks.todo.psv') as todo:
                        x = todo.read()
                    self.assertEqual('?000001 x', x[:9])
