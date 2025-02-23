import pytest

from aika import TimeIntervalParser

TESTDRIVE_DATETIME = "2023-08-17T23:03:17+0200"


@pytest.fixture
def dr():
    return TimeIntervalParser(midnight_heuristics=True, return_tuple=True)


@pytest.fixture
def ti():
    return TimeIntervalParser()
