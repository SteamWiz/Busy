from functools import cached_property
from pathlib import Path

from wizlib.app import WizApp
from wizlib.ui_handler import UIHandler
from wizlib.config_handler import ConfigHandler

from busy.command import BusyCommand
from busy.storage.file_storage import FileStorage
from busy.util.identifier import Identifier
from busy.model.configured import ConfiguredQueue


class BusyApp(WizApp):
    base = BusyCommand
    name = "busy"
    handlers = [UIHandler, ConfigHandler]

    @cached_property
    def directory(self):
        return self.config.get("busy-storage-directory") or Path.home() / ".busy"

    @cached_property
    def identifier(self):
        identifier_address = self.config.get("busy-identifier-address") or "0"
        return Identifier(identifier_address, self.directory)

    @cached_property
    def storage(self):
        return FileStorage(self.directory, self.identifier)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    @cached_property
    def queues(self):
        if queues_config := self.config.get("busy-queues"):
            return {
                n: ConfiguredQueue.from_config(n, c) for n, c in queues_config.items()
            }
        else:
            return {}

    def get_queue(self, name):
        if name in self.queues:
            return self.queues[name]
        elif "_" in self.queues:
            return self.queues["_"]
        else:
            return ConfiguredQueue(name)

    # def run(self, **vals):
    #     super().run(**vals)
