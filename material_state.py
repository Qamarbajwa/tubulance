"""
Material-state interface (Milestone 5.7)
===========================================

Milestone 5.7 requires the terminal-layer model schema to support multiple
material states, without pretending to have solved physics it hasn't. Only
the incompressible Newtonian regime (any viscosity) is actually integrated
by pseudo_spectral_solver.py -- everything else is declared but
`implemented=False`, and any caller that tries to run an unimplemented
material must classify the attempt `material_interface_only`, never
silently fall back to treating it as Newtonian.
"""

from __future__ import annotations

from dataclasses import dataclass

MATERIAL_TYPES = (
    "incompressible_newtonian_liquid",
    "low_mach_newtonian_gas",
    "high_viscosity_newtonian_liquid",
    "simplified_viscoelastic_candidate",
    "generic_compressible_gas_placeholder",
)


class MaterialConfigError(ValueError):
    pass


class MaterialNotImplementedError(NotImplementedError):
    """Raised if code tries to actually solve/step an interface_only material."""


@dataclass(frozen=True)
class MaterialState:
    name: str
    implemented: bool
    compressibility: str  # "incompressible" | "low_mach" | "compressible"
    notes: str = ""

    def __post_init__(self):
        if self.name not in MATERIAL_TYPES:
            raise MaterialConfigError(f"unknown material {self.name!r}; must be one of {MATERIAL_TYPES}")
        if self.compressibility not in ("incompressible", "low_mach", "compressible"):
            raise MaterialConfigError(f"invalid compressibility {self.compressibility!r}")

    def require_implemented(self) -> None:
        if not self.implemented:
            raise MaterialNotImplementedError(
                f"material {self.name!r} is interface_only in this milestone -- "
                "it cannot be run and must not be silently approximated as Newtonian."
            )


_REGISTRY: dict[str, MaterialState] = {
    "incompressible_newtonian_liquid": MaterialState(
        "incompressible_newtonian_liquid",
        implemented=True,
        compressibility="incompressible",
        notes="Solved by pseudo_spectral_solver.py; the primary material for this milestone.",
    ),
    "high_viscosity_newtonian_liquid": MaterialState(
        "high_viscosity_newtonian_liquid",
        implemented=True,
        compressibility="incompressible",
        notes=(
            "Physically the same incompressible Newtonian equations at a higher "
            "kinematic viscosity -- no new constitutive law is needed, so this "
            "material is implemented via the same solver with SolverConfig.viscosity "
            "set high, not via a separate code path."
        ),
    ),
    "low_mach_newtonian_gas": MaterialState(
        "low_mach_newtonian_gas",
        implemented=False,
        compressibility="low_mach",
        notes="interface_only -- no low-Mach (weakly compressible) solver implemented.",
    ),
    "simplified_viscoelastic_candidate": MaterialState(
        "simplified_viscoelastic_candidate",
        implemented=False,
        compressibility="incompressible",
        notes="interface_only -- no constitutive law for a viscoelastic stress has been specified.",
    ),
    "generic_compressible_gas_placeholder": MaterialState(
        "generic_compressible_gas_placeholder",
        implemented=False,
        compressibility="compressible",
        notes="interface_only placeholder -- no compressible solver implemented.",
    ),
}


def get_material(name: str) -> MaterialState:
    if name not in _REGISTRY:
        raise MaterialConfigError(f"unknown material {name!r}; must be one of {MATERIAL_TYPES}")
    return _REGISTRY[name]


def all_materials() -> tuple[MaterialState, ...]:
    return tuple(_REGISTRY[name] for name in MATERIAL_TYPES)


def classify_material_support(name: str) -> str:
    """Returns 'implemented' or 'material_interface_only'. Never silently
    approximates an unimplemented material as Newtonian."""
    return "implemented" if get_material(name).implemented else "material_interface_only"
