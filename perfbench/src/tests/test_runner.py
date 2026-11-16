import pytest

from perfbench import run_software_benchmarks


def test_run_software_benchmarks_returns_per_call_statistics():
    calls = []

    def target():
        calls.append(None)

    report = run_software_benchmarks(
        {"target": target},
        rounds=4,
        iterations=3,
    )

    result = report["benchmark_info"]["software"][0]
    stats = result["stats"]
    assert len(calls) == 12
    assert stats["rounds"] == 4
    assert stats["iterations"] == 3
    assert stats["warmup_iterations"] == 0
    assert len(stats["data"]) == 4
    assert stats["mean"] == pytest.approx(sum(stats["data"]) / 4)
    assert stats["min"] <= stats["median"] <= stats["max"]
    assert set(report["commit_info"]) >= {
        "id",
        "time",
        "author_time",
        "dirty",
        "project",
        "branch",
    }


def test_run_software_benchmarks_excludes_warmup_calls_from_timing():
    calls = []

    def target():
        calls.append(None)

    report = run_software_benchmarks(
        {"target": target},
        rounds=4,
        iterations=3,
        warmup_iterations=2,
    )

    stats = report["benchmark_info"]["software"][0]["stats"]
    assert len(calls) == 14
    assert stats["warmup_iterations"] == 2
    assert stats["rounds"] == 4
    assert stats["iterations"] == 3
    assert len(stats["data"]) == 4


def test_run_benchmarks_requires_a_target():
    from perfbench import run_benchmarks

    with pytest.raises(ValueError, match="At least one"):
        run_benchmarks(include_anchors=False)


def test_run_benchmarks_rejects_negative_warmup_iterations():
    from perfbench import run_benchmarks

    with pytest.raises(ValueError, match="warmup_iterations"):
        run_benchmarks({"target": lambda: None}, include_anchors=False, warmup_iterations=-1)
