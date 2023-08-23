# Copyright (c) 2023, The Panodata developers and contributors.
# Distributed under the terms of the LGPL license, see LICENSE.

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
        == dr.parse("jetzt")
        == (
            dt.datetime(2023, 8, 17, 23, 3, 17),
            dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
        )
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_single_relative_now_today():
    dr = DaterangeExpression()
    assert (
        dr.parse("today")
        == dr.parse("heute")
        == (
            dt.datetime(2023, 8, 17, 0, 0, 0),
            dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
        )
    )
    assert (
        dr.parse("now")
        == dr.parse("jetzt")
        == (
            dt.datetime(2023, 8, 17, 23, 3, 17),
            dt.datetime(2023, 8, 17, 23, 59, 59, 999999),
        )
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_single_relative_friday():
    dr = DaterangeExpression()
    assert (
        dr.parse_single("friday")
        == dr.parse_single("current friday")
        == dr.parse_single("next friday")
        == dr.parse_single("this friday")
        == dr.parse_single("freitag")
        == dr.parse_single("dieser freitag")
        == dr.parse_single("kommender freitag")
        == dr.parse_single("nächster freitag")
        == dr.parse_single("diesen freitag")
        == dr.parse_single("kommenden freitag")
        == dr.parse_single("nächsten freitag")
        == dt.datetime(2023, 8, 18, 0, 0, 0)
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_single_absolute():
    dr = DaterangeExpression()
    assert (
        dr.parse_single("August 20 2024")
        == dr.parse_single("August, 20 2024")
        == dr.parse_single("August 20 2024")
        == dr.parse_single("20. August 2024")
        == dr.parse_single("20.8.2024")
        == dr.parse_single("20.08.2024")
        == dt.datetime(2024, 8, 20, 0, 0)
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_range_basics():
    # Make the parser exclusively use `arbitrary-dateparser`,
    # to make sure it does not get parsed by `DateRangeParser`.
    from aika.core import adp_parse_english, adp_parse_german

    dr = DaterangeExpression()
    dr.clear_parsers()
    dr.add_parser(name="arbitrary-dateparser [de]", fun=adp_parse_german)
    dr.add_parser(name="arbitrary-dateparser [en]", fun=adp_parse_english)

    # Verify parsing.
    assert (
        dr.parse("jul 1 to jul 7")
        == dr.parse("1. juli bis 7. juli")
        == (
            dt.datetime(2023, 7, 1, 0, 0),
            dt.datetime(2023, 7, 7, 23, 59, 59, 999999),
        )
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_range_relative():
    dr = DaterangeExpression()
    assert (
        dr.parse("tomorrow to next thursday")
        == dr.parse("morgen bis nächsten donnerstag")
        == (
            dt.datetime(2023, 8, 18, 0, 0, 0),
            dt.datetime(2023, 8, 24, 23, 59, 59, 999999),
        )
    )
    assert (
        dr.parse("tomorrow - next week")
        == dr.parse("morgen - nächste woche")
        == (
            dt.datetime(2023, 8, 18, 0, 0, 0),
            dt.datetime(2023, 8, 27, 23, 59, 59, 999999),
        )
    )
    assert (
        dr.parse("next month")
        == dr.parse("nächster monat")
        == dr.parse("nächsten monat")
        == (
            dt.datetime(2023, 9, 1, 0, 0, 0),
            dt.datetime(2023, 9, 30, 23, 59, 59, 999999),
        )
    )
    assert (
        dr.parse("december")
        == dr.parse("im dezember")
        == (
            dt.datetime(2023, 12, 1, 0, 0, 0),
            dt.datetime(2023, 12, 31, 23, 59, 59, 999999),
        )
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
    assert (
        dr.parse("from Saturday to Tuesday")
        == dr.parse("Sat - Tue")
        == dr.parse("von Samstag bis Dienstag")
        == dr.parse("Sa - Di")
        == dr.parse("Sa-Di")
        == (
            dt.datetime(2023, 8, 19, 9, 0, 0),
            dt.datetime(2023, 8, 22, 17, 0, 0),
        )
    )


@freeze_time(TESTDRIVE_DATETIME)
def test_months():
    dr = DaterangeExpression(
        default_start_time=dt.time(hour=9),
        default_end_time=dt.time(hour=17),
    )
    assert (
        dr.parse("in March")
        == dr.parse("im März")
        == (
            dt.datetime(2023, 3, 1, 9, 0, 0),
            dt.datetime(2023, 3, 31, 17, 0, 0),
        )
    )
    assert (
        dr.parse("July to December")
        == dr.parse("Juli-Dezember")
        == (
            dt.datetime(2023, 7, 1, 9, 0, 0),
            dt.datetime(2023, 12, 31, 17, 0, 0),
        )
    )
