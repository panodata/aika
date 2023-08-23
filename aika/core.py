# Copyright (c) 2023, The Panodata developers and contributors.
# Distributed under the terms of the MIT license, see LICENSE.

import datetime as dt
import logging
import typing as t

from arbitrary_dateparser import DateParser
from daterangeparser import parse as drp_parse_english

from .daterangeparser_german import parse_german as drp_parse_german
from .model import Parser, trange

logger = logging.getLogger(__name__)

# FIXME: Do not set timezone explicitly.
arbitrary_parser = DateParser(tz="Europe/Berlin")

before_midnight = dt.time(hour=23, minute=59, second=59, microsecond=999999)
midnights = [dt.time(hour=0, minute=0, second=0), before_midnight]


class DaterangeExpression:
    """
    Unified date range parser, using multiple packages.

    - DateRangeParser: Parsing absolute dates in different formats. Ignores time values.
      Examples: jul 1 to jul 7, 1-7 july
    - arbitrary-dateparser: Parsing relative dates using textual inputs in different formats.
      Examples: next week, tomorrow to next thursday.
    """

    def __init__(self, default_start_time: t.Optional[dt.time] = None, default_end_time: t.Optional[dt.time] = None):
        self.default_start_time = default_start_time
        self.default_end_time = default_end_time
        self.parsers: t.List[Parser] = []
        self.use_all_parsers()

    def use_all_parsers(self):
        self.parsers += [
            Parser(name="DateRangeParser [en]", fun=drp_parse_english),
            Parser(name="DateRangeParser [de]", fun=drp_parse_german),
            Parser(name="arbitrary-dateparser [en]", fun=adp_parse_english),
        ]

    def clear_parsers(self):
        self.parsers = []

    def add_parser(self, fun: t.Callable, name: str = "unknown"):
        self.parsers.append(Parser(name=name, fun=fun))

    def parse(self, when: str) -> trange:
        """
        Parse date range from text.
        """
        if not when:
            when = "now"

        date_start: t.Optional[dt.datetime] = None
        date_end: t.Optional[dt.datetime] = None

        for parser in self.parsers:
            try:
                date_start, date_end = parser.fun(when)
                break
            except Exception:
                logger.warning(f"Parsing date range failed ({parser.name}): {when}")

        if date_start is None:
            raise ValueError(f"Failed parsing date range: {when}")

        if date_end is None:
            date_end = date_start

        if date_start.time() in midnights and self.default_start_time is not None:
            date_start = dt.datetime.combine(date_start, self.default_start_time)

        if date_end.time() in midnights:
            if self.default_end_time is not None:
                time = self.default_end_time
            else:
                time = dt.time(hour=23, minute=59, second=59, microsecond=999999)
            date_end = dt.datetime.combine(date_end, time)

        return date_start, date_end


def adp_parse_english(when: str) -> trange:
    """
    Parse date range using `arbitrary-dateparser`.
    """

    def pendulum_to_datetime(value):
        return dt.datetime.fromisoformat(value.to_iso8601_string())

    period = arbitrary_parser(when)
    date_start = period.start.naive()
    date_end = period.end.end_of("day").naive()
    return pendulum_to_datetime(date_start), pendulum_to_datetime(date_end)
