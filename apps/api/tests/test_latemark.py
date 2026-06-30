"""Late-mark rules (acceptance criteria 6, 7)."""

from datetime import time

from app.services.latemark import is_late, late_deduction_hours


def test_late_after_cutoff():
    assert is_late(time(10, 21), "10:20")


def test_not_late_at_or_before_cutoff():
    assert not is_late(time(10, 20), "10:20")
    assert not is_late(time(9, 0), "10:20")


def test_first_three_late_marks_free():
    # criterion 6
    assert late_deduction_hours(1, 3) == 0
    assert late_deduction_hours(3, 3) == 0


def test_fourth_late_mark_deducts_one_hour():
    # criterion 7
    assert late_deduction_hours(4, 3) == 1.0
    assert late_deduction_hours(6, 3) == 3.0
