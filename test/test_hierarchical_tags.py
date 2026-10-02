from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest.mock import patch
from busy import BusyApp
from busy.error import BusyError
from busy.test_case import BusyTestCase


class TestHierarchicalTags(BusyTestCase):

    def test_nested_tag_configuration_parsing(self):
        """Test that nested tag configuration can be parsed"""
        with TemporaryDirectory() as dir:
            with self.patchout(), self.patcherr():
                with NamedTemporaryFile(mode='w') as config:
                    yaml = f"""busy:
  storage:
    directory: {dir}
  queues:
    tasks:
      tags:
        project:
          tags:
            wizlib:
            busy:
            vernum:
        trackable:
          tags:
            development:
            research:
            admin:
              tags:
                finance:
                personnel:
                facilities:
"""
                    config.write(yaml)
                    config.seek(0)
                    app = BusyApp(config=config.name)

                    queue = app.queues['tasks']
                    self.assertIsNotNone(queue.get_tag('project'))
                    self.assertIsNotNone(
                        queue.get_tag('project').get_tag('busy'))

    def test_add_invalid_tag_parent(self):
        y = "Queue 'a' requires items with tag 'c' to have parent tag 'b'"
        with TemporaryDirectory() as temp_dir:
            a = BusyApp(config={'busy': {
                'queues': {
                    'a': {'tags': {'b': {'tags': {'c': True}}}}
                },
                'storage': {'directory': temp_dir}
            }})
            try:
                a.parse_run('add', '-q', 'a', 'something #c')
            except BusyError as e:
                self.assertIn(y, str(e))

    def test_add_invalid_tag_missing(self):
        y = "Queue 'a' requires items with tag 'b' to have exactly one of 'c'"
        with TemporaryDirectory() as temp_dir:
            a = BusyApp(config={'busy': {
                'queues': {
                    'a': {'tags': {'b': {'tags': {'c': True}}}}
                },
                'storage': {'directory': temp_dir}
            }})
            with self.assertRaises(BusyError) as context:
                a.parse_run('add', '-q', 'a', 'something #b')
            self.assertIn(y, str(context.exception))

    def test_invalid_tag_more_than_one_child(self):
        y = "Queue 'a' requires items with tag 'b' to have " + \
            "exactly one of 'c' 'd'"
        with TemporaryDirectory() as temp_dir:
            a = BusyApp(config={'busy': {
                'queues': {
                    'a': {'tags': {'b': {'tags': {'c': True, 'd': True}}}}
                },
                'storage': {'directory': temp_dir}
            }})
            with self.assertRaises(BusyError) as context:
                a.parse_run('add', '-q', 'a', 'something #b #c #d')
            self.assertIn(y, str(context.exception))

    def test_edit_invalid_tag_parent(self):
        y = "Queue 'a' requires items with tag 'c' to have parent tag 'b'"
        with TemporaryDirectory() as temp_dir:
            a = BusyApp(config={'busy': {
                'queues': {
                    'a': {'tags': {'b': {'tags': {'c': True}}}}
                },
                'storage': {'directory': temp_dir}
            }})
            a.parse_run('add', '-q', 'a', 'x')
            with patch('busy.util.edit.edit_text', lambda s, i: 'x #c\n'), \
                    self.assertRaises(BusyError) as context:
                a.parse_run('edit', '-q', 'a')
            self.assertIn(y, str(context.exception))


#     def test_parent_tag_requires_exactly_one_child_tag(self):
#         """Test that parent tag requires exactly one child tag"""
#         with TemporaryDirectory() as dir:
#             with self.patchout(), self.patcherr():
#                 with NamedTemporaryFile(mode='w') as config:
#                     yaml = f"""busy:
#   storage:
#     directory: {dir}
#   queues:
#     tasks:
#       tags:
#         project:
#           tags:
#             wizlib:
#             busy:
#             vernum:
# """
#                     config.write(yaml)
#                     config.seek(0)
#                     app = BusyApp(config=config.name)

