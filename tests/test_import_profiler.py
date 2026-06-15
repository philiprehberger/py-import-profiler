import json

from philiprehberger_import_profiler import profile_imports, ImportReport, ImportEntry


def test_profile_json():
    report = profile_imports("json")
    assert isinstance(report, ImportReport)
    assert report.module_count > 0
    assert report.total_ms >= 0


def test_slowest():
    report = profile_imports("json")
    slowest = report.slowest(5)
    assert isinstance(slowest, list)
    if len(slowest) > 1:
        assert slowest[0].duration_ms >= slowest[1].duration_ms


def test_entry_has_name():
    report = profile_imports("json")
    for entry in report.entries:
        assert isinstance(entry.name, str)
        assert len(entry.name) > 0


def test_entry_self_ms():
    report = profile_imports("json")
    for entry in report.entries:
        assert entry.self_ms >= 0


def test_to_dict():
    report = profile_imports("json")
    data = report.to_dict()
    assert isinstance(data, list)
    if data:
        assert "name" in data[0]
        assert "duration_ms" in data[0]


def test_print_tree(capsys):
    report = profile_imports("json")
    report.print_tree()
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def _make_report(entries: list[ImportEntry]) -> ImportReport:
    return ImportReport(entries=list(entries), _by_name={e.name: e for e in entries})


def test_slowest_returns_top_n_descending():
    entries = [
        ImportEntry(name="a", duration_ms=50.0),
        ImportEntry(name="b", duration_ms=200.0),
        ImportEntry(name="c", duration_ms=10.0),
    ]
    report = _make_report(entries)
    top = report.slowest(2)
    assert len(top) == 2
    assert top[0].duration_ms == 200.0
    assert top[0].name == "b"
    assert top[1].duration_ms == 50.0
    assert top[1].name == "a"


def test_slowest_returns_all_when_n_exceeds_length():
    entries = [
        ImportEntry(name="a", duration_ms=50.0),
        ImportEntry(name="b", duration_ms=200.0),
        ImportEntry(name="c", duration_ms=10.0),
    ]
    report = _make_report(entries)
    assert len(report.slowest(100)) == 3


def test_slowest_zero_returns_empty():
    entries = [
        ImportEntry(name="a", duration_ms=50.0),
        ImportEntry(name="b", duration_ms=200.0),
        ImportEntry(name="c", duration_ms=10.0),
    ]
    report = _make_report(entries)
    assert report.slowest(0) == []


def test_filter_returns_only_matching_prefix():
    entries = [
        ImportEntry(name="os", duration_ms=12.0),
        ImportEntry(name="os.path", duration_ms=4.0),
        ImportEntry(name="json", duration_ms=20.0),
        ImportEntry(name="sys", duration_ms=1.0),
    ]
    report = _make_report(entries)
    filtered = report.filter("os")
    assert isinstance(filtered, ImportReport)
    names = [e.name for e in filtered.entries]
    assert names == ["os", "os.path"]


def test_filter_does_not_mutate_original():
    entries = [
        ImportEntry(name="os", duration_ms=12.0),
        ImportEntry(name="json", duration_ms=20.0),
    ]
    report = _make_report(entries)
    original_names = [e.name for e in report.entries]
    _ = report.filter("os")
    assert [e.name for e in report.entries] == original_names
    assert len(report.entries) == 2


def test_to_json_round_trips_through_loads():
    entries = [
        ImportEntry(name="os", duration_ms=12.0, parent=""),
        ImportEntry(name="json", duration_ms=20.0, parent=""),
    ]
    report = _make_report(entries)
    payload = json.loads(report.to_json())
    assert isinstance(payload, list)
    assert payload[0]["name"] == "os"
    assert payload[0]["duration_ms"] == 12.0


def test_to_json_compact_when_indent_none():
    entries = [ImportEntry(name="os", duration_ms=12.0)]
    report = _make_report(entries)
    compact = report.to_json(indent=None)
    assert "\n" not in compact


def test_summary_basic_fields():
    entries = [
        ImportEntry(name="a", duration_ms=50.0),
        ImportEntry(name="b", duration_ms=200.0),
        ImportEntry(name="c", duration_ms=10.0),
    ]
    report = _make_report(entries)
    summary = report.summary(slowest=2)
    assert summary["module_count"] == 3
    assert summary["total_ms"] == 260.0
    assert len(summary["slowest"]) == 2
    assert summary["slowest"][0]["name"] == "b"
    assert summary["slowest"][0]["duration_ms"] == 200.0
