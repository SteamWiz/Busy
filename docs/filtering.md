# Filtering and Selection

## Sequence numbers

Sequence numbers appear in the output from the `list` command. Note that the numbering starts with 1, and is not an ID -- the number of a item will change when the collection is modified. So always reference the most recent output from the `list` command.

Sequence numbers are used with filters. To designate more than one item, separate the sequence numbers with a space.

Another choice is ranges. A range of sequence numbers is separated by a hyphen, with no whitespace, and is inclusive. For example, `4-6` designates items 4, 5, and 6. A hyphen without a number after it includes all the items from that item to the end of the queue. A hyphen on its own indicates the last item in the queue.

Below are some examples of task designations by sequence number.

- `busy pop 5` pops item number 5
- `busy drop 3-7` drops items 3 through 7 (4 items)
- `busy list 3-` lists all the items from number 3 through the end of the list
- `busy delete  3 5 7 9` deletes only the items designated
- `busy defer -` defers the last task
- `busy edit -4` is an error! Use `busy edit 1-4` instead
- `busy manage` allows you to edit the entire queue

Items will always be handled in the order they appear in the queue, regardless of the order the filter are provided. So for example, if a `pop` command designates some items, they will be moved to the top of the queue in the order, relative to each other, they currently appear in the queue.

The sequence numbers in the `list` command output are from the collection itself. So the `list` command does not modify the sequence numbers, even when item designation is applied.

## Tags

[BusyML](busyml.md) includes tags as words in item markup starting with `#`.

Tags may be used as filter in addition to sequence numbers. For example, the following command will move all the items with the `#errands` tag to the top of the queue.

```
busy pop errands
```

Numerical filters use OR logic with each other, and tag filters use OR logic with each other. But AND logic applies between the two types. For example, the command below deletes tasks in the range 1-10 that have either the admin or sales tag.

```
busy delete 1-10 admin sales
```

To use AND logic with tags in filters, combine them with a plus (+). For example, the command below lists tasks that are tagged both daily and admin.

```
busy list daily+admin
```

To exclude items that have a specific tag, prefix the tag with a tilde (`~`). For example, the command below lists tasks tagged `admin` but not `done`.

```
busy list admin ~done
```

Multiple exclusions may be combined. The command below lists tasks tagged `admin` that have neither `done` nor `blocked`.

```
busy list admin ~done ~blocked
```

## Named Filters

Certain data fields support named filters using a colon syntax in the command.

- `planmin:2024-09-28` for the `plan` collections to specify the lowest plan date
- `planmax:2024-09-28` for the `plan` collections to specify the highest plan date
- `donemin:2024-09-28` for the `done` collections to specify the lowest done date
- `donemax:2024-09-28` for the `done` collections to specify the highest done date
- `val:i456` for any collection to specify a data value
- `grep:pattern` for any collection to filter items whose text matches a pattern (case-insensitive)

Example:

`busy list -s done donemin:2024-11-11 client awesomeco val:i456`

The `grep` filter performs a case-insensitive search against the item text (including tags). It supports regular expression patterns. For example:

```
busy list grep:reconcile
busy view grep:Chase.*Visa
```

## Ready to get Busy?

Dig into [Planning](planning.md) capabilities.
