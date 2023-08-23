# daterangeparser - a Python library to parse string date ranges
# Copyright (C) 2013  Robin Wilson

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime

from daterangeparser.parse_date_range import check_day, post_process
from pyparsing import Group, Literal, Optional, ParseException, Word, nums, oneOf, stringEnd

from aika.model import trange

MONTHS = {
    "jan": 1,
    "januar": 1,
    "feb": 2,
    "februar": 2,
    "mär": 3,
    "märz": 3,
    "maer": 3,
    "maerz": 3,
    "apr": 4,
    "april": 4,
    "mai": 5,
    "jun": 6,
    "juni": 6,
    "jul": 7,
    "juli": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "okt": 10,
    "oktober": 10,
    "nov": 11,
    "november": 11,
    "dez": 12,
    "dezember": 12,
}


def month_to_number(tokens):
    """
    Converts a given month in string format to the equivalent month number.

    Works with strings in any case, both abbreviated (Jan) and full (January).
    """
    month_name = tokens[0].lower()
    return MONTHS[month_name]


def create_daterangeparser_german():
    """Creates the parser using PyParsing functions."""

    # Day details (day number, superscript and day name)
    daynum = Word(nums, max=2)
    day = oneOf("Mo Montag Di Dienstag Mi Mittwoch Do Donnerstag Fr Freitag Sa Samstag So Sonntag", caseless=True)

    full_day_string = daynum + Optional(Literal(".").suppress())
    full_day_string.setParseAction(check_day)
    full_day_string.leaveWhitespace()

    # Month names, with abbreviations, with action to convert to equivalent month number
    month = oneOf(list(MONTHS.keys()), caseless=True) + Optional(Literal(".").suppress())
    month.setParseAction(month_to_number)

    # Year
    year = Word(nums, exact=4)
    year.setParseAction(lambda tokens: int(tokens[0]))

    time_sep = oneOf(": .")
    am_pm = oneOf("am pm", caseless=True)
    hours = Word(nums, max=2)
    mins = Word(nums, max=2)

    time = hours("hour") + time_sep.suppress() + mins("mins") + Optional(am_pm)("meridian")

    # date pattern
    date = Group(
        Optional(time).suppress()
        & Optional(full_day_string("day"))
        & Optional(day).suppress()
        & Optional(month("month"))
        & Optional(year("year"))
    )

    # Possible separators
    separator = oneOf("- -- bis \u2013 \u2014 ->", caseless=True)

    # Strings to completely ignore (whitespace ignored by default)
    ignoreable_chars = oneOf(", von vom ab anfang zum", caseless=True)

    # Final putting together of everything
    daterange = (
        Optional(date("start") + Optional(time).suppress() + separator.suppress())
        + date("end")
        + Optional(time).suppress()
        + stringEnd()
    )
    daterange.ignore(ignoreable_chars)

    return daterange


def parse_german(text: str, allow_implicit: bool = True) -> trange:
    """
    Parses a date range string and returns the start and end as datetimes.

    **Accepted formats:**

    This parsing routine works with date ranges and single dates, and should
    work with a wide variety of human-style string formats, including:

    - 27th-29th June 2010
    - 30 May to 9th Aug
    - 3rd Jan 1980 - 2nd Jan 2013
    - Wed 23 Jan - Sat 16 February 2013
    - Tuesday 29 May -> Sat 2 June 2012
    - From 27th to 29th March 1999
    - 1--9 Jul
    - 14th July 1988
    - 23rd October 7:30pm
    - From 07:30 18th Nov to 17:00 24th Nov

    **Notes:**

    - If an error encountered while parsing the date range then a
    `pyparsing.ParseException` will be raised.
    - If no year is specified then the current year is used.
    - All day names are ignored, so there is no checking to see whether,
    for example, the 23rd Jan 2013 is actually a Wednesday.
    - All times are ignored, assuming they are placed either before or after
    each date, otherwise they will cause an error.
    - The separators that are allows as part of the date range are `to`,
    `until`, `-`, `--` and `->`, plus the unicode em and en dashes.
    - Other punctuation, such as commas, is ignored.

    :param text: The string to parse
    :param allow_implicit: If implicit dates are allowed. For example,
    string 'May' by default treated as range
           from May, 1st to May, 31th. Setting allow_implicit to False helps avoid it.
    :return: A tuple ``(start, end)`` where each element is a datetime object.
    If the string only defines a single date then the tuple is ``(date, None)``.
    All times in the datetime objects are set to 00:00 as this function only parses dates.
    """
    parser = create_daterangeparser_german()

    result = parser.parseString(text)
    res = post_process(result, allow_implicit)

    # Create standard dd/mm/yyyy strings and then convert to Python datetime
    # objects
    if "year" not in res.start:
        # in case only separator was given
        raise ParseException("Couldn't parse resulting datetime")

    try:
        start_str = "%(day)s/%(month)s/%(year)s" % res.start
        start_datetime = datetime.datetime.strptime(start_str, "%d/%m/%Y")
    except ValueError as ex:
        raise ParseException("Couldn't parse resulting datetime") from ex

    if res.end is None:
        return start_datetime, None
    elif not res.end:
        raise ParseException("Couldn't parse resulting datetime")
    else:
        try:
            if "month" not in res.end:
                res.end["month"] = res.start["month"]
            end_str = "%(day)s/%(month)s/%(year)s" % res.end
            end_datetime = datetime.datetime.strptime(end_str, "%d/%m/%Y")
        except ValueError as ex:
            raise ParseException("Couldn't parse resulting datetime") from ex

        if end_datetime < start_datetime:
            # end is before beginning!
            # This is probably caused by a date straddling the change of year
            # without the year being given
            # So, we assume that the start should be the previous year
            res.start["year"] = res.start["year"] - 1
            start_str = "%(day)s/%(month)s/%(year)s" % res.start
            start_datetime = datetime.datetime.strptime(start_str, "%d/%m/%Y")

        return start_datetime, end_datetime