#                     # Should raise BusyError when parent has no child
#                     with self.assertRaises(BusyError) as cm:
#                         app.parse_run('add', 'test task #project')
#                     self.assertIn(
#                         'tag interdependency validation violations',
#                         str(cm.exception))

#     def test_child_tag_requires_parent(self):
#         """Test that child tag requires parent tag"""
#         with TemporaryDirectory() as dir:
#             with self.patchout(), self.patcherr():
#                 with NamedTemporaryFile(mode='w') as config:
#                     yaml = f"""busy:
#   storage:
#     directory: {dir}
#   queues:
#     tasks:
#       tags:
#         project:
#           tags:
#             wizlib:
#             busy:
#             vernum:
# """
#                     config.write(yaml)
#                     config.seek(0)
#                     app = BusyApp(config=config.name)

#                     # Should raise BusyError when child has no parent
#                     with self.assertRaises(BusyError) as cm:
#                         app.parse_run('add', 'test task #wizlib')
#                     self.assertIn(
#                         'tag interdependency validation violations',
#                         str(cm.exception))

#     def test_valid_parent_child_combination(self):
#         """Test that valid parent-child combinations work"""
#         with TemporaryDirectory() as dir:
#             with self.patchout(), self.patcherr():
#                 with NamedTemporaryFile(mode='w') as config:
#                     yaml = f"""busy:
#   storage:
#     directory: {dir}
#   queues:
#     tasks:
#       tags:
#         project:
#           tags:
#             wizlib:
#             busy:
#             vernum:
# """
#                     config.write(yaml)
#                     config.seek(0)
#                     app = BusyApp(config=config.name)

#                     # Should not raise an exception for valid combination
#                     try:
#                         app.parse_run('add', 'test task #project #wizlib')
#                     except BusyError:
#                         self.fail(
#                             "BusyError raised for valid " +
#                             "parent-child combination")

#     def test_parent_with_multiple_children_fails(self):
#         """Test that parent with multiple children fails validation"""
#         with TemporaryDirectory() as dir:
#             with self.patchout(), self.patcherr():
#                 with NamedTemporaryFile(mode='w') as config:
#                     yaml = f"""busy:
#   storage:
#     directory: {dir}
#   queues:
#     tasks:
#       tags:
#         project:
#           tags:
#             wizlib:
#             busy:
#             vernum:
# """
#                     config.write(yaml)
#                     config.seek(0)
#                     app = BusyApp(config=config.name)

#                     # Should raise BusyError when parent
# has multiple children
#                     with self.assertRaises(BusyError) as cm:
#                         app.parse_run(
#                             'add', 'test task #project #wizlib #busy')
#                     self.assertIn(
#                         'tag interdependency validation violations',
#                         str(cm.exception))

#     def test_done_command_validates_tag_interdependencies(self):
#         """Test that done command validates tag interdependencies"""
#         with TemporaryDirectory() as dir:
#             with self.patchout(), self.patcherr():
#                 with NamedTemporaryFile(mode='w') as config:
#                     yaml = f"""busy:
#   storage:
#     directory: {dir}
#   queues:
#     tasks:
#       tags:
#         project:
#           tags:
#             wizlib:
#             busy:
#             vernum:
# """
#                     config.write(yaml)
#                     config.seek(0)
#                     app = BusyApp(config=config.name)

#                     # Add a valid item first
#                     app.parse_run('add', 'test task #project #wizlib')

#                     # Now manually create an invalid item by editing the file
#                     # (simulating an item that became invalid)
#                     with open(Path(dir) / 'tasks.todo.psv', 'w') as f:
#                         f.write('?000001 invalid task #project\n')

#                     # Should raise BusyError when trying to mark done
#                     with self.assertRaises(BusyError) as cm:
#                         app.parse_run('done', '1', '-y')
#                     self.assertIn(
#                         'tag interdependency validation violations',
#                         str(cm.exception))

