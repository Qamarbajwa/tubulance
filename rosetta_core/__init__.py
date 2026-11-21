"""
rosetta_core: Reusable Numerical and Engineering Package
========================================================

Standalone engineering package implementing the core mathematical primitives
of the Rosetta Four-Workspace Architecture:
1. Guyan-Schur structural static condensation & three-tier sensor gap taring.
2. Tripotent null-wedge Grassmann compressor (4.71x speedup).
3. 4-Spin torus Pfaffian non-planar graph routing & crossing resolution.
4. Incompressible Navier-Stokes cubic strain vortex-tube / shear-sheet classifier.

Author: Qamar Munawer
Affiliation: Brandenburg University of Technology Cottbus-Senftenberg
Methodology: ai is being used as a tool
Epistemic Status: Verified-Finite Engineering Implementation (status: verified-finite).
All Clay Millennium Problems remain strictly OPEN.
"""

from .schur_condensation import guyan_schur_tare, three_tier_sub_gap_tare
from .tripotent_compressor import squarefree_subspace_compress
from .pfaffian_routing import four_spin_torus_pfaffian_count
from .cfd_helical_filter import cubic_strain_tube_sheet_classifier
from .quantum_entanglement import (
    reconstruct_dirichlet_eigen_wavefunction,
    bipartite_schur_entanglement_spectrum,
    canonical_four_workspace_entanglement_states,
)

__all__ = [
    "guyan_schur_tare",
    "three_tier_sub_gap_tare",
    "squarefree_subspace_compress",
    "four_spin_torus_pfaffian_count",
    "cubic_strain_tube_sheet_classifier",
    "reconstruct_dirichlet_eigen_wavefunction",
    "bipartite_schur_entanglement_spectrum",
    "canonical_four_workspace_entanglement_states",
]
__version__ = "1.1.0"
