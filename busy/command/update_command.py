from wizlib.parser import WizParser

from busy.command import CollectionCommand


class UpdateCommand(CollectionCommand):
    """Update filtered items: add tags, remove tags, or set data vals"""

    name = 'update'
    is_writer = True
    add_tags: list = None
    remove_tags: list = None
    set_vals: list = None

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument(
            '--add-tag', dest='add_tags',
            action='append', metavar='TAG',
            help='Add a tag to all filtered items'
        )
        parser.add_argument(
            '--remove-tag', dest='remove_tags',
            action='append', metavar='TAG',
            help='Remove a tag from all filtered items'
        )
        parser.add_argument(
            '--set-val', dest='set_vals',
            action='append', metavar='VAL',
            help='Set a data val on all filtered items'
        )

    @CollectionCommand.wrap
    def execute(self):
        for item in self.selected_items:
            for tag in (self.add_tags or []):
                item.tags.add(tag.lower())
            for tag in (self.remove_tags or []):
                item.tags.discard(tag.lower())
            for val in (self.set_vals or []):
                item.vals[val[0]] = val[1:]
        self.collection.changed = True
