"""Lightweight, explicit profiling instrumentation (Milestone 7 Part I).

Deliberately **not** the Python ``cProfile``/``profile`` module wrapped
around every simulation step (the review: "Do not use the Python
profiler inside every normal simulation by default"): that would add
nontrivial per-call overhead to a loop that may run thousands of times.
Instead, :class:`StepProfiler` is a plain accumulator that callers
(``time_integrators.py``) feed pre-measured ``time.perf_counter()``
durations into, at explicit, hand-picked category boundaries -- the
review's ``convection``/``diffusion RHS construction``/
``diffusion linear solve``/``pressure RHS construction``/
``pressure solve``/``projection correction``/``boundary conditions``/
``diagnostics``/``total timestep`` categories.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ProfileReport:
    """One category's accumulated time and share of the profiled total."""

    category: str
    seconds: float
    percent: float


class StepProfiler:
    """Accumulates named-category durations across one or more time steps.
    Not thread-safe; one instance per integrator (or per run), fed
    directly from measured ``time.perf_counter()`` deltas by the caller.
    """

    def __init__(self) -> None:
        self._totals: Dict[str, float] = {}

    def add(self, category: str, seconds: float) -> None:
        self._totals[category] = self._totals.get(category, 0.0) + max(0.0, seconds)

    def reset(self) -> None:
        self._totals = {}

    @property
    def totals(self) -> Dict[str, float]:
        return dict(self._totals)

    def report(self, total_category: str = "total") -> list:
        """Return a list of :class:`ProfileReport`, most expensive first,
        with percentages of ``total_category``'s accumulated time (falls
        back to the sum of all *other* categories if ``total_category``
        was never explicitly added -- e.g. a caller that only tracks
        sub-categories)."""
        total = self._totals.get(total_category)
        if total is None or total <= 0.0:
            total = sum(v for k, v in self._totals.items() if k != total_category)
        if total <= 0.0:
            return [ProfileReport(category=k, seconds=v, percent=0.0) for k, v in self._totals.items()]
        rows = [
            ProfileReport(category=k, seconds=v, percent=100.0 * v / total)
            for k, v in self._totals.items()
        ]
        rows.sort(key=lambda r: r.seconds, reverse=True)
        return rows

    def format_report(self, total_category: str = "total") -> str:
        """Human-readable table, e.g.::

            Pressure solve          58.2%
            Diffusion solves        29.4%
            Convection               7.1%
        """
        rows = [r for r in self.report(total_category) if r.category != total_category]
        if not rows:
            return "(no profiling data recorded)"
        name_width = max(len(r.category) for r in rows)
        return "\n".join(f"{r.category:<{name_width}}  {r.percent:5.1f}%" for r in rows)
