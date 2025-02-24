import pytest

from aika import DaterangeExpression, TimeIntervalParser

TESTDRIVE_DATETIME = "2023-08-17T23:03:17+0200"


@pytest.fixture
def dr():
    return DaterangeExpression()


@pytest.fixture
def ti():
    return TimeIntervalParser()
