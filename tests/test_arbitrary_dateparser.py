# Copyright (c) 2023, The Panodata developers and contributors.
# Distributed under the terms of the MIT license, see LICENSE.

import datetime as dt

from freezegun import freeze_time

from aika import DaterangeExpression
from tests import TESTDRIVE_DATETIME


@freeze_time(TESTDRIVE_DATETIME)
def test_single_empty():
    """
    An empty date range constraint should yield the same result as when using "now".
    """
    dr = DaterangeExpression()
    assert (
        dr.parse("")
        == dr.parse("now")
        == (
            dt.datetime(2023, 8, 17, 23, 3, 17),
            dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
        )
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_single_relative():
    dr = DaterangeExpression()
    assert dr.parse("today") == (
        dt.datetime(2023, 8, 17, 0, 0, 0),
        dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
    )
    assert dr.parse("now") == (
        dt.datetime(2023, 8, 17, 23, 3, 17),
        dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_range_basics():
    # Make the parser exclusively use `arbitrary-dateparser`.
    from aika.core import adp_parse_english

    dr = DaterangeExpression()
    dr.clear_parsers()
    dr.add_parser(name="arbitrary-dateparser [en]", fun=adp_parse_english)

    # Verify parsing.
    assert dr.parse("jul 1 to jul 7") == (
        dt.datetime(2023, 7, 1, 0, 0),
        dt.datetime(2023, 7, 7, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_range_relative():
    dr = DaterangeExpression()
    assert dr.parse("tomorrow to next thursday") == (
        dt.datetime(2023, 8, 18, 0, 0, 0),
        dt.datetime(2023, 8, 24, 23, 59, 59, 999999),
    )
    assert dr.parse("tomorrow - next week") == (
        dt.datetime(2023, 8, 18, 0, 0, 0),
        dt.datetime(2023, 8, 27, 23, 59, 59, 999999),
    )
    assert dr.parse("next month") == (
        dt.datetime(2023, 9, 1, 0, 0, 0),
        dt.datetime(2023, 9, 30, 23, 59, 59, 999999),
    )
    assert dr.parse("december") == (
        dt.datetime(2023, 12, 1, 0, 0, 0),
        dt.datetime(2023, 12, 31, 23, 59, 59, 999999),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_default_start_end_time():
    dr = DaterangeExpression(
        default_start_time=dt.time(hour=9),
        default_end_time=dt.time(hour=17),
    )
    assert dr.parse("jul 1 to jul 7") == (
        dt.datetime(2023, 7, 1, 9, 0),
        dt.datetime(2023, 7, 7, 17, 0, 0),
    )
    assert dr.parse("today") == (
        dt.datetime(2023, 8, 17, 9, 0, 0),
        dt.datetime(2023, 8, 17, 17, 0, 0),
    )
    # A specific datetime must not be changed through `default_start_time`.
    assert dr.parse("now") == (
        dt.datetime(2023, 8, 17, 23, 3, 17),
        dt.datetime(2023, 8, 17, 17, 0, 0),
    )
    assert dr.parse("tomorrow to next thursday") == (
        dt.datetime(2023, 8, 18, 9, 0, 0),
        dt.datetime(2023, 8, 24, 17, 0, 0),
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_range_relative_weekdays():
    dr = DaterangeExpression(
        default_start_time=dt.time(hour=9),
        default_end_time=dt.time(hour=17),
    )
    assert dr.parse("Sat - Tue") == (
        dt.datetime(2023, 8, 19, 9, 0, 0),
        dt.datetime(2023, 8, 22, 17, 0, 0),
    )
