# philiprehberger-import-profiler

[![Tests](https://github.com/philiprehberger/py-import-profiler/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-import-profiler/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-import-profiler.svg)](https://pypi.org/project/philiprehberger-import-profiler/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-import-profiler)](https://github.com/philiprehberger/py-import-profiler/commits/main)

![philiprehberger-import-profiler](https://raw.githubusercontent.com/philiprehberger/py-import-profiler/main/package-card.webp)

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

### Summary and JSON export

Use `summary()` for a compact dict you can log or pretty-print, and `to_json()` for the full entry list as a JSON string.

```python
report = profile_imports("my_package")

print(report.summary(slowest=3))
# {"total_ms": 124.5, "module_count": 42, "slowest": [
#     {"name": "numpy", "duration_ms": 62.0},
#     {"name": "requests", "duration_ms": 45.2},
#     {"name": "urllib3", "duration_ms": 22.1},
# ]}

# JSON string (compact when indent=None)
print(report.to_json(indent=None))
```

### Sorting and filtering reports

```python
report = profile_imports("my_package")

# Top N slowest entries (descending by duration_ms)
for entry in report.slowest(3):
    print(f"{entry.name}: {entry.duration_ms:.1f}ms")

# Filter to entries whose module name starts with a prefix
numpy_only = report.filter("numpy")
print(f"numpy.* modules: {numpy_only.module_count}, total={numpy_only.total_ms:.1f}ms")

# filter returns a new report; the original is unchanged
assert report.module_count >= numpy_only.module_count
```

## API

| Function / Class | Description |
|---|---|
| `profile_imports(module_name)` | Profile all imports, returns `ImportReport` |
| `report.slowest(n=10)` | Top N slowest imports as `ImportEntry` list, sorted descending |
| `report.filter(prefix)` | New `ImportReport` containing only entries whose name starts with `prefix` |
| `report.print_tree(threshold_ms=0)` | Print indented tree |
| `report.total_ms` | Total import time in milliseconds |
| `report.module_count` | Number of modules imported |
| `report.to_dict()` | Export as list of dicts |
| `report.to_json(indent=2)` | Export entries as a JSON-formatted string |
| `report.summary(slowest=5)` | Compact dict with `total_ms`, `module_count`, and top-N slowest |
| `ImportEntry.name` | Module name |
| `ImportEntry.duration_ms` | Total duration including children |
| `ImportEntry.self_ms` | Duration excluding children |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-import-profiler)

🐛 [Report issues](https://github.com/philiprehberger/py-import-profiler/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-import-profiler/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
