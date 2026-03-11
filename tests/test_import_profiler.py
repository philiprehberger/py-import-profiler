from philiprehberger_import_profiler import profile_imports, ImportReport


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
