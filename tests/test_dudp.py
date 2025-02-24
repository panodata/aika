import datetime as dt

import pytest
from freezegun import freeze_time

from aika import TimeInterval
from tests.conftest import TESTDRIVE_DATETIME


def test_week_calendar(ti):
    """
    Test calendar weeks.
    """
    assert ti.parse("2025W02") == TimeInterval(
        dt.datetime(2025, 1, 6, 0, 0),
        dt.datetime(2025, 1, 13, 0, 0),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_week_last(ti):
    """
    Test relative weeks.
    """
    # This is 2023W32.
    assert ti.parse("last week") == TimeInterval(
        dt.datetime(2023, 8, 7, 0, 0),
        dt.datetime(2023, 8, 13, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_week_this(ti):
    """
    Test relative weeks.
    """
    # This is 2023W33.
    assert ti.parse("this week") == TimeInterval(
        dt.datetime(2023, 8, 14, 0, 0),
        dt.datetime(2023, 8, 20, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_week_next(ti):
    """
    Test relative weeks.
    """
    # This is 2023W33.
    assert ti.parse("next week") == TimeInterval(
        dt.datetime(2023, 8, 21, 0, 0),
        dt.datetime(2023, 8, 27, 23, 59, 59, 999999),
    )


def test_month_calendar(ti):
    """
    Test calendar months.
    """
    assert (
        ti.parse("2025M01")
        == ti.parse("2025-01")
        == TimeInterval(
            dt.datetime(2025, 1, 1, 0, 0),
            dt.datetime(2025, 2, 1, 0, 0),
        )
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_month_last(ti):
    """
    Test relative months.
    """
    # This is 2023-07.
    assert ti.parse("last month") == TimeInterval(
        dt.datetime(2023, 7, 1, 0, 0),
        dt.datetime(2023, 7, 31, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_month_this(ti):
    """
    Test relative months.
    """
    # This is 2023-08.
    assert ti.parse("this month") == TimeInterval(
        dt.datetime(2023, 8, 1, 0, 0),
        dt.datetime(2023, 8, 31, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_month_next(ti):
    """
    Test relative months.
    """
    # This is 2023-09.
    assert ti.parse("next month") == TimeInterval(
        dt.datetime(2023, 9, 1, 0, 0),
        dt.datetime(2023, 9, 30, 23, 59, 59, 999999),
    )


def test_quarter(ti):
    """
    Test fiscal quarters.
    """
    assert ti.parse("2025Q01") == TimeInterval(
        dt.datetime(2025, 1, 1, 0, 0),
        dt.datetime(2025, 3, 31, 23, 59, 59),
    )


def test_year_calendar(ti):
    """
    Test calendar years.
    """
    assert ti.parse("2025") == TimeInterval(
        dt.datetime(2025, 1, 1, 0, 0),
        dt.datetime(2026, 1, 1, 0, 0, 0),
    )


@freeze_time(TESTDRIVE_DATETIME)
@pytest.mark.xfail()
def test_year_last(ti):
    """
    Test relative years.
    """
    # This is 2022.
    assert ti.parse("last year") == TimeInterval(
        dt.datetime(2022, 1, 1, 0, 0),
        dt.datetime(2022, 12, 31, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_year_this(ti):
    """
    Test relative years.
    """
    # This is 2023.
    assert ti.parse("this year") == TimeInterval(
        dt.datetime(2023, 1, 1, 0, 0),
        dt.datetime(2023, 12, 31, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
@pytest.mark.xfail()
def test_year_next(ti):
    """
    Test relative years.
    """
    # This is 2024.
    assert ti.parse("next year") == TimeInterval(
        dt.datetime(2024, 1, 1, 0, 0),
        dt.datetime(2024, 12, 31, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_delta(ti):
    """
    Test time interval deltas lika `-1d`.
    """
    assert ti.parse("-3d3h5m30s") == TimeInterval(
        dt.datetime(2023, 8, 14, 19, 57, 47),
        dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
    )

    assert ti.parse("-1w") == TimeInterval(
        dt.datetime(2023, 8, 10, 23, 3, 17),
        dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
    )

    assert ti.parse("-1 week") == TimeInterval(
        dt.datetime(2023, 8, 10, 23, 3, 17),
        dt.datetime(2023, 9, 10, 23, 3, 17),
    )

    assert ti.parse("-1M") == TimeInterval(
        dt.datetime(2023, 8, 1, 0, 0),
        dt.datetime(2023, 9, 1, 0, 0),
    )

    assert ti.parse("-1 month") == TimeInterval(
        dt.datetime(2023, 7, 17, 23, 3, 17),
        dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
    )

    assert ti.parse("-3 M") == TimeInterval(
        dt.datetime(2023, 8, 3, 0, 0),
        dt.datetime(2023, 9, 3, 0, 0),
    )

    assert ti.parse("-3 months") == TimeInterval(
        dt.datetime(2023, 5, 17, 23, 3, 17),
        dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
    )

    assert ti.parse("-1y") == TimeInterval(
        dt.datetime(2022, 8, 17, 23, 3, 17),
        dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
    )

    assert ti.parse("-1 year") == TimeInterval(
        dt.datetime(2022, 8, 17, 23, 3, 17),
        dt.datetime(2023, 8, 17, 23, 3, 17),
    )
