from tempfile import TemporaryDirectory
from wizlib.config_handler import ConfigHandler
from busy import BusyApp
from busy.error import BusyError
from busy.storage.file_storage import FileStorage
from busy.test_case import BusyTestCase


class TestAdvancedConfig(BusyTestCase):

    def _setup_app_with_config(self, temp_dir, **base_config):
        """Helper method to properly set up BusyApp with fake config and
        reinitialize storage"""
        base_config = base_config if base_config else {'busy': {}}
        base_config['busy']['storage'] = {
            'directory': temp_dir
        }
        app = BusyApp()
        app.config = ConfigHandler(data=base_config)
        return app

    def test_active_queue_setting_allows_active_queue(self):
        """Test that a queue marked as active=true can be used"""
        with TemporaryDirectory() as temp_dir:
            # Create app with fake config that has active queue setting
            app = self._setup_app_with_config(temp_dir, busy={'queues': {
                'tasks': {'active': True},
                'project': {'active': True}
            }})

            # Should not raise an exception
            with self.patchout(), self.patcherr():
                try:
                    app.parse_run('add', '-q', 'project', 'test task')
                except BusyError:
                    self.fail("BusyError was raised for active queue")

    def test_active_queue_setting_blocks_inactive_queue(self):
        """Test that a queue marked as active=false cannot be used"""
        with TemporaryDirectory() as temp_dir:
            # Create app with fake config that has inactive queue setting
            app = self._setup_app_with_config(temp_dir, busy={'queues': {
                'tasks': {'active': True},
                'old': {'active': False}
            }})

            # Should raise BusyError
            with self.patchout(), self.patcherr():
                with self.assertRaises(BusyError):
                    app.parse_run('add', '-q', 'old', 'test task')

    # def test_queue_active_true_is_default(self):
    #     """Test that queues are active by default (true is default)"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with config that doesn't explicitly set active
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': {},  # No active setting
    #             'project': {}  # No active setting
    #         }})

    #         # Should not raise an exception (default is active)
    #         with self.patchout(), self.patcherr():
    #             try:
    #                 app.parse_run('add', '-q', 'project', 'test task')
    #             except BusyError:
    #                 self.fail("BusyError was raised for queue with default "
    #                           "active setting")

    # def test_boolean_value_indicates_inactive(self):
    #     """Test the shorthand boolean syntax: old: false"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with config using boolean shorthand
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': True,  # Active using boolean
    #             'old': False    # Inactive using boolean
    #         }})

    #         # Should raise BusyError
    #         with self.patchout(), self.patcherr():
    #             with self.assertRaises(BusyError):
    #                 app.parse_run('add', '-q', 'old', 'test task')

    # def test_catch_all_queue_blocks_arbitrary_names(self):
    #     """Test catch-all queue setting blocks arbitrary queue names"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with config that has catch-all setting
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': {'active': True},
    #             '_': {'active': False}  # Catch-all blocks arbitrary names
    #         }})

    #         # Should raise BusyError
    #         with self.patchout(), self.patcherr():
    #             with self.assertRaises(BusyError):
    #                 app.parse_run('add', '-q', 'arbitrary', 'test task')

    def test_no_config_allows_all_queues(self):
        """Test that when no queue config exists, all queues are allowed"""
        with TemporaryDirectory() as temp_dir:
            # Create app with no queue configuration
            app = self._setup_app_with_config(temp_dir)
            # No queues config at all

            # Should not raise an exception
            with self.patchout(), self.patcherr():
                try:
                    app.parse_run('add', '-q', 'anyqueue', 'test task')
                except BusyError:
                    self.fail(
                        "BusyError was raised when no queue config exists")

    # def test_boolean_true_allows_queue(self):
    #     """Test the shorthand boolean syntax: tasks: true"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with config using boolean shorthand for active
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': True,    # Active using boolean
    #             'project': True   # Active using boolean
    #         }})

    #         # Should not raise an exception
    #         with self.patchout(), self.patcherr():
    #             try:
    #                 app.parse_run('add', '-q', 'project', 'test task')
    #             except BusyError:
    #                 self.fail("BusyError was raised for boolean true queue "
    #                           "setting")

    # def test_active_tag_setting_allows_active_tag(self):
    #     """Test that a tag marked as active=true can be used"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with fake config that has active tag setting
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': {
    #                 'tags': {
    #                     'main': {'active': True},
    #                     'work': {'active': True}
    #                 }
    #             }
    #         }})

    #         # Should not raise an exception
    #         with self.patchout(), self.patcherr():
    #             try:
    #                 app.parse_run('add', 'test task #work')
    #             except BusyError:
    #                 self.fail("BusyError was raised for active tag")

    # def test_active_tag_setting_blocks_inactive_tag(self):
    #     """Test that a tag marked as active=false cannot be used"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with fake config that has inactive tag setting
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': {
    #                 'tags': {
    #                     'main': {'active': True},
    #                     'old': {'active': False}
    #                 }
    #             }
    #         }})

    #         # Should raise BusyError with specific message
    #         with self.patchout(), self.patcherr():
    #             with self.assertRaises(BusyError):
    #                 app.parse_run('add', 'test task #old')

    # def test_tag_active_true_is_default(self):
    #     """Test that tags are active by default (true is default)"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with config that doesn't explicitly set active
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': {
    #                 'tags': {
    #                     'main': {},  # No active setting
    #                     'work': {}   # No active setting
    #                 }
    #             }
    #         }})

    #         # Should not raise an exception (default is active)
    #         with self.patchout(), self.patcherr():
    #             try:
    #                 app.parse_run('add', 'test task #work')
    #             except BusyError:
    #                 self.fail("BusyError was raised for tag with default "
    #                           "active setting")

    # def test_tag_boolean_value_indicates_inactive(self):
    #     """Test the shorthand boolean syntax for tags: old: false"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with config using boolean shorthand
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': {
    #                 'tags': {
    #                     'main': True,  # Active using boolean
    #                     'old': False   # Inactive using boolean
    #                 }
    #             }
    #         }})

    #         # Should raise BusyError
    #         with self.patchout(), self.patcherr():
    #             with self.assertRaises(BusyError):
    #                 app.parse_run('add', 'test task #old')

    # def test_catch_all_tag_blocks_arbitrary_tags(self):
    #     """Test catch-all tag setting blocks arbitrary tag names"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with config that has catch-all tag setting
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': {
    #                 'tags': {
    #                     'main': {'active': True},
    #                     # Catch-all blocks arbitrary
    #                     '_': {'active': False}
    #                 }
    #             }
    #         }})

    #         # Should raise BusyError
    #         with self.patchout(), self.patcherr():
    #             with self.assertRaises(BusyError):
    #                 app.parse_run('add', 'test task #arbitrary')

    # def test_no_tag_config_allows_all_tags(self):
    #     """Test that when no tag config exists, all tags are allowed"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with no tag configuration
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': {}  # No tags config
    #         }})

    #         # Should not raise an exception
    #         with self.patchout(), self.patcherr():
    #             try:
    #                 app.parse_run('add', 'test task #anytag')
    #             except BusyError:
    #                 self.fail("BusyError was raised when no
    # tag config exists")

    # def test_tag_boolean_true_allows_tag(self):
    #     """Test the shorthand boolean syntax for tags: main: true"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with config using boolean shorthand for active
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': {
    #                 'tags': {
    #                     'main': True,  # Active using boolean
    #                     'work': True   # Active using boolean
    #                 }
    #             }
    #         }})

    #         # Should not raise an exception
    #         with self.patchout(), self.patcherr():
    #             try:
    #                 app.parse_run('add', 'test task #work')
    #             except BusyError:
    #                 self.fail("BusyError was raised for boolean true tag "
    #                           "setting")

    # def test_multiple_tags_validation(self):
    #     """Test that all tags in an item are validated"""
    #     with TemporaryDirectory() as temp_dir:
    #         # Create app with mixed tag settings
    #         app = self._setup_app_with_config(temp_dir, busy={'queues': {
    #             'tasks': {
    #                 'tags': {
    #                     'main': True,
    #                     'old': False,
    #                     'work': True
    #                 }
    #             }
    #         }})

    #         # Should raise BusyError when one tag is inactive
    #         with self.patchout(), self.patcherr():
    #             with self.assertRaises(BusyError):
    #                 app.parse_run('add', 'test task #main #old #work')
