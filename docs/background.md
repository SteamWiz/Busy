
# Background

## Principles

Busy is built with the following usage principles in mind:

- *Monotasking*: We each focus better when we work on exactly one task at a time. So busy only shows you one task.
- *Keyboard-driven*: Productive people use the keyboard effectively, because muscle memory builds up over time, and it's faster to hit a key than to find an icon on a screen and move the pointer.
- *Offline use*: It's designed to run on your laptop or desktop computer, without needing an internet connection, so it works extremely fast under any conditions.
- *Multi-platform* Because Busy is a terminal-based application, it will run on MacOS, Linux, or Windows.
- *Personal*: Busy is not a collaboration platform or project management application. It's for managing your personal time, not assigning things to others.
- *Importance over Urgency*: Stop stressing out over last-minute tasks and impending deadlines! Busy makes it easy to capture future tasks and remember to do them early enough to reduce the pressure.
- *Editable data*: The data is stored in text files, which can easily be edited outside of Busy itself. (In fact, Busy started as a todo.txt type of approach and grew from there.)

## Data model

Busy's core model is a collection of Items, which are typically tasks but can also be discussion topics, groceries to buy, or anything else you like. Items are organized into Queues, which are named sets of Items to do. You work on the top Item in a Queue, and when it's done, that Item gets marked as "done", to reveal the next one. There is a default Queue (called "tasks") but you can also create other Queues, for example a shopping list or discussion list.

Busy actually moves Items between States within each Queue. Each Queue contains a Collection (ordered list) of Items for each State. The States are:

- `todo`: Current Items for you to work on, discuss, or buy now.
- `done`: Items that have been done, with the date completed.
- `plan`: Items that have been deferred to a future date, with that date.
