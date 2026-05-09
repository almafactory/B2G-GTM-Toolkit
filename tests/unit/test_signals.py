from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from b2g_gtm_toolkit.models.gtm import (
    ActionStatus,
    NotificationPreference,
    NotificationPreferences,
    NotificationStatus,
    Owner,
    Priority,
    Signal,
    SignalType,
)


def test_owner_with_full_notification_preferences() -> None:
    owner = Owner(
        name="Ana Gomez",
        role="GTM Lead",
        email="ana@example.com",
        slack_id="U12345",
        notification_preference=NotificationPreference.both,
        notification_preferences=NotificationPreferences(slack=True, email=True),
    )
    assert owner.notification_preferences.slack is True
    assert owner.notification_preferences.email is True
    assert owner.slack_id == "U12345"


def test_owner_default_notification_preferences() -> None:
    owner = Owner(name="Sin Pref")
    assert owner.notification_preferences.slack is False
    assert owner.notification_preferences.email is False


@pytest.mark.parametrize("priority", list(Priority))
def test_signal_accepts_each_priority(priority: Priority) -> None:
    s = Signal(type=SignalType.new_opportunity, summary="Nueva senal", priority=priority)
    assert s.priority == priority


@pytest.mark.parametrize("status", list(ActionStatus))
def test_signal_accepts_each_action_status(status: ActionStatus) -> None:
    s = Signal(
        type=SignalType.contract_awarded,
        summary="Contrato adjudicado",
        action_status=status,
    )
    assert s.action_status == status


@pytest.mark.parametrize("status", list(NotificationStatus))
def test_signal_accepts_each_notification_status(status: NotificationStatus) -> None:
    s = Signal(
        type=SignalType.budget_publication,
        summary="Publicacion de presupuesto",
        notification_status=status,
        detected_at=datetime.now(timezone.utc),
    )
    assert s.notification_status == status


def test_signal_rejects_invalid_priority() -> None:
    with pytest.raises(ValidationError):
        Signal(type=SignalType.other, summary="x", priority="critical")


def test_signal_rejects_invalid_action_status() -> None:
    with pytest.raises(ValidationError):
        Signal(type=SignalType.other, summary="x", action_status="working")


def test_signal_rejects_invalid_notification_status() -> None:
    with pytest.raises(ValidationError):
        Signal(type=SignalType.other, summary="x", notification_status="pending")


def test_signal_with_owner_ref() -> None:
    s = Signal(
        type=SignalType.leadership_change,
        summary="Nuevo alcalde",
        owner_ref="owner-123",
    )
    assert s.owner_ref == "owner-123"
