# philiprehberger-import-profiler

Show how long each Python import takes during startup.

## Installation

```bash
pip install philiprehberger-import-profiler
```

## Usage

```python
from philiprehberger_import_profiler import profile_imports

report = profile_imports("my_package")

# Slowest imports
for entry in report.slowest(10):
    print(f"{entry.name}: {entry.duration_ms:.1f}ms")

# Tree view
report.print_tree(threshold_ms=5.0)
# └── my_package (124.5ms)
#     ├── requests (45.2ms)
#     │   └── urllib3 (22.1ms)
#     └── numpy (62.0ms)

# Summary
print(f"Total: {report.total_ms:.1f}ms, Modules: {report.module_count}")

# Export
data = report.to_dict()
```

## API

- `profile_imports(module_name)` — Profile all imports, returns `ImportReport`
- `report.slowest(n)` — Top N slowest imports
- `report.print_tree(threshold_ms=0)` — Print indented tree
- `report.total_ms` — Total import time
- `report.to_dict()` — Export as list of dicts

## License

MIT
