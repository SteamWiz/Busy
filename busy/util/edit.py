# Call the system editor

import os
from io import StringIO
from subprocess import run
from tempfile import NamedTemporaryFile

from busy.model.collection import Collection


def edit_text(text: str, command: str):
    # Write the initial text, then close the file *before* launching the
    # editor. Many editors (vim by default among them) save changes by
    # writing a new file and renaming it over the original path, rather
    # than overwriting the original inode in place. If we kept our own
    # file descriptor open across the edit and read from it afterward, it
    # would still point at the old (now orphaned) inode and return the
    # unedited text - silently discarding the user's changes. Reopening
    # the path fresh after the editor exits ensures we always read
    # whatever the editor actually left on disk.
    with NamedTemporaryFile(mode="w+", delete=False) as tempfile:
        tempfile.write(text)
        name = tempfile.name
    try:
        run([command, name])
        with open(name) as editedfile:
            return editedfile.read()
    finally:
        os.unlink(name)


def edit_items(collection: Collection, indices, command):
    with StringIO() as oldio:
        collection.write_items(oldio, indices)
        oldio.seek(0)
        oldtext = oldio.read()
    newtext = edit_text(oldtext, command)
    with StringIO() as newio:
        newio.write(newtext)
        newio.seek(0)
        newitems = collection.read_items(newio, indices)
    return newitems
