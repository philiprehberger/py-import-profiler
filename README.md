# philiprehberger-import-profiler

[![Tests](https://github.com/philiprehberger/py-import-profiler/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-import-profiler/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-import-profiler.svg)](https://pypi.org/project/philiprehberger-import-profiler/)
[![License](https://img.shields.io/github/license/philiprehberger/py-import-profiler)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

Show how long each Python import takes during startup.

## Installation

```bash
pip install philiprehberger-import-profiler
```

## Usage

### Basic Profiling

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
```

### Self Time and Export

```python
report = profile_imports("my_package")

# Self time excludes children's duration
for entry in report.slowest(5):
    print(f"{entry.name}: total={entry.duration_ms:.1f}ms self={entry.self_ms:.1f}ms")

# Export as list of dicts
data = report.to_dict()
# [{"name": "requests", "duration_ms": 45.2, "self_ms": 23.1, "parent": "my_package"}, ...]
```

## API

| Function / Class | Description |
|---|---|
| `profile_imports(module_name)` | Profile all imports, returns `ImportReport` |
| `report.slowest(n)` | Top N slowest imports as `ImportEntry` list |
| `report.print_tree(threshold_ms=0)` | Print indented tree |
| `report.total_ms` | Total import time in milliseconds |
| `report.module_count` | Number of modules imported |
| `report.to_dict()` | Export as list of dicts |
| `ImportEntry.name` | Module name |
| `ImportEntry.duration_ms` | Total duration including children |
| `ImportEntry.self_ms` | Duration excluding children |


## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
