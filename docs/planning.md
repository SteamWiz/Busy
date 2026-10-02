# Planning

## Doing things later

Busy supports several specific commands related to planning -- that is, scheduling tasks for the future. They are `done`, `defer`, and `activate`. The task-specific commands handle items in the `plan` state and, in some cases, the `done` state.

The task commands accept filters. The `done` and `defer` commands reference the `todo` collection; the `activate` command references the `plan` collection. The default for `done` and `defer` is the top item in the collection; the default for `activate` is to activate only plans deferred to today or earlier.

## Planning by date

Planning is by date, not time, and is relative to the current date according to the system clock.

There are two ways to add items to your plan:
- Using the `defer` command to move existing items from the `todo` collection to the `plan` collection
- Using the `add` command with a `--when` option to create new items directly in the `plan` collection

In the `done` command, the date can be specified using the `--defer` option (or by inputting a value after issuing the command). If the option is omitted, then the date can be provided as input during confirmation.

The date may take any of the following forms:

- A specific date in `YYYY-MM-DD` format, such as `2018-10-28`. Slashes are
  also acceptable, but the order is always year, then month, then day.
- A specific date without the year in `MM-DD` format, such as `7-4`, which will defer the item to that date in the future (even if it's in the next year).
- A specific day of the month as a simple integer, such as `12`, which will defer the item to that day of the month, in either the current month or the next month.
- An integer, a space, and the word `day` or `days`, such as `4 days`, which will defer the item to that number of days from today.
- An integer without a space and the letter `d`, such as `4d`, which is a short form of `4 days`.
- The word `tomorrow`, which is also the default if no date is provided.
- The word `today`, which is useful for activating tasks later in the day.

As examples:

```
# Defer existing tasks 4, 5, and 6 to 4 days from today
busy defer 4-6 -w "4 days"

# Add a new task directly to the plan collection for tomorrow
busy add "Call the dentist" --when tomorrow
```

Note that the `plan` collection keep the task information from the `todo` collection along with the date information (as an absolute date).

To pull tasks from the `plan` collection and put them back into the `todo` collection, use the `activate` command. There are two ways to use the `activate` command:

- With no filter, in which case Busy activates all the tasks scheduled for today or earlier, bringing the `todo` list up to date
- With designated items from the `plan` collection; note that the `activate` command accepts item designation from the `plan` queue itself so use `busy list -s plan` first to get the right list.


## Finishing and repeating

The `done` command removes the designated Task (or the top task if none is designated) from the `todo` state  and adds it to the `done` state, with today's date to indicate when it was completed.

Optionally, a task can have a repeat value by adding a right angle bracket a relative date phrase (same as with the `defer` command).

- `check email > 1 day`
- `phone mom > sunday`
- `balance the checkbook > 6`

The `done` command uses the repeat value as the default for its iteration.

## Ready to get Busy?

Go deep with [BusyML](busyml.md).
