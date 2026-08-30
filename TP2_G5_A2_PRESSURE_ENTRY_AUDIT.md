# TP2-G5-A2 — Pressure Entry Audit

Classification:
NO_EXPLICIT_PRESSURE_TERM_AT_THIS_LEVEL

The exact A2 drift contains A, S, Omega, G, and the accepted strain-gradient
source T^S=(nabla S)omega. T^S is not pressure and is not relabeled as
pressure. The vorticity equation has already eliminated pressure at this
instantaneous level.

Pressure has an INDIRECT_NONLOCAL_DEPENDENCE through the Navier-Stokes
evolution of A and S, including the pressure Hessian in the future evolution
of the velocity gradient. That indirect dependence does not authorize
insertion of a direct pressure-Hessian term into F or b_Xi.
