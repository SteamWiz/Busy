from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from busy import BusyApp
from busy.error import BusyError
from busy.test_case import BusyTestCase


# class TestHierarchicalTagsMissing(BusyTestCase):

# Note: edit command test is skipped because it launches an external editor
# The warning behavior is implemented in the edit command but cannot be
# easily tested

#     def test_list_command_validates_with_warning(self):
#         """Test that list command validates tag interdependencies with
#         warning"""
#         with TemporaryDirectory() as dir:
#             with self.patchout() as out, self.patcherr() as err:
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

#                     # Create an invalid item directly
#                     with open(Path(dir) / 'tasks.todo.psv', 'w') as f:
#                         f.write('?000001 invalid task #project\n')

#                     # List command should NOT raise an
# exception but should
#                     # warn
#                     app.parse_run('list')

#                     # Should have warning in stderr but
# not raise exception
#                     self.assertIn(
#                         'tag interdependency validation violations',
#                         err.getvalue())

#     def test_view_command_validates_with_warning(self):
#         """Test that view command validates tag interdependencies with
#         warning"""
#         with TemporaryDirectory() as dir:
#             with self.patchout() as out, self.patcherr() as err:
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

#                     # Create an invalid item directly
#                     with open(Path(dir) / 'tasks.todo.psv', 'w') as f:
#                         f.write('?000001 invalid task #project\n')

#                     # View command should NOT raise an
# exception but should
#                     # warn
#                     app.parse_run('view', '1')

#                     # Should have warning in stderr but
# not raise exception
#                     self.assertIn(
#                         'tag interdependency validation violations',
#                         err.getvalue())
