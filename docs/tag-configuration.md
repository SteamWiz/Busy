# Tag configuration

## Tag Access Control

You can control which tags are allowed within each queue. This helps maintain consistent tagging and prevents typos.

```yaml
busy:
  queues:
    tasks:
      tags:
        work: true       # Allow #work tag
        personal: true   # Allow #personal tag
        old: false       # Block #old tag
    shopping:
      tags:
        urgent: true     # Allow #urgent tag in shopping queue
```

Configuration formats:

- Boolean shorthand: `work: true` or `work: false`
- Explicit format: `work: { active: true }` or `work: { active: false }`

Default behavior: When no tag configuration exists, all tags are allowed. There is no catch-all pattern for tags — only explicitly listed tags can be blocked or allowed by name.

**Error handling**: If you try to use a blocked tag, Busy will display an error like `Tag old is inactive for queue tasks`.

## Hierarchical tag structure

Busy supports hierarchical tag relationships where parent tags act as "fields" with child tags as "values" for structured data organization. This enables you to enforce consistent tagging patterns and create more organized task categorization.

```yaml
busy:
  queues:
    tasks:
      tags:
        project:
          tags:
            wizlib:
            busy:
            vernum:
        trackable:
          tags:
            development:
            research:
            admin:
              tags:
                finance:
                personnel:
                facilities:
    friends:
      tags:
        interests:
          tags:
            research:
            writing:
            art:
```

Tag interdependency rules:

- Parent requires exactly one child: Items with `#project` must have exactly one of `#wizlib`, `#busy`, or `#vernum`
- Child requires parent: Items with `#busy` must also have `#project`
- Multi-level validation: Works across multiple levels, so `#trackable #admin #finance` is valid

Validation behavior varies by command:

- Add commands: Validate before storing new items, raise error if invalid
- State change commands (`done`, `defer`, `activate`): Validate selection, raise error if invalid
- Edit commands (`edit`, `manage`): Validate after editing, show warning if invalid but still save
- Output commands (`list`, `view`, `describe`, `simple`, `dump`, `tags`): Validate selection, show warning if invalid

Unique definition requirement: Tags cannot be defined in multiple places within the same queue, but the same tag name can be used in different queues.

Example hierarchical usage:

```bash
# Valid: parent with exactly one child
busy add "Fix authentication bug #project #wizlib"

# Valid: multi-level hierarchy
busy add "Review budget #trackable #admin #finance"

# Invalid: parent without child (will raise error)
busy add "Some task #project"
# BusyError: Queue 'tasks' requires items with tag 'project' to have exactly one of 'busy' 'vernum' 'wizlib'

# Invalid: parent with multiple children (will raise error)
busy add "Some task #project #wizlib #busy"
# BusyError: Queue 'tasks' requires items with tag 'project' to have exactly one of 'busy' 'vernum' 'wizlib'

# Invalid: child without parent (will raise error)
busy add "Some task #wizlib"
# BusyError: Queue 'tasks' requires items with tag 'wizlib' to have parent tag 'project'
```

## Tag exclusivity groups

Tags at the top level of a queue's tag configuration can be assigned to a
named exclusivity group. Items may carry **at most one** tag from any given
group.

```yaml
busy:
  queues:
    tasks:
      tags:
        work:
          group: context
        personal:
          group: context
        hobby:
          group: context
        urgent:          # no group — can coexist freely with anything
```

With this configuration, an item tagged `#work` or `#personal` is valid,
but an item tagged `#work #personal` is rejected:

```bash
# Valid: one tag from group 'context'
busy add "Fix auth bug #work"

# Valid: no tag from group 'context' at all
busy add "Buy milk #urgent"

# Invalid: two tags from the same group
busy add "Some task #work #personal"
# BusyError: Queue 'tasks' allows at most one tag from group 'context': 'personal' 'work'
```

Groups only apply to **top-level tags** (those not nested as children of
another tag). Child tags in a hierarchy already have mutual exclusion
enforced by their parent — a parent tag requires exactly one child — so
`group` is ignored on child tags.

Multiple independent groups can be defined in the same queue:

```yaml
busy:
  queues:
    tasks:
      tags:
        work:
          group: context
        personal:
          group: context
        high:
          group: priority
        low:
          group: priority
```

An item may have at most one `context` tag and at most one `priority` tag,
but one from each group is perfectly valid: `#work #high`.

## Example Configuration

Here's a complete example showing both queue and tag controls:

```yaml
busy:
  storage:
    directory: /home/user/my-tasks
  queues:
    tasks:
      active: true
      tags:
        work: true
        personal: true
        urgent: true
    shopping:
      active: true
    archive:
      active: false     # Block this queue entirely
    _: false           # Block other queue names
```

**Error handling**: If you try to use a blocked queue by name, Busy will display an error like `Queue archive is inactive`. If the queue is blocked via the `_: false` catch-all, the error will read `Queue _ is inactive`.
