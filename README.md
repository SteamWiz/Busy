# Busy

⚠️ DISCLAIMER: This is a hobby/personal project. Not a commercial product. Not for production use.

## Escape from overwhelm and stay focused all day

**NOTE** Usage documentation lives in the `docs/` directory of the repo, published at https://busy.steamwiz.io. The text below is for developers (including AI agents).

## Development setup

Requires Python 3.13 or higher.

Busy uses [Dyngle](https://dyngle.steamwiz.io) for developer tooling instead of using Make. Shared operations come from the `.conf` submodule ([SteamWiz/Conf](https://github.com/SteamWiz/Conf)); clone with `--recurse-submodules` or run `git submodule update --init`. Install Dyngle using `pipx` so it lives outside the venv, for isolation from work in progress. All commands assume the `pwd` is the root of the project.

- `dyngle run init` - Create the virtual environment and install poetry
- `dyngle run dependencies` - Install the required packages using poetry
- `dyngle run test` - Run the full unit test suite and check coverage
- `dyngle run style` - Run style cleanup and check
- `dyngle run build` - Create a local build
- `dyngle run sandbox` - Create the sandbox for play

GitHub Actions performs the entire build/test/style/release cycle using the shared workflows in [SteamWiz/actions](https://github.com/SteamWiz/actions).

Documentation for the WizLib framework, including important testing techniques for WizLib-based applications, is at https://wizlib.steamwiz.io.

Note that this application makes heavy use of WizLib and all code changes are expected to comply with, and take advantage of, the framework.

## Software architecture guidelines

A few notes specific to the architecture of this application.

### Command extensions

- Inheritance: Be cautious - prefer selective code reuse over changing inheritance hierarchy
- QueueCommand base: Add shared functionality here for automatic coverage across all queue commands
- Validation: Implement in base class `handle_vals()` method for automatic inheritance
- Documentation: Update docs/commands.md, specific feature docs, and docs/getting-started.md

### Testing with WizLib

- ConfigHandler.fake(): Use underscore format (`busy_storage_directory`) → converts to hyphen format (`busy-storage-directory`)
- parse_run(): Test full command execution instead of manual command instances
- BusyError: Assert exceptions are raised, not output text
- Test sandboxing: When using `ConfigHandler.fake()` with storage-dependent apps, reinitialize storage after setting fake config to prevent writing to production data
- Output capture: Wrap `parse_run()` calls with `self.patchout(), self.patcherr()` to suppress debug output during tests

```python
def test_config_validation(self):
    with TemporaryDirectory() as temp_dir:
        app = BusyApp()
        app.config = ConfigHandler.fake(
            busy_storage_directory=temp_dir,
            queues={'old': {'active': False}}
        )
        # CRITICAL: Reinitialize storage after setting fake config
        app.storage = FileStorage(temp_dir, app.identifier)
        
        # Capture output to prevent debug messages during tests
        with self.patchout(), self.patcherr():
            with self.assertRaises(BusyError):
                app.parse_run('add', '-q', 'old', 'test task')
```

### Command hierarchy and configuration access

- QueueCommand base class: Most queue-related commands inherit from `QueueCommand` in `busy/command/__init__.py`. This is the ideal place to add functionality that should apply to all queue operations.
- Configuration access: Commands have access to configuration through `self.app.config.get('config-key')`. The WizLib framework automatically sets up handlers as app attributes, so `ConfigHandler` becomes `self.app.config`.
- Validation patterns: For features that need to validate user input against configuration (like active queue settings), implement the validation logic in the base command class's `handle_vals()` method. This ensures automatic coverage across all inheriting commands.
- Error handling: Use `busy.error.BusyError` for user-facing errors that should be caught and displayed cleanly rather than causing stack traces.

### Configuration structure

Configuration follows YAML format and supports multiple syntax patterns for flexibility:

- Explicit format: `queues: { tasks: { active: true }, old: { active: false } }`
- Boolean shorthand: `queues: { tasks: true, old: false }`
- Catch-all patterns: `queues: { tasks: true, _: false }` (blocks arbitrary queue names)

Default behavior should be permissive (allow operations when no config exists) to maintain backward compatibility.

Configuration keys use hyphen-separated format (`busy-storage-directory`) which the ConfigHandler converts from underscore format in code.

Nested configuration: Tags can be configured within queues using the same patterns: `queues: { tasks: { tags: { main: true, old: false } } }`

### Validation architecture patterns

- Cached properties: Use `@cached_property` for config access to avoid repeated lookups
- Generic methods: Create reusable validation helpers for similar entities (queues, tags, etc.)
- Boolean config pitfall: Avoid `config.get(key) or fallback` - use explicit `None` checks when `key` might be `False`
- Validation placement: Start with simple commands (AddCommand) before complex edit workflows
- Edit command complexity: Validation in edit workflows requires careful handling of collection modification timing

### Implementation notes

- Collection modification: `collection.read_items()` modifies collections in-place and sets `changed=True` before validation can occur
- Validation timing: For edit commands, validate parsed items BEFORE calling `collection.read_items()` or `collection.replace()`
- Error recovery: If validation fails after collection modification, the collection may still be marked as changed and saved
- DRY principle enforcement: When adding similar validation logic to multiple commands, create centralized helper methods in the base class rather than duplicating code. For example, `check_and_set_validation_warnings()` method replaced repeated validation code across output commands.
- Performance optimization with caching: Use `@cached_property` for expensive operations that don't change during command execution. Tag hierarchy building was optimized from being called multiple times to once per command instance.
- Testing limitations with external processes: Edit commands cannot be easily tested because they launch external editors. Document this limitation and implement the feature based on architectural patterns rather than comprehensive testing.
- Validation timing patterns: Some validation needs to happen at different times:
  - Configuration validation: At app startup (in `__init__`)
  - Command validation: During command execution (in `handle_vals()` or `execute()`)
  - Different behavior by command type: Some commands raise exceptions, others show warnings
- Two-phase validation for complex features: Features like hierarchical tags require both structural validation (unique definitions) at configuration load time and runtime validation (interdependencies) during command execution.
- Helper method design: When creating validation helpers, use parameters to control behavior (e.g., `raise_exception=True/False`) rather than creating separate methods for similar logic.

