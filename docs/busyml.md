# BusyML  markup

Every item in a Busy collection is created and stored using a specific form of markup we call "BusyML".

Loosely, an item's markup contains one or more space-separated **words**, and those works that start with a **marker** indicate some special data field.

The idea is to concentrate useful information in a way that's easy to remember and type.

The markers are:

- `#` - tag
- `%` - data value
- `!` - timing-related data
- `@` - url (only one allowed)
- `>` - repeat timing, special because the marker itself can exist as its own word (i.e. have a space after) - only one allowed
- `?` - unique identifier - created automatically by Busy, so no need to edit or create

All words without markers that appear before the repeat marker are considered the "base" description, and represent the human-readable action or topic of the item.

## Example

`?A003KP Check new Mac prices #shopping #weekend %i88 !e14 @https://apple.com/store > repeat on saturday'

- The unique identifier is A003KP
- The base is "Check new Mac prices"
- Tags are `shopping` and `weekend`
- One data item `i88` (might refer to a GitLab issue, for example)
- 14 minutes of elapsed time
- Related url is the Apple store
- When done, the task will repeat next Saturday

## Tags

Items can have tags, which are space-separated hashtags in the markup. An item can have no tags, one tag, or more than one tag. For example the following item has the tag "errands":

```
go to the supermarket #errands
```

The only punctuation that tags can contain is the hyphen ("-").

Busy supports hierarchical tag relationships where parent tags require specific child tags. For example, with proper configuration, you might require that tasks with `#project` must also have exactly one of `#wizlib`, `#busy`, or `#vernum`:

```
Fix authentication bug #project #wizlib
Review budget #trackable #admin #finance
```

See the [system configuration documentation](system.md#hierarchical-tag-structure) for details on setting up hierarchical tag validation.

## Data values

Data values can be used by integrations to correlate to outside systems. They start with `%` followed immediately by a 1-letter reference to the data value being tracked and (optionally) a value.

It's possible to filter by data vals.

`busy list val:x45`

Use the `view` command to view data values in isolation.

`busy view --fields val.x`

Use the `update` command to set data vals on filtered items.

`busy update --set-val x45`

The `--set-val` option may be specified multiple times to set more than one val at once.

## Timing-related data

The [time tracking subsystem](time-tracking.md) inserts words starting with `!` into tasks. Leave them alone.

## URL

Useful place to bookmark a single URL related to the item

## Repeat timing

Described on the [planning](planning.md) page.

## Ready to get Busy?

Find out how to edit data directly in [Editing and Storage](system.md).
