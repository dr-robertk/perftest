# perfbench

`perfbench` collects machine metadata and runs its compute- and
memory-bandwidth-bound anchor benchmarks alongside benchmarks for arbitrary
zero-argument Python callables. It uses Python's `timeit` module and does not
depend on pytest.

```python
from perfbench import run_benchmarks, write_report
from room_solver.solver import solveDirichletNeumann

report = run_benchmarks(
    {
        "room_solver": lambda: solveDirichletNeumann(n=51, iterations=1),
    },
    rounds=10,
    iterations=1,
    warmup_iterations=3,
)

print(report["machine_info"])
print(report["benchmark_info"]["anchors"])
print(report["benchmark_info"]["software"])
write_report(report, "benchmark.json")
```

By default, the anchor benchmarks use a 5120 × 5120 matrix and 80 million
array elements. Set `matmul_size` and `memcopy_size` to adjust their inputs.
Use `run_anchor_benchmarks()` or `run_software_benchmarks({...})` to run only
one group. Functions that need arguments can be wrapped in a lambda or
`functools.partial`.

Each benchmark's `stats` contains per-call seconds for each round in `data`,
plus min, max, mean, median, standard deviation, total time, and operations
per second. `warmup_iterations` runs extra calls before timing; the default is
zero. `timeit` disables garbage collection while timing, like its standard
default behavior.