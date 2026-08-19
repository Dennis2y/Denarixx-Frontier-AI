from __future__ import annotations

import math

import torch

from ml.run_experiment import advance_scheduler


def _make_optimizer_and_scheduler(t_max: int = 4):
    parameter = torch.nn.Parameter(torch.tensor([1.0]))

    optimizer = torch.optim.AdamW(
        [parameter],
        lr=3e-4,
        weight_decay=0.01,
    )

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=t_max,
        eta_min=3e-5,
    )

    return optimizer, scheduler


def test_pytorch_cosine_scheduler_rebounds_after_original_tmax():
    """
    Document the exact scheduler behavior that exposed the issue.

    This is not the desired Denarixx policy. It proves why a continuation
    guard is required.
    """

    optimizer, scheduler = _make_optimizer_and_scheduler(t_max=4)

    rates = []

    for _ in range(8):
        optimizer.step()
        scheduler.step()
        rates.append(scheduler.get_last_lr()[0])

    assert math.isclose(
        rates[3],
        3e-5,
        rel_tol=0.0,
        abs_tol=1e-12,
    )

    assert rates[4] > rates[3]
    assert rates[5] > rates[4]
    assert rates[6] > rates[5]
    assert rates[7] > rates[6]


def test_required_denarixx_policy_holds_eta_min_after_completed_cosine():
    """
    Specify the required Denarixx resume behavior without invoking
    run_experiment.py or performing model training.
    """

    optimizer, scheduler = _make_optimizer_and_scheduler(t_max=4)

    for _ in range(4):
        optimizer.step()
        scheduler.step()

    checkpoint_scheduler_state = scheduler.state_dict()
    checkpoint_optimizer_state = optimizer.state_dict()

    assert checkpoint_scheduler_state["T_max"] == 4
    assert checkpoint_scheduler_state["last_epoch"] == 4

    resumed_optimizer, resumed_scheduler = (
        _make_optimizer_and_scheduler(t_max=8)
    )

    resumed_optimizer.load_state_dict(
        checkpoint_optimizer_state
    )

    resumed_scheduler.load_state_dict(
        checkpoint_scheduler_state
    )

    restored_t_max = int(
        resumed_scheduler.state_dict()["T_max"]
    )

    restored_last_epoch = int(
        resumed_scheduler.state_dict()["last_epoch"]
    )

    eta_min = float(
        resumed_scheduler.state_dict()["eta_min"]
    )

    assert restored_last_epoch >= restored_t_max

    continuation_rates = []

    for _ in range(4):
        for group in resumed_optimizer.param_groups:
            group["lr"] = eta_min

        continuation_rates.append(
            resumed_optimizer.param_groups[0]["lr"]
        )

    assert continuation_rates == [
        eta_min,
        eta_min,
        eta_min,
        eta_min,
    ]

    assert all(
        math.isclose(
            rate,
            3e-5,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        for rate in continuation_rates
    )



def test_production_policy_preserves_cosine_before_tmax():
    optimizer, scheduler = _make_optimizer_and_scheduler(t_max=4)

    optimizer.step()
    rate_1 = advance_scheduler(optimizer, scheduler)

    optimizer.step()
    rate_2 = advance_scheduler(optimizer, scheduler)

    optimizer.step()
    rate_3 = advance_scheduler(optimizer, scheduler)

    assert scheduler.last_epoch == 3
    assert rate_1 > rate_2 > rate_3 > scheduler.eta_min


def test_production_policy_holds_eta_min_after_restored_tmax():
    optimizer, scheduler = _make_optimizer_and_scheduler(t_max=4)

    for _ in range(4):
        optimizer.step()
        scheduler.step()

    checkpoint_optimizer_state = optimizer.state_dict()
    checkpoint_scheduler_state = scheduler.state_dict()

    resumed_optimizer, resumed_scheduler = (
        _make_optimizer_and_scheduler(t_max=8)
    )

    resumed_optimizer.load_state_dict(
        checkpoint_optimizer_state
    )
    resumed_scheduler.load_state_dict(
        checkpoint_scheduler_state
    )

    assert resumed_scheduler.T_max == 4
    assert resumed_scheduler.last_epoch == 4

    rates = []

    for _ in range(4):
        resumed_optimizer.step()

        rates.append(
            advance_scheduler(
                resumed_optimizer,
                resumed_scheduler,
            )
        )

    assert resumed_scheduler.last_epoch == 4

    assert all(
        math.isclose(
            rate,
            3e-5,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        for rate in rates
    )

    assert all(
        math.isclose(
            group["lr"],
            3e-5,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        for group in resumed_optimizer.param_groups
    )
