import fcntl
import time
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from wizlib.config_handler import ConfigHandler

from busy import BusyApp
from busy.error import BusyError
from busy.model.item import Item
from busy.storage.file_storage import DEFAULT_LOCK_TIMEOUT, FileStorage
from busy.test_case import BusyTestCase


@contextmanager
def held_lock(directory):
    """Hold the storage lock on a separate open file description, as another
    process would. flock locks conflict between open file descriptions even
    within one process."""
    with open(Path(directory) / '.lock', 'a+') as file:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX)
        yield


def lock_is_free(directory):
    with open(Path(directory) / '.lock', 'a+') as file:
        try:
            fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            return False


class TestFileStorageLock(BusyTestCase):

    def app(self, directory, **config):
        app = BusyApp()
        app.config = ConfigHandler.fake(busy_storage_directory=directory,
                                        **config)
        app.storage = FileStorage(directory, app.identifier,
                                  lock_timeout=app.config.get(
                                      'busy-lock-timeout'))
        return app

    def test_default_timeout(self):
        with TemporaryDirectory() as t:
            self.assertEqual(FileStorage(t).lock_timeout,
                             DEFAULT_LOCK_TIMEOUT)

    def test_timeout_from_config(self):
        with TemporaryDirectory() as t:
            app = BusyApp()
            app.config = ConfigHandler.fake(busy_storage_directory=t,
                                            busy_lock_timeout=0.5)
            self.assertEqual(app.storage.lock_timeout, 0.5)

    def test_invalid_timeout(self):
        with TemporaryDirectory() as t:
            with self.assertRaises(BusyError):
                FileStorage(t, lock_timeout='soon')
            with self.assertRaises(BusyError):
                FileStorage(t, lock_timeout=-1)

    def test_load_acquires_and_save_releases(self):
        with TemporaryDirectory() as t:
            s = FileStorage(t)
            self.assertFalse(s.locked)
            c = s.get_collection('tasks')
            self.assertTrue(s.locked)
            self.assertFalse(lock_is_free(t))
            c.append(Item.from_markup('a'))
            s.get_collection('tasks', 'plan')
            self.assertTrue(s.locked)
            s.save()
            self.assertFalse(s.locked)
            self.assertTrue(lock_is_free(t))
            # A later load takes the lock again
            self.assertEqual(s.get_collection('tasks')[0].markup, 'a')
            self.assertTrue(s.locked)
            s.release()
            self.assertTrue(lock_is_free(t))

    def test_held_lock_times_out(self):
        with TemporaryDirectory() as t:
            s = FileStorage(t, lock_timeout=0.2)
            with held_lock(t):
                start = time.monotonic()
                with self.assertRaises(BusyError) as e:
                    s.get_collection('tasks')
                self.assertGreaterEqual(time.monotonic() - start, 0.2)
            self.assertIn('.lock', str(e.exception))
            self.assertFalse(s.locked)
            # Works once the other holder lets go
            s.get_collection('tasks')
            self.assertTrue(s.locked)
            s.release()

    def test_add_times_out_while_lock_held(self):
        with TemporaryDirectory() as t:
            app = self.app(t, busy_lock_timeout=0.2)
            with held_lock(t):
                with self.patchout(), self.patcherr():
                    with self.assertRaises(BusyError):
                        app.parse_run('add', 'a')
            self.assertFalse((Path(t) / 'tasks.todo.psv').exists())

    def test_list_times_out_while_lock_held(self):
        with TemporaryDirectory() as t:
            app = self.app(t, busy_lock_timeout=0.2)
            with held_lock(t):
                with self.patchout(), self.patcherr():
                    with self.assertRaises(BusyError):
                        app.parse_run('list')

    def test_timeout_exits_nonzero(self):
        with TemporaryDirectory() as t:
            config = Path(t) / 'busy.yml'
            config.write_text(
                f"busy:\n  storage:\n    directory: {t}\n" +
                "  lock:\n    timeout: 0.2\n")
            with held_lock(t):
                with self.patchout(), self.patcherr() as e:
                    with self.assertRaises(SystemExit) as x:
                        BusyApp.start('--config', str(config), 'add', 'a')
            self.assertEqual(x.exception.code, 1)
            self.assertIn('BusyError', e.getvalue())
            self.assertIn(str(Path(t) / '.lock'), e.getvalue())

    def test_normal_commands_unaffected(self):
        with TemporaryDirectory() as t:
            app = self.app(t, busy_lock_timeout=0.2)
            with self.patchout() as o, self.patcherr():
                app.parse_run('add', 'a')
                app.parse_run('add', 'b')
                # A second app (another process) can use the data in turn
                other = self.app(t, busy_lock_timeout=0.2)
                other.parse_run('add', 'c')
                app.parse_run('list')
            self.assertIn('c', o.getvalue())
            self.assertTrue(lock_is_free(t))

    def test_lock_released_after_failed_command(self):
        with TemporaryDirectory() as t:
            app = self.app(t, busy_lock_timeout=0.2)
            app.storage.get_collection('tasks')
            with self.patchout(), self.patcherr():
                with self.assertRaises(Exception):
                    app.run(command='nonexistent')
            self.assertFalse(app.storage.locked)
            self.assertTrue(lock_is_free(t))

    def test_del_releases(self):
        with TemporaryDirectory() as t:
            s = FileStorage(t)
            s.get_collection('tasks')
            del s
            self.assertTrue(lock_is_free(t))