#     def test_defer_command_validates_tag_interdependencies(self):
#         """Test that defer command validates tag interdependencies"""
#         with TemporaryDirectory() as dir:
#             with self.patchout(), self.patcherr():
#                 with NamedTemporaryFile(mode='w') as config:
#                     yaml = f"""busy:
#   storage:
#     directory: {dir}
#   queues:
#     tasks:
#       tags:
#         project:
#           tags:
#             wizlib:
#             busy:
#             vernum:
# """
#                     config.write(yaml)
#                     config.seek(0)
#                     app = BusyApp(config=config.name)

#                     # Add a valid item first
#                     app.parse_run('add', 'test task #project #wizlib')

#                     # Now manually create an invalid item by editing the file
#                     # (simulating an item that became invalid)
#                     with open(Path(dir) / 'tasks.todo.psv', 'w') as f:
#                         f.write('?000001 invalid task #project\n')

#                     # Should raise BusyError when trying to defer
#                     with self.assertRaises(BusyError) as cm:
#                         app.parse_run('defer', '1', '-w', 'tomorrow', '-y')
#                     self.assertIn(
#                         'tag interdependency validation violations',
#                         str(cm.exception))

#     def test_activate_command_validates_tag_interdependencies(self):
#         """Test that activate command validates tag interdependencies"""
#         with TemporaryDirectory() as dir:
#             with self.patchout(), self.patcherr():
#                 with NamedTemporaryFile(mode='w') as config:
#                     yaml = f"""busy:
#   storage:
#     directory: {dir}
#   queues:
#     tasks:
#       tags:
#         project:
#           tags:
#             wizlib:
#             busy:
#             vernum:
# """
#                     config.write(yaml)
#                     config.seek(0)
#                     app = BusyApp(config=config.name)

#                     # Add a valid item to plan first
#                     app.parse_run(
#                         'add', 'test task #project #wizlib', '-w',
#  'tomorrow')

#                     # Now manually create an invalid item in plan
#                     # (simulating an item that became invalid)
#                     with open(Path(dir) / 'tasks.plan.psv', 'w') as f:
#                         f.write('2025-01-01|?000001 invalid task #project\n')

#                     # Should raise BusyError when trying to activate
#                     with self.assertRaises(BusyError) as cm:
#                         app.parse_run('activate', '1', '-y')
#                     self.assertIn(
#                         'tag interdependency validation violations',
#                         str(cm.exception))

#     def test_unique_definition_validation_blocks_duplicate_tags(self):
#         """Test that tags cannot be defined in multiple places within one
#         queue"""
#         with TemporaryDirectory() as dir:
#             with self.patchout(), self.patcherr():
#                 with NamedTemporaryFile(mode='w') as config:
#                     yaml = f"""busy:
#   storage:
#     directory: {dir}
#   queues:
#     tasks:
#       tags:
#         project:
#           tags:
#             wizlib:
#         trackable:
#           tags:
#             wizlib:  # Duplicate definition of wizlib
# """
#                     config.write(yaml)
#                     config.seek(0)

#                     # Should raise BusyError when loading configuration
#                     with self.assertRaises(BusyError) as cm:
#                         app = BusyApp(config=config.name)
#                     self.assertIn('duplicate tag definition',
#                                   str(cm.exception).lower())

#     def test_unique_definition_val_allows_cross_queue_duplicates(self):
#         """Test that tags can be defined in multiple queues"""
#         with TemporaryDirectory() as dir:
#             with self.patchout(), self.patcherr():
#                 with NamedTemporaryFile(mode='w') as config:
#                     yaml = f"""busy:
#   storage:
#     directory: {dir}
#   queues:
#     tasks:
#       tags:
#         project:
#           tags:
#             wizlib:
#     friends:
#       tags:
#         interests:
#           tags:
#             wizlib:  # Same tag name but different queue - should be allowed
# """
#                     config.write(yaml)
#                     config.seek(0)

#                     # Should not raise an exception
#                     try:
#                         app = BusyApp(config=config.name)
#                     except BusyError:
#                         self.fail(
#                             "BusyError raised for cross-queue
#  duplicate tags")
