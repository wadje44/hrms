"""Late-mark rules (doc §8.3).

- A punch-in after the cutoff (default 10:20) is a late mark.
- First N (default 3) late marks per month are free.
- From the (N+1)th onward, 1 hour is deducted from paid hours per late mark.
- Count resets every calendar month.
"""

from datetime import time

from app.core.constants import LATE_MARK_DEDUCTION_HOURS


def parse_cutoff(cutoff: str) -> time:
    hh, mm = cutoff.split(":")
    return time(int(hh), int(mm))


def is_late(punch_in_local: time, cutoff: str) -> bool:
    """True if the first punch-in of the day is strictly after the cutoff."""
    return punch_in_local > parse_cutoff(cutoff)


def late_deduction_hours(late_count: int, free_marks: int) -> float:
    """Hours deducted for a month given the total late marks that month."""
    billable = max(0, late_count - free_marks)
    return billable * LATE_MARK_DEDUCTION_HOURS
