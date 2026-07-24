from run_classification import RunStages, classify_run, positive_result_bar


def test_classify_run_blocked_when_pipeline_fails():
    assert classify_run(RunStages(pipeline_ok=False)) == "blocked"


def test_classify_run_pipeline_only_when_resolution_inadequate():
    assert classify_run(RunStages(pipeline_ok=True, resolution_ok=False)) == "pipeline_only"


def test_classify_run_apriori_operator_valid():
    stages = RunStages(pipeline_ok=True, resolution_ok=True, apriori_operator_ok=True)
    assert classify_run(stages) == "apriori_operator_valid"


def test_classify_run_finite_difference_comparison_valid():
    stages = RunStages(
        pipeline_ok=True,
        resolution_ok=True,
        apriori_operator_ok=True,
        finite_difference_ok=True,
    )
    assert classify_run(stages) == "finite_difference_comparison_valid"


def test_classify_run_nonlinear_transfer_comparison_valid():
    stages = RunStages(
        pipeline_ok=True,
        resolution_ok=True,
        apriori_operator_ok=True,
        finite_difference_ok=True,
        nonlinear_transfer_ok=True,
        nonlinear_transfer_meets_positive_result_bar=False,
    )
    assert classify_run(stages) == "nonlinear_transfer_comparison_valid"


def test_classify_run_forward_validation_required():
    stages = RunStages(
        pipeline_ok=True,
        resolution_ok=True,
        apriori_operator_ok=True,
        finite_difference_ok=True,
        nonlinear_transfer_ok=True,
        nonlinear_transfer_meets_positive_result_bar=True,
    )
    assert classify_run(stages) == "forward_validation_required"


def test_positive_result_bar_all_pass():
    passes, reasons = positive_result_bar(
        n_t=8.0,
        min_terminal_shells=6,
        populated_terminal_shells=5,
        min_populated_terminal_shells=4,
        conservation_relative_residual=1e-9,
        conservation_tolerance=1e-6,
        energy_above_cutoff=0.0,
        transfer_correlation=0.5,
    )
    assert passes
    assert reasons == []


def test_positive_result_bar_flags_each_failure():
    passes, reasons = positive_result_bar(
        n_t=4.0,
        min_terminal_shells=6,
        populated_terminal_shells=1,
        min_populated_terminal_shells=4,
        conservation_relative_residual=1e-2,
        conservation_tolerance=1e-6,
        energy_above_cutoff=1e-3,
        transfer_correlation=-0.2,
    )
    assert not passes
    assert len(reasons) == 5
