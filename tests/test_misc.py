# Copyright (c) 2023, The Panodata developers and contributors.
# Distributed under the terms of the MIT license, see LICENSE.

import datetime as dt

import pytest

from aika.misc import next_date_by_weekday


def test_weekdaymap_de():
    date_value = next_date_by_weekday("do")
    assert isinstance(date_value, dt.date)


def test_weekdaymap_en():
    date_value = next_date_by_weekday("su")
    assert isinstance(date_value, dt.date)


def test_weekdaymap_fail():
    with pytest.raises(KeyError) as ex:
        next_date_by_weekday("foo")
    assert ex.match("Weekday not found: foo")
