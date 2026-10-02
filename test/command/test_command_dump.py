import yaml
from datetime import date
from unittest.mock import Mock

from busy import BusyApp
from busy.command.dump_command import DumpCommand
from busy.model.collection.done_collection import DoneCollection
from busy.model.collection.plan_collection import PlanCollection
from busy.model.collection.todo_collection import TodoCollection
from busy.model.item import Item
from busy.test_case import BusyTestCase


class TestCommandDump(BusyTestCase):

    def test_dump_single_item_basic(self):
        """Test basic dump with single item"""
        item = Item.from_markup('Check new Mac prices')
        collection = TodoCollection([item])
        app = Mock()
        app.storage.get_collection.return_value = collection
        command = DumpCommand(app, filter=['1'])
        result = command.execute()

        data = yaml.safe_load(result)
        self.assertEqual(data['tasks'][0]['base'], 'Check new Mac prices')
        self.assertEqual(data['tasks'][0]['state'], 'todo')

    def test_dump_item_with_all_fields(self):
        """Test dump with item containing all possible fields"""
        item = Item.from_markup(
            'Do xyz #shopping @https://apple.com/store %i88 !e14 > sat',
            state='todo')
        collection = TodoCollection([item])
        app = Mock()
        app.storage.get_collection.return_value = collection
        command = DumpCommand(app, filter=['1'])
        result = command.execute()

        data = yaml.safe_load(result)
        item_data = data['tasks'][0]

        self.assertEqual(item_data['base'], 'Do xyz')
        self.assertEqual(item_data['state'], 'todo')
        self.assertIn('shopping', item_data['tags'])
        self.assertEqual(item_data['data']['i'], '88')
        self.assertEqual(item_data['timing']['elapsed'], 14)
        self.assertEqual(item_data['url'], 'https://apple.com/store')
        self.assertEqual(item_data['repeat'], 'sat')

    def test_dump_omits_empty_fields(self):
        """Test that empty fields are omitted from output"""
        item = Item.from_markup('Simple task')
        collection = TodoCollection([item])
        app = Mock()
        app.storage.get_collection.return_value = collection
        command = DumpCommand(app, filter=['1'])
        result = command.execute()

        data = yaml.safe_load(result)
        item_data = data['tasks'][0]

        # Should only have base and state
        self.assertEqual(len(item_data), 2)
        self.assertIn('base', item_data)
        self.assertIn('state', item_data)
        self.assertNotIn('tags', item_data)
        self.assertNotIn('data', item_data)
        self.assertNotIn('timing', item_data)
        self.assertNotIn('url', item_data)
        self.assertNotIn('repeat', item_data)
        self.assertNotIn('dates', item_data)

    def test_dump_with_dates(self):
        """Test dump with done and plan dates"""
        done_item = Item.from_markup('Done task', state='done',
                                     done_date=date(2023, 1, 15))
        plan_item = Item.from_markup('Planned task', state='plan',
                                     plan_date=date(2023, 6, 8))

        # Test done item using BusyApp to avoid Mock issues
        app = BusyApp()
        app.storage = self.mock_storage(
            TodoCollection(),
            PlanCollection(),
            DoneCollection([done_item])
        )

        with self.patchout() as output:
            app.parse_run('dump', '--state', 'done')

        output.seek(0)
        result = output.read()
        data = yaml.safe_load(result)
        self.assertEqual(data['tasks'][0]['dates']['done'], '2023-01-15')

        # Test plan item
        app.storage = self.mock_storage(
            TodoCollection(),
            PlanCollection([plan_item]),
            DoneCollection()
        )

        with self.patchout() as output:
            app.parse_run('dump', '--state', 'plan')

        output.seek(0)
        result = output.read()
        data = yaml.safe_load(result)
        self.assertEqual(data['tasks'][0]['dates']['plan'], '2023-06-08')

    def test_dump_multiple_items(self):
        """Test dump with multiple items"""
        items = [
            Item.from_markup('Task A #tag1'),
            Item.from_markup('Task B #tag2'),
            Item.from_markup('Task C')
        ]
        collection = TodoCollection(items)
        app = Mock()
        app.storage.get_collection.return_value = collection
        command = DumpCommand(app, filter=['1-'])
        result = command.execute()

        data = yaml.safe_load(result)
        self.assertEqual(len(data['tasks']), 3)
        self.assertEqual(data['tasks'][0]['base'], 'Task A')
        self.assertEqual(data['tasks'][1]['base'], 'Task B')
        self.assertEqual(data['tasks'][2]['base'], 'Task C')

    def test_dump_data_type_preservation(self):
        """Test that data values preserve their types"""
        item = Item.from_markup('Task %i42 %f3.14 %stext')
        collection = TodoCollection([item])
        app = Mock()
        app.storage.get_collection.return_value = collection
        command = DumpCommand(app, filter=['1'])
        result = command.execute()

        data = yaml.safe_load(result)
        data_section = data['tasks'][0]['data']

        self.assertEqual(data_section['i'], '42')
        self.assertEqual(data_section['f'], '3.14')
        self.assertEqual(data_section['s'], 'text')  # string

    def test_dump_filtering_works(self):
        """Test that filtering works like view command"""
        items = [
            Item.from_markup('Task A #important'),
            Item.from_markup('Task B #normal'),
            Item.from_markup('Task C #important')
        ]
        collection = TodoCollection(items)
        app = Mock()
        app.storage.get_collection.return_value = collection
        command = DumpCommand(app, filter=['2'])  # Only second item
        result = command.execute()

        data = yaml.safe_load(result)
        self.assertEqual(len(data['tasks']), 1)
        self.assertEqual(data['tasks'][0]['base'], 'Task B')

    def test_dump_multi_state(self):
        """Test dump with multi-state collection"""
        todo_items = [Item.from_markup('Todo task')]
        done_items = [
            Item.from_markup(
                'Done task', state='done', done_date=date(
                    2023, 1, 1))]
        plan_items = [
            Item.from_markup(
                'Plan task', state='plan', plan_date=date(
                    2023, 6, 1))]

        app = BusyApp()
        app.storage = self.mock_storage(
            TodoCollection(todo_items),
            PlanCollection(plan_items),
            DoneCollection(done_items)
        )

        with self.patchout() as output:
            app.parse_run('dump', '--state', 'multi')

        output.seek(0)
        result = output.read()
        data = yaml.safe_load(result)

        # Should have all three items
        self.assertEqual(len(data['tasks']), 3)
        states = [item['state'] for item in data['tasks']]
        self.assertIn('done', states)
        self.assertIn('todo', states)
        self.assertIn('plan', states)

    def test_dump_tags_sorted(self):
        """Test that tags are sorted in output"""
        item = Item.from_markup('Task #zebra #alpha #beta')
        collection = TodoCollection([item])
        app = Mock()
        app.storage.get_collection.return_value = collection
        command = DumpCommand(app, filter=['1'])
        result = command.execute()

        data = yaml.safe_load(result)
        tags = data['tasks'][0]['tags']
        self.assertEqual(tags, ['alpha', 'beta', 'zebra'])

    def test_dump_valid_yaml(self):
        """Test that output is always valid YAML"""
        item = Item.from_markup('Task with "quotes" and special: characters')
        collection = TodoCollection([item])
        app = Mock()
        app.storage.get_collection.return_value = collection
        command = DumpCommand(app, filter=['1'])
        result = command.execute()

        # Should not raise exception
        data = yaml.safe_load(result)
        self.assertIsInstance(data, dict)
        self.assertIn('tasks', data)

    def test_dump_from_run(self):
        """Test dump command through app.parse_run"""
        items = [Item.from_markup('Test task #tag @url')]
        app = BusyApp()
        app.storage = self.mock_storage(
            TodoCollection(items),
            PlanCollection(),
            DoneCollection()
        )

        with self.patchout() as output:
            app.parse_run('dump')

        output.seek(0)
        result = output.read()
        data = yaml.safe_load(result)

        self.assertEqual(data['tasks'][0]['base'], 'Test task')
        self.assertEqual(data['tasks'][0]['tags'], ['tag'])
        self.assertEqual(data['tasks'][0]['url'], 'url')
