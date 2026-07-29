import pytest

from material_state import (
    get_material, all_materials, classify_material_support, MaterialConfigError, MaterialNotImplementedError, MATERIAL_TYPES,
)


def test_all_material_types_registered():
    materials = all_materials()
    assert {m.name for m in materials} == set(MATERIAL_TYPES)


def test_incompressible_newtonian_is_implemented():
    m = get_material("incompressible_newtonian_liquid")
    assert m.implemented is True
    m.require_implemented()  # should not raise


def test_high_viscosity_newtonian_is_implemented_same_solver():
    m = get_material("high_viscosity_newtonian_liquid")
    assert m.implemented is True


@pytest.mark.parametrize(
    "name",
    ["low_mach_newtonian_gas", "simplified_viscoelastic_candidate", "generic_compressible_gas_placeholder"],
)
def test_unimplemented_materials_are_interface_only_not_silently_newtonian(name):
    m = get_material(name)
    assert m.implemented is False
    assert classify_material_support(name) == "material_interface_only"
    with pytest.raises(MaterialNotImplementedError):
        m.require_implemented()


def test_unknown_material_name_raises():
    with pytest.raises(MaterialConfigError):
        get_material("plasma")
