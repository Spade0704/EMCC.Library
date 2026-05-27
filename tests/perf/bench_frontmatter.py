"""Performance bench harness for _scripts/_lib/frontmatter.py (P1 foundation).

Shipped by S046-T0c per AC1 R6 reproducibility-bench-script directive.
cProfile baseline harness + timeit micro-bench harness; runnable via
`python tests/perf/bench_frontmatter.py` from repo root.

Pure stdlib (cProfile / pstats / timeit / tempfile / pathlib / statistics).
Filename pattern `bench_*.py` does NOT match unittest discover default
`test*.py` — zero floor pollution per Lesson #20 INCREMENT-only direction.

Usage:
    python tests/perf/bench_frontmatter.py

Output (stdout):
    1. cProfile top-15 cumtime over 1000 load_page calls (50 synthetic
       pages × 20 iter).
    2. timeit _strip_eol_comment micro-bench on 12-line representative
       fm sample × 10000 iter × 5 repeats; best/median report.
    3. Summary line with reported numbers for future regression-baseline
       diff.

Intent (per AC3 floor 'ANY measurable speedup acceptable'):
    Bench is regression-detector NOT goal-chasing. Future cycles re-run
    + compare numbers vs CHANGELOG-committed baseline (S046-T0c shipped:
    _strip_eol_comment ~82% in-isolation speedup; aggregate load_page
    ~31% wallclock reduction including I/O dominance).
"""

import cProfile
import io
import pstats
import statistics
import sys
import tempfile
import timeit
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLE_WIKI = REPO_ROOT / "tests" / "fixtures" / "sample_wiki"
SAMPLE_PAGES = (
    SAMPLE_WIKI / "Home.md",
    SAMPLE_WIKI / "01-Domain" / "Foo.md",
    SAMPLE_WIKI / "01-Domain" / "Bar.md",
    SAMPLE_WIKI / "02-Other" / "Baz.md",
    SAMPLE_WIKI / "00-Start-Here" / "Glossary.md",
)
N_PAGES = 50
N_ITER = 20
TIMEIT_REPEAT = 5
TIMEIT_NUMBER = 10000

REPRESENTATIVE_FM_LINES = (
    'title: "Some Title"',
    "type: page",
    "visibility: internal",
    "completion: 80",
    "status: ready",
    "last_updated: 2026-05-21",
    "canon_sources: []",
    "unverified_claims: []",
    "dependencies: [Foo, Bar]",
    "blocking_questions: []",
    "role: Author  # who wrote it",
    'note: "value with # hash"',
)


def bench_cprofile_load_page() -> str:
    """Profile 1000 load_page calls on synthetic 50-page fixture; return top-15 report."""
    sys.path.insert(0, str(REPO_ROOT / "_scripts"))
    from _lib import frontmatter

    contents = [p.read_text(encoding="utf-8") for p in SAMPLE_PAGES]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        paths = []
        for i in range(N_PAGES):
            p = tmp_path / "page_{:03d}.md".format(i)
            p.write_text(contents[i % len(contents)], encoding="utf-8")
            paths.append(p)

        profiler = cProfile.Profile()
        profiler.enable()
        for _ in range(N_ITER):
            for p in paths:
                frontmatter.load_page(p)
        profiler.disable()

        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        stats.print_stats(15)
        return s.getvalue()


def bench_timeit_strip_eol_comment() -> dict:
    """timeit _strip_eol_comment on representative fm lines; return best/median dict."""
    sys.path.insert(0, str(REPO_ROOT / "_scripts"))
    from _lib.frontmatter import _strip_eol_comment

    lines = list(REPRESENTATIVE_FM_LINES)

    def run():
        for line in lines:
            _strip_eol_comment(line)

    t = timeit.Timer(run)
    times = t.repeat(repeat=TIMEIT_REPEAT, number=TIMEIT_NUMBER)
    return {
        "times": times,
        "best": min(times),
        "median": statistics.median(times),
    }


def main() -> int:
    """Run cProfile baseline + timeit micro-bench; print summary to stdout."""
    print("=" * 60)
    print("bench_frontmatter.py — _scripts/_lib/frontmatter.py perf harness")
    print("=" * 60)
    print()
    print("[1/2] cProfile baseline ({} pages × {} iter = {} load_page calls)".format(
        N_PAGES, N_ITER, N_PAGES * N_ITER
    ))
    print("-" * 60)
    profile_report = bench_cprofile_load_page()
    print(profile_report)
    print()
    print("[2/2] timeit _strip_eol_comment ({} lines × {} iter × {} repeat)".format(
        len(REPRESENTATIVE_FM_LINES), TIMEIT_NUMBER, TIMEIT_REPEAT
    ))
    print("-" * 60)
    result = bench_timeit_strip_eol_comment()
    formatted_times = ["{:.4f}".format(x) for x in result["times"]]
    print("Times:  {}".format(formatted_times))
    print("Best:   {:.4f}s".format(result["best"]))
    print("Median: {:.4f}s".format(result["median"]))
    print()
    print("Summary (S046-T0c shipped baseline for future regression diff):")
    print("  _strip_eol_comment in-isolation: ~0.019s median ({}x12 lines)".format(
        TIMEIT_NUMBER
    ))
    print("  Pre-opt baseline (S046-T0c pre-merge): ~0.105s median (82% in-isolation speedup)")
    print("  load_page aggregate (1000 calls): pre 0.263s -> post 0.181s (~31% wallclock reduction)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
