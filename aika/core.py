# Copyright (c) 2023-2025, The Panodata developers and contributors.
# Distributed under the terms of the LGPL license, see LICENSE.

import datetime as dt
import logging
import typing as t

import dateparser
import dateutil.parser.isoparser
import fiscalyear
from daterangeparser import parse as drp_parse_english
from dateutil.rrule import MONTHLY, WEEKLY, YEARLY

from .arbitrary_dateparser import DateParser
from .daterangeparser_german import parse_german as drp_parse_german
from .model import Parser, TimeInterval, trange

if t.TYPE_CHECKING:
    import pandulum


# FIXME: Do not set timezone explicitly.
arbitrary_parser_english = DateParser(tz="Europe/Berlin")
arbitrary_parser_english.replaced_words["in"] = "this"


before_midnight = dt.time(hour=23, minute=59, second=59, microsecond=999999)
midnights = [dt.time(hour=0, minute=0, second=0), before_midnight]


logger = logging.getLogger(__name__)


class TimeIntervalParser:
    """
    Unified date range parser, using multiple packages.

    - DateRangeParser: Parsing absolute dates in different formats. Ignores time values.
      Examples: jul 1 to jul 7, 1-7 july
    - arbitrary-dateparser: Parsing relative dates using textual inputs in different formats.
      Examples: next week, tomorrow to next thursday.
    """

    NOW = ["now", "jetzt"]
    TODAY = ["today", "heute"]

    def __init__(
        self,
        default_start_time: t.Optional[dt.time] = None,
        default_end_time: t.Optional[dt.time] = None,
        midnight_heuristics: bool = False,
        snap_hours: bool = False,
        return_tuple: bool = False,
    ):
        self.default_start_time = default_start_time
        self.default_end_time = default_end_time
        self.return_tuple = return_tuple
        self.midnight_heuristics = midnight_heuristics
        self.snap_hours = snap_hours
        self.parsers: t.List[Parser] = []
        self.use_all_parsers()

    def use_all_parsers(self):
        self.parsers += [
            Parser(name="DateRangeParser [en]", fun=drp_parse_english),
            Parser(name="DateRangeParser [de]", fun=drp_parse_german),
            Parser(name="arbitrary-dateparser [de]", fun=adp_parse_german),
            Parser(name="arbitrary-dateparser [en]", fun=adp_parse_english),
            Parser(name="DUDP [all]", fun=self.dudp_parse),
        ]

    def clear_parsers(self):
        self.parsers = []

    def add_parser(self, fun: t.Callable, name: str = "unknown"):
        self.parsers.append(Parser(name=name, fun=fun))

    def parse(self, when: str) -> t.Union[trange, TimeInterval]:
        """
        Parse date range from textual expression.
        """
        if not when:
            when = "now"

        date_start: t.Optional[dt.datetime] = None
        date_end: t.Optional[dt.datetime] = None

        for parser in self.parsers:
            try:
                date_start, date_end = parser.fun(when)
                break
            except Exception as ex:
                logger.debug(f"Parsing date range failed ({parser.name}) for '{when}': {ex}")

        if date_start is None:
            raise ValueError(f"Failed detecting start date: {when}")

        # A specific datetime must not be changed through `default_start_time`.
        is_now = when in self.NOW
        if self.snap_hours and not is_now:
            if self.default_start_time is not None:
                date_start = dt.datetime.combine(date_start, self.default_start_time)
            if date_end is not None and self.default_end_time is not None:
                date_end = dt.datetime.combine(date_end, self.default_end_time)

        if self.midnight_heuristics:
            if date_start.time() in midnights and self.default_start_time is not None:
                date_start = dt.datetime.combine(date_start, self.default_start_time)

            if date_end is not None and date_end.time() in midnights:
                if self.default_end_time is not None:
                    time = self.default_end_time
                else:
                    time = dt.time(hour=23, minute=59, second=59, microsecond=999999)
                date_end = dt.datetime.combine(date_end, time)

        if self.return_tuple:
            return date_start, date_end

        return TimeInterval(date_start, date_end)

    def parse_single(self, when: str) -> dt.datetime:
        """
        Parse single date from textual expression.
        """
        ti = self.parse(when)
        if isinstance(ti, TimeInterval):
            return ti.start
        elif isinstance(ti, tuple):
            return ti[0]
        else:
            raise TypeError(f"Invalid time interval type: {type(ti)}")

    def dudp_parse(self, when: str) -> trange:
        """
        Parse date range using `python-dateutil` and `dateparser` libraries.
        """

        if ".." in when:
            return t.cast(trange, when.split(".."))

        if "Q" in when:
            year, quarter = when.split("Q")
            q = fiscalyear.FiscalQuarter(int(year), int(quarter)).next_fiscal_quarter
            return q.start, q.end

        interval = None
        if (when.isnumeric() and len(when) == 4) or "year" in when:
            interval = YEARLY
        elif "M" in when or (len(when) == 7 and when.count("-") == 1):
            when = when.replace("M", "-")
            interval = MONTHLY
        elif "W" in when:
            interval = WEEKLY

        t_start: t.Optional[dt.datetime] = None
        try:
            try:
                t_start = dateutil.parser.isoparse(when)
            except Exception:
                t_start = dateutil.parser.parse(when)
        except dateutil.parser.ParserError:
            parser = dateparser.date.DateDataParser()
            response = parser.get_date_data(when)
            t_start = response.date_obj
            if self.snap_hours:
                if when in self.TODAY and t_start is not None:
                    t_start = t_start.replace(hour=0, minute=0, second=0, microsecond=0)

        if t_start is None:
            raise ValueError(f"Failed parsing date range: {when}")

        t_end: t.Optional[dt.datetime] = None
        if interval == YEARLY:
            t_end = t_start + dt.timedelta(days=365)
        elif interval == MONTHLY:
            t_end = t_start + dt.timedelta(days=31)
        elif interval == WEEKLY:
            t_end = t_start + dt.timedelta(days=7)
        else:
            t_end = dt.datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999)

        return t_start, t_end


def adp_parse_english(when: str) -> trange:
    """
    Parse date range using `arbitrary-dateparser`. English variant.
    """
    return from_pendulum(arbitrary_parser_english(when))


def adp_parse_german(when: str) -> trange:
    """
    Parse date range using `arbitrary-dateparser`. German variant.
    """
    from .dateparser_german import DateParserGerman

    arbitrary_parser_german = DateParserGerman(tz="Europe/Berlin")

    return from_pendulum(arbitrary_parser_german(when))


def from_pendulum(period: "pandulum.Period") -> trange:
    """
    Translate Pendulum `Period` to tuple of `datetime` objects.
    """

    def pendulum_to_datetime(value):
        return dt.datetime.fromisoformat(value.to_iso8601_string())

    date_start = period.start.naive()
    date_end = period.end.naive()
    return pendulum_to_datetime(date_start), pendulum_to_datetime(date_end)


class DaterangeExpression(TimeIntervalParser):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("snap_hours", True)
        kwargs.setdefault("midnight_heuristics", True)
        kwargs.setdefault("return_tuple", True)
        super().__init__(*args, **kwargs)
