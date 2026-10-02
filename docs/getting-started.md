# Busy

⚠️ DISCLAIMER: This is a hobby/personal project. Not a commercial product. Not for production use.

## Escape from overwhelm and stay focused all day

Buzz through crazy busy days with as little stress as possible. Stay focused by seeing only one task at a time. Use this simple. fast, fun tool all day with the keyboard in a familiar terminal environment.

## Quick installation (MacOS)

```bash
brew install pipx
pipx install busy
```

## Getting started

To get started, add some tasks to your default queue.

```
busy add 'Donate to the Busy project'
busy add 'Phone mom'
busy add 'Do the laundry'
busy add 'Take a shower'
```

Then, when you're ready to start your day, ask Busy what to do first:

```
busy
```

Returns:

```
Donate to the Busy project
```

That's it! Get to work.

See [commands](commands.md) for details or read on to experiment more.

## Handling tasks

When you've finished that task, mark it off to find the next task.

```
busy done
```

It will ask you to confirm that you're done, then mark the task as done and tell you what to do next.

```
Phone mom
```

If you want to see the whole queue, with sequence numbers, type:

```
busy list
```

Here's the list you will see. Note that the completed Tasks are gone:

```
1  Do the laundry
2  Take a shower
```

If you need to export your tasks as structured data (for integration with other tools), you can use the dump command:

```
busy dump
```

This outputs your tasks in YAML format:

```yaml
tasks:
  - base: "Do the laundry"
    state: "todo"
  - base: "Take a shower"
    state: "todo"
```

See [planning](planning.md) to learn about time management or read on!

## Planning

If you decide, in the moment, to wait until later today to perform a task, drop it to the bottom of the queue using the `drop` command:

```
busy drop
```

If you see a task on the list that seems urgent, and you intend to perform it immediately, pop it to the top of the list:

```
busy pop 2
```

Let's say you realize that it's not an appropriate task for today, but you want to defer it to tomorrow:

```
busy defer
```

It will ask you to confirm "tomorrow" as the day for deferral. Agree with it for now. The Item will then be moved into the `plan` State with tomorrow's date as the plan date. As usual, Busy will tell you what to do next after deferring that task.

You can also add tasks directly to your plan for a future date:

```
busy add "Check car insurance renewal date" --when "next monday"
```

This creates a new task and immediately adds it to your plan for next Monday, skipping the todo queue entirely.

At the start of a new day, tell Busy to add all the previously deferred Items to the current queue.

```
busy activate
```

Congratulations! You may now start enjoying the benefits of a more relaxed approach to your busy life.

## Ready to get busy?

Learn the [principles and data model](background.md)
