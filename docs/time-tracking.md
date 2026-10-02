# Time tracking

Busy keeps track of how long you spend on the current task, and records it in the list of completed tasks. It only works on the `tasks` (default) queue and only works in minutes.

The elapsed time is stored in the task markup using `!e` and is visible with the `busy describe` command.

For reporting, Busy can optionally apply a multiplier to the clock-minutes for e.g. invoicing (basic theory is that clock time at keyboard is only a part of overall value). The multiplier lives in the busy configuration.

At the bottom of `busy list`, see the total value (time*multiplier) for the queried tasks.

Works great with the new `donemin:` and `donemax:` filters, for example:

`busy list -s done donemin:2024-10-12 donemax:2024-10-18 myclient`

The timing system records the "start" time (basically clock time as of the last busy command) in the queue, then updates elapsed time when the next command runs. So while it gives the impression of a running clock, it's really just subtracting.

Also note that tasks without text (i.e. purely tags) don't record time. Use them for gaps in your day. For example, I use a task called simply `#pause` for breaks and such.

## Ready to get Busy?
