# Commands

## List of commands

Output commands:

- `describe` provides the full BusyML markup
- `simple` includes less detail than `describe`
- `list` is like `describe` but with sequence numbers
- `view` outputs specific fields - for now only the `val` fields
- `dump` outputs items as YAML with same filtering as view command
- `queues` to lists all the queues
- `tags` to lists tags from a queue

Commands that make changes:

- `add` adds a new item
- `done` marks an item as 'done' and gives the option of iterating - "done for today"
- `defer` puts a task or set of items on the plan for a future date
- `pop` moves a task or set of items to the top of a queue - "pop it to the top"
- `drop` moves a task or set of items to the bottom of a queue - "drop it to the bottom"
- `pick` moves one random item from the filtered set to the top of the queue - "pick one for me"
- `pop1` moves the topmost matching item from the filtered set to the top of the queue
- `delete` permanently removes a task or set of items from a queue
- `edit` opens a text editor to edit items - the default is to edit only the top item
- `manage` is the same as `edit`, but defaults to edit the whole collection
- `activate` finds everything planned for today and adds it to the list - "activate my day"
- `update` modifies fields on a filtered set of items (e.g. add tags)

## Common options

- filters to designate items to be acted upon, using sequence numbers or tags
- the `add` command requires markup of the new item instead of filters
- `--queue` if not the default `tasks` queue
- `--help` to find out which options apply
- `--yes` to skip confirmation of any command that requires it
- `--state` to work on Items of a different state (`todo`, `plan`, `done`)
- `--when` applies to the `defer` and `add` commands
- `--defer` applies to the `done` command
- `--fields` and `--unique` apply to the `view` command
- `--add-tag` applies to the `update` command (may be specified multiple times)
- `--set-val` applies to the `update` command (may be specified multiple times)

## Default item designations

For the most part, commands that accept item designations default to only act on the top item in the queue. The exceptions are:

- `list` and `manage` default to handle the entire collection
- `pop` defaults to pop the last item in the collection to the top
- `activate` defaults to activate `plan` items for today (more on that below)
- `add` adds to the bottom of the `todo` queue

## Alternate queues

Busy will manage any number of queues, which are entirely separate sets of items. For example, you might have a `shopping` queue for items to buy at the store, and a `movies` queue for films you'd like to watch. The default queue is called `tasks`.

To designate an alternate queue, use the `--queue` or `-q` option. For example:

```
busy add --queue shopping -d "Skimmed Milk"
busy list -q movies
```

## Ready to get busy?

Learn about [Filtering and Selection](filtering.md)
