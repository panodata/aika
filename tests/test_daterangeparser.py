# Copyright (c) 2023, The Panodata developers and contributors.
# Distributed under the terms of the MIT license, see LICENSE.

import datetime as dt

from freezegun import freeze_time

from aika import DaterangeExpression
from tests import TESTDRIVE_DATETIME


@freeze_time(TESTDRIVE_DATETIME)
def test_range_basics():
    dr = DaterangeExpression()
    assert dr.parse("jul 1 to jul 7") == (
        dt.datetime(2023, 7, 1, 0, 0),
        dt.datetime(2023, 7, 7, 23, 59, 59, 999999),
    )

    assert dr.parse("1-7 july") == (
        dt.datetime(2023, 7, 1, 0, 0),
        dt.datetime(2023, 7, 7, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_single_basics():
    dr = DaterangeExpression()
    assert dr.parse("1st july") == (
        dt.datetime(2023, 7, 1, 0, 0),
        dt.datetime(2023, 7, 1, 23, 59, 59, 999999),
    )
    assert dr.parse("March 2024") == (
        dt.datetime(2024, 3, 1, 0, 0, 0),
        dt.datetime(2024, 3, 31, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
    )
    )
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_months():
    dr = DaterangeExpression(
        default_start_time=dt.time(hour=9),
        default_end_time=dt.time(hour=17),
    )
    assert dr.parse("March") == (
        dt.datetime(2023, 3, 1, 9, 0, 0),
        dt.datetime(2023, 3, 31, 17, 0, 0),
    )
    assert dr.parse("July to December") == (
        dt.datetime(2023, 7, 1, 9, 0, 0),
        dt.datetime(2023, 12, 31, 17, 0, 0),
    )
