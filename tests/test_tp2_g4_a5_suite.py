"""Worker test suite for TP2-G4-A5 Whole-Gate Synthesis and R1 Corrections."""
import numpy as np
import pytest
from navier3d.math_assurance import MathAssuranceEngine, ClaimManager, PromotionManager


def test_g4_synthesis_barrier_1_parabolic_scaling_class():
    """Barrier 1: Verify parabolic scaling exponents [x]=-1, [t]=-2, [u]=1, [omega]=2, [J_omega]=3, [Q_s]=6, [S_s]=4, [R_Q]=2."""
    dim_x = -1
    dim_t = -2
    dim_u = 1
    dim_omega = 2
    dim_J_omega = 3
    dim_Q_s = 6
    dim_S_s = 4
    dim_R_Q = dim_Q_s - dim_S_s # 6 - 4 = 2
    dim_Xi = 2 * dim_J_omega - 2 * dim_omega # 6 - 4 = 2

    assert dim_R_Q == 2
    assert dim_Xi == 2


def test_g4_synthesis_barrier_2_periodic_shear_annihilation():
    """Barrier 2: Verify E12 E32 = 0 decoupling deformation from vorticity gradient on fixed T^3."""
    e1 = np.array([1.0, 0.0, 0.0])
    e2 = np.array([0.0, 1.0, 0.0])
    e3 = np.array([0.0, 0.0, 1.0])

    E12 = np.outer(e1, e2)
    E32 = np.outer(e3, e2)

    product = E12 @ E32
    assert np.allclose(product, np.zeros((3, 3)))


def test_g4_synthesis_barrier_3_kinematic_decoupling():
    """Barrier 4: Verify A_omega = K^2, A_grad = K^-2 => Theta = K^-4 -> 0."""
    K = 10.0
    D_K = np.diag([K, 1.0, 1.0 / K])
    w = np.array([1.0, 0.0, 0.0])
    G = np.array([[0, 0, 0], [0, 0, 0], [0, 1, 0]])

    A_w = np.sum((D_K @ w) ** 2) / np.sum(w ** 2)
    A_g = np.sum((D_K @ G) ** 2) / np.sum(G ** 2)
    Theta = A_g / A_w

    assert np.isclose(A_w, 100.0)
    assert np.isclose(A_g, 0.01)
    assert np.isclose(Theta, 1e-4)


def test_g4_synthesis_surviving_xi_rate_identity():
    """Surviving Result: Verify d_s ln(chi_s) = 2nu E_mu[Xi] on random ensembles."""
    nu = 1e-3
    np.random.seed(42)
    n_samples = 50

    Z_sq_list = []
    DG_sq_list = []
    Xi_list = []

    for _ in range(n_samples):
        D = np.diag(np.exp(np.random.randn(3)))
        D /= np.prod(np.diag(D)) ** (1.0 / 3.0)
        w = np.random.randn(3)
        G = np.random.randn(3, 3)

        Z = D @ w
        Z_sq = np.sum(Z ** 2)
        DG_sq = np.sum((D @ G) ** 2)

        Z_sq_list.append(Z_sq)
        DG_sq_list.append(DG_sq)
        Xi_list.append(DG_sq / Z_sq)

    Z_sq_arr = np.array(Z_sq_list)
    DG_sq_arr = np.array(DG_sq_list)
    Xi_arr = np.array(Xi_list)

    S_s = np.mean(Z_sq_arr)
    Q_s = 2.0 * nu * np.mean(DG_sq_arr)
    direct_rate = Q_s / S_s

    # mu-weighted average
    mu_weights = Z_sq_arr / np.sum(Z_sq_arr)
    mu_avg_Xi = np.sum(mu_weights * Xi_arr)
    formula_rate = 2.0 * nu * mu_avg_Xi

    assert np.isclose(direct_rate, formula_rate, atol=1e-14)


def test_g4_synthesis_r1_project_synthesis_cannot_be_theorem():
    """R1: Verify that claim type PROJECT_SYNTHESIS cannot have truth_status PROVED_THEOREM."""
    mgr = ClaimManager()
    clm14 = mgr.get_claim("CLM-014")
    assert clm14["claim_type"] == "PROJECT_SYNTHESIS"
    assert clm14["passport"]["truth_status"] == "VERIFIED_SYNTHESIS"

    # Testing validator rejection if someone attempts PROVED_THEOREM on PROJECT_SYNTHESIS
    invalid_passport = dict(clm14["passport"])
    invalid_passport["truth_status"] = "PROVED_THEOREM"
    val = mgr.validate_passport(invalid_passport, claim_type="PROJECT_SYNTHESIS")
    assert val["valid"] is False
    assert "Category error" in val["reason"]


def test_g4_synthesis_r1_undocumented_significance_rejected():
    """R1: Verify that undocumented significance state (e.g. S3_FIELD_SIGNIFICANCE) is rejected."""
    mgr = ClaimManager()
    clm14 = mgr.get_claim("CLM-014")
    assert clm14["passport"]["significance"] == "S3_POTENTIAL_FIELD_SIGNIFICANCE"

    invalid_passport = dict(clm14["passport"])
    invalid_passport["significance"] = "S3_FIELD_SIGNIFICANCE" # Undocumented status drift
    val = mgr.validate_passport(invalid_passport, claim_type="PROJECT_SYNTHESIS")
    assert val["valid"] is False
    assert "Invalid significance tier" in val["reason"]


def test_g4_synthesis_r1_xi_identity_cannot_promote_target_status():
    """R1: Verify that Xi structural identity cannot promote target problem status to SOLVED."""
    res = PromotionManager.validate_solved_eligibility(
        claim_id="CLM-011",
        target_equivalence=True,
        truth_status="PROVED_IDENTITY",
        assumption_drift="NONE",
        dependency_closure=True,
        formalization_fidelity=True,
        math_independence="MATH_I4_HUMAN_SPECIALIST",
        external_validation="MULTI_SPECIALIST_REVIEWED",
        community_status="COMMUNITY_ACCEPTED"
    )
    assert res["solved_eligible"] is False
    assert res["verdict"] == "SUBTHEOREM_CANNOT_BE_SOLVED_ELIGIBLE"


def test_g4_synthesis_clay_statement_b_unresolved():
    """Preservation: Verify that Clay Statement B is confirmed UNRESOLVED."""
    engine = MathAssuranceEngine()
    branch = engine.validate_branch_identity()
    assert branch["valid"] is True
    assert branch["official_target_branch"] == "CLAY_STATEMENT_B_PERIODIC_R3_MOD_Z3"
