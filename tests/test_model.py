import datetime as dt

import pytest
from freezegun import freeze_time

from aika import TimeInterval, TimeIntervalParser
from tests.conftest import TESTDRIVE_DATETIME


@pytest.fixture
def interval():
    tip = TimeIntervalParser()
    return tip.parse("july 2023")


def test_interval_create_void():
    with pytest.raises(TypeError) as ex:
        TimeInterval()
    assert ex.match("missing 1 required positional argument: 'start'")


@freeze_time(TESTDRIVE_DATETIME)
def test_interval_create_start():
    ti = TimeInterval(dt.datetime.now())
    assert str(ti) == "TimeInterval(start=FakeDatetime(2023, 8, 17, 21, 3, 17), end=None)"


@freeze_time(TESTDRIVE_DATETIME)
def test_interval_create_full():
    ti = TimeInterval(dt.datetime.now(), dt.datetime.now())
    assert (
        str(ti) == "TimeInterval(start=FakeDatetime(2023, 8, 17, 21, 3, 17), end=FakeDatetime(2023, 8, 17, 21, 3, 17))"
    )


def test_interval_format_github(interval):
    assert interval.githubformat() == "2023-07-01..2023-07-31"


def test_interval_format_iso(interval):
    assert interval.isoformat() == "2023-07-01T00:00:00/2023-07-31T00:00:00"


def test_interval_format_lucene(interval):
    with pytest.raises(NotImplementedError):
        interval.luceneformat()


def test_interval_format_math(interval):
    assert interval.mathformat() == "2023-07-01T00:00:00..2023-07-31T00:00:00"


def test_interval_format_opsgenie(interval):
    assert interval.opsgenieformat() == 'createdAt >= "01-07-2023T00:00:00" and createdAt <= "31-07-2023T00:00:00"'
