# Editing and Storage

## Text editor integration

The `edit` and `manage` commands launch the user's default text editor to directly edit a task, the whole queue, or part of a queue. Note that `edit` and `manage` are identical commands except for their default filter.

A text editor can be designated in a configuration file (`.busy.yml`) otherwise Busy uses Emacs.

The `edit` command with no filter will edit the top item in the list, and the `manage` command with no filter will edit the entire list. But it's also possible to designate items to be edited with both commands using a filter. The commands do their best to replace the edited items in place in the list order. So if you `edit` or `manage` a tag whose items are recently popped (at the top of the collection), then the edited items will still appear at the top. Even if you add items, they will be inserted after the last item in the edited set, not at the end of the queue. But all the items brought up in the editor will be edited. So if you remove an item in the editor, it will be deleted and the others will be moved up to take its place.

The editing process includes the full markup in [BusyML](busyml.md).

## Data storage

Busy keeps the collections in plain text files, so if the tool doesn't do something you want, you may edit the files. The files are in a directory together, referred to as the "root". Each file is the named according to the following convention:

```
<queue>.<state>.psv
```

If a required file is missing, it will be created automatically. So typically, the root includes `tasks.todo.psv`, `tasks.plan.psv`, `tasks.done.txt`, and any number of custom queue files.

Technically, Busy data files are pipe-delimited data files, though the `todo` collections only have one field ("markup") while the `plan` and `done` files have only two fields (date and markup).

Busy is not a database (yet). There is no support for managing separate fields in the Busy tool itself.

The default location for the files is a directory at `~/.busy`, which will be generated as needed. Specify an alternative location using the `--config` option referencing a YAML file with the following format:

```yaml
busy:
  storage:
    directory: /some/other/directory
```

## Configuration

Busy supports additional configuration options in the `.busy.yml` file to control queue and tag access.

### Queue Access Control

You can control which queues are available for use. This is useful for preventing accidental use of archived queues or enforcing team workflows.

```yaml
busy:
  queues:
    tasks: true          # Allow the tasks queue
    shopping: true       # Allow the shopping queue
    archived: false      # Block the archived queue
    _: false            # Block any other queue names
```

**Configuration formats:**

- **Boolean shorthand**: `tasks: true` or `tasks: false`
- **Explicit format**: `tasks: { active: true }` or `tasks: { active: false }`
- **Catch-all pattern**: Use `_: false` to block any queue names not explicitly listed. Note that when an unlisted queue is blocked this way, the error will read "Queue _ is inactive" rather than naming the specific queue.

**Default behavior**: When no queue configuration exists, all queue names are allowed.

For tag-specific configuration including access control and hierarchical tag relationships, see [Tag configuration](tag-configuration.md).

Note that Busy does not support concurrency or locking in any form. If two commands are executing at the same time, they might overwrite each other. Overwriting is especially risky with the `edit` and `manage` commands, which keeps the user's editor open until they close it.

The format is designed to be simple but not idiot-proof. Experimentation might result in unintended consequences.

## Ready to get Busy?

Advance with [Time tracking](time-tracking.md).
