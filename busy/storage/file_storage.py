import fcntl
import os
import re
import time
from dataclasses import dataclass
from io import IOBase
from pathlib import Path

from busy.error import BusyError
from busy.model.collection import Collection
from busy.storage import Storage
from busy.util.identifier import Identifier

STATES = Collection.family_attrs('state')
RE_QUEUE = re.compile(f"([a-zA-Z0-9\\-]+)\\.({'|'.join(STATES)})\\.psv")
LOCK_FILENAME = '.lock'
DEFAULT_LOCK_TIMEOUT = 5.0
LOCK_POLL_INTERVAL = 0.05


class FileStorage(Storage):

    """Queue files in a directory.

    An exclusive lock on `<directory>/.lock` is held from the first collection
    load until the cache is saved (or released), so that concurrent Busy
    processes can't overwrite each other's changes. If the lock is held
    elsewhere for longer than `lock_timeout` seconds, BusyError is raised."""

    def __init__(self, path: str, identifier: Identifier = None,
                 lock_timeout: float = None):
        self.directory = Path(path) if isinstance(path, str) else path
        self.directory.mkdir(parents=True, exist_ok=True)
        assert isinstance(self.directory, Path) and self.directory.is_dir()
        self.cache = {}
        self.identifier = identifier
        if lock_timeout is None:
            lock_timeout = DEFAULT_LOCK_TIMEOUT
        try:
            self.lock_timeout = float(lock_timeout)
        except (TypeError, ValueError):
            raise BusyError(f"Invalid lock timeout {lock_timeout!r}; " +
                            "busy-lock-timeout must be a number of seconds")
        if self.lock_timeout < 0:
            raise BusyError("busy-lock-timeout can't be negative")
        self._lock_file = None

    @property
    def lock_path(self) -> Path:
        return self.directory / LOCK_FILENAME

    @property
    def locked(self) -> bool:
        """Whether this storage object currently holds the lock"""
        return self._lock_file is not None

    def acquire(self):
        """Take the exclusive storage lock; no-op if already held"""
        if self.locked:
            return
        file = open(self.lock_path, 'a+')
        deadline = time.monotonic() + self.lock_timeout
        while True:
            try:
                fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    file.close()
                    raise BusyError(
                        f"Timed out after {self.lock_timeout:g}s waiting " +
                        f"for the lock on {self.lock_path}; another busy " +
                        "process (perhaps an open edit or manage session) " +
                        "is using the data. Try again when it finishes.")
                time.sleep(LOCK_POLL_INTERVAL)
        self._lock_file = file

    def release(self):
        """Release the storage lock, discarding any unsaved cached
        collections (they can't be trusted once another process can write)"""
        self.cache.clear()
        if self.locked:
            file, self._lock_file = self._lock_file, None
            try:
                fcntl.flock(file.fileno(), fcntl.LOCK_UN)
            finally:
                file.close()

    def __del__(self):
        if getattr(self, '_lock_file', None) is not None:
            self.release()

    def filepath(self, queue: str, state: str) -> str:
        return self.directory / f"{queue}.{state}.psv"

    def get_collection(self, queue: str, state: str = 'todo'):
        cache_key = (queue, state)
        if cache_key not in self.cache:
            self.acquire()
            collection = Collection.family_member('state', state)()
            path = self.filepath(queue, state)
            if path.is_file():
                with open(path) as file:
                    collection.read_items(file, identifier=self.identifier,
                                          from_storage=True)
            self.cache[cache_key] = collection
        return self.cache[cache_key]

    def queue_exists(self, queue: str):
        collections = [self.get_collection(queue, s) for s in STATES]
        return any(len(c) for c in collections)

    @property
    def queue_names(self):
        """Return names of queues. Cache nothing."""
        result = set()
        for path in self.directory.iterdir():
            if path.is_file() and (match := RE_QUEUE.match(path.name)):
                queue = match.groups()[0]
                if (queue not in result) and path.stat().st_size:
                    result.add(queue)
        return result

    def save(self):
        """Save any changes, clear the cache, and release the lock"""
        try:
            while self.cache:
                key, collection = self.cache.popitem()
                if collection.changed:
                    path = self.filepath(*key)
                    with open(path, 'w') as file:
                        collection.write_items(file,
                                               identifier=self.identifier)
        finally:
            self.release()
