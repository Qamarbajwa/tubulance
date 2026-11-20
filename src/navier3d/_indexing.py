"""Shared low-level 3-tuple indexing helpers for padded (ghost-cell) arrays.

Internal module: used by :mod:`navier3d.boundary_conditions` and
:mod:`navier3d.operators`. Field classes (:mod:`navier3d.fields`) expose
higher-level, named accessors (``interior``, ``ghost_layer``,
``boundary_layer``, ``interior_range``, ``first_interior_layer``) built on
top of these two primitives; prefer those in new code over calling
``axis_index``/``axis_slice`` directly.
"""
from __future__ import annotations


def axis_index(axis: int, i: int) -> tuple:
    """A 3-tuple index selecting a single plane ``i`` along ``axis``, all else full."""
    return tuple(i if a == axis else slice(None) for a in range(3))


def axis_slice(axis: int, s: slice) -> tuple:
    """A 3-tuple index selecting slice ``s`` along ``axis``, all else full."""
    return tuple(s if a == axis else slice(None) for a in range(3))
