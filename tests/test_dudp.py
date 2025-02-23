import datetime as dt

from aika import TimeInterval


def test_calendar_week(ti):
    """
    Test calendar weeks.
    """
    assert ti.parse("2025W02") == TimeInterval(
        dt.datetime(2025, 1, 6, 0, 0),
        dt.datetime(2025, 1, 13, 0, 0),
    )


def test_month(ti):
    """
    Test months.
    """
    assert (
        ti.parse("2025M01")
        == ti.parse("2025-01")
        == TimeInterval(
            dt.datetime(2025, 1, 1, 0, 0),
            dt.datetime(2025, 2, 1, 0, 0),
        )
    )


def test_quarter(ti):
    """
    Test fiscal quarters.
    """
    assert ti.parse("2025Q01") == TimeInterval(
        dt.datetime(2025, 1, 1, 0, 0),
        dt.datetime(2025, 3, 31, 23, 59, 59),
    )
