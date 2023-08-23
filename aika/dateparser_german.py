"""
The German variant of the DateParser module from the arbitrary-dateparser package by Michael Phelps.

https://pypi.org/project/arbitrary-dateparser/
"""

import calendar
import re
from itertools import product
from typing import Tuple

import pendulum
from arbitrary_dateparser import DateParser

from aika.util import LocaleManager

with LocaleManager("de_DE.UTF-8"):
    MONTH_NAMES = [calendar.month_name[x].lower() for x in range(1, 13)]
    MONTH_NAMES_ABBREVIATED = [calendar.month_abbr[x].lower() for x in range(1, 13)]

    # Start with Sunday for Indexing.
    DAY_NAMES = [calendar.day_name[x].lower() for x in (6, *range(0, 6))]
    DAY_NAMES_ABBREVIATED = [calendar.day_abbr[x].lower() for x in (6, *range(0, 6))]

# German language has masculine, feminine, and neuter forms for entities of calendar nouns.
# https://deutsch.lingolia.com/en/grammar/nouns-and-articles/gender
# Examples: nächster Montag, dieser Januar, diese Woche, vorheriges Jahr
# Examples: kommenden Januar, letzten März, aktuelles Jahr
NEXT_MN = "nächster"
NEXT_MG = "nächsten"
NEXT_F = "nächste"
NEXT_N = "nächstes"
THIS_MN = "dieser"
THIS_MG = "diesen"
THIS_F = "diese"
THIS_N = "dieses"
PREVIOUS_MN = "vorheriger"
PREVIOUS_MG = "vorherigen"
PREVIOUS_F = "vorherige"
PREVIOUS_N = "vorheriges"


class DateParserGerman(DateParser):
    def __init__(
        self,
        tz="local",
        support_periods=True,
        always_return_period=True,
        format_templates=None,
        unfiltered_words=None,
        strict=True,
    ):
        # What timezone to use?
        self.tz = tz

        # Try to split what's passed in into two dates?
        self.support_periods = support_periods

        # Should two dates always be returned? If a single day is passed,
        # you will be given that day as the start and end date
        self.always_return_period = always_return_period

        # Length of format string (minus brackets) must exactly match string
        self.strict = strict

        # Variables here are written in the order they're
        # applied, although they may be interleaved with additional
        # transformations.

        # These variables modify date ranges
        self.splitters = {
            " bis ",
            " - ",
            # Because German does not use the dash as an in-date separator,
            # it can be used to separate date ranges.
            "-",
        }

        self.period_transformations = [lambda s: s.lower(), lambda s: s.strip()]

        # These variables modify dates
        self.pre_word_replace_date_transformations = [lambda s: s.lower(), lambda s: s.strip()]

        # Formats are separated by spaces only. So convert any other separator
        # you want to a space.
        self.space_strings = {"-", "/", ","}

        self.replaced_words = {
            "im": NEXT_MN,
            "kommender": NEXT_MN,
            "kommenden": NEXT_MG,
            "kommende": NEXT_F,
            "kommendes": NEXT_N,
            "aktueller": THIS_MN,
            "aktuellen": THIS_MG,
            "aktuelle": THIS_F,
            "aktuelles": THIS_N,
            "letzter": PREVIOUS_MN,
            "letzten": PREVIOUS_MG,
            "letzte": PREVIOUS_F,
            "letztes": PREVIOUS_N,
        }

        for i, day in enumerate(DAY_NAMES):
            self.replaced_words[day] = DAY_NAMES_ABBREVIATED[i]
        for i, month in enumerate(MONTH_NAMES):
            self.replaced_words[month] = MONTH_NAMES_ABBREVIATED[i]

        # These variables modify dates
        self.unfiltered_words: Tuple[str]
        self.post_word_replace_date_transformations = [
            lambda s: " ".join(x for x in s.split(" ") if x in self.unfiltered_words or not x.isalpha()),
        ]

        self.regex_replacements = {
            re.compile(x): y
            for x, y in {
                r"\s+": " ",
            }.items()
        }

        _day_formats = ("DD", "D")  # {d}
        _month_formats = ("MMMM", "MMM", "MM", "M")  # {m}
        _year_formats = ("YYYY", "YY")  # {y}
        _time_formats = ("LT", "LTS")  # {t}

        # All format templates must use title case. Conversion will be handled.
        if format_templates is None:
            format_templates = {
                # Yearless
                "{d}. {m}",
                "{d} {m}",
                # # Monthless
                # 'DDDD [Day Of] YYYY', # noqa: ERA001
                # # Dayless             # noqa: ERA001
                # '{m} YYYY',           # noqa: ERA001
                # Full
                "{d}.{m}.{y}",
                "{d}. {m} {y}",
            }  # noqa: ERA001
            format_templates.update(
                # {'%s {t}' % x for x in format_templates}          # noqa: ERA001
                # | {'%s [At] {t}' % x for x in format_templates}   # noqa: ERA001
            )

        self.date_formats = [
            f.format(d=d, m=m, y=y, t=t)
            for d, m, y, t, f in product(_day_formats, _month_formats, _year_formats, _time_formats, format_templates)
        ]

        # Unfortunately this appears to be necessary for consistent behavior
        def _format_sorter(fmt):
            priority = 0
            priority += ("YYYY" in fmt) * 1000
            priority += ("MMM" in fmt) * 100
            priority += ("MMM" not in fmt and "MM" in fmt or "M" in fmt) * 10
            priority += ("DD" in fmt or "D" in fmt) * 1
            priority += 1 // len(fmt)
            return priority

        self.date_formats = sorted(self.date_formats, key=_format_sorter, reverse=True)

        # Words that are not filtered (replacements -> this -> regex)
        self.unfiltered_words = unfiltered_words

        # Use default filter
        if self.unfiltered_words is None:
            self.unfiltered_words = (
                *MONTH_NAMES_ABBREVIATED,
                *DAY_NAMES_ABBREVIATED,
                *[x.strip() for x in self.splitters],
                "jetzt",
                "heute",
                "morgen",
                "gestern",
                THIS_MN,
                THIS_MG,
                THIS_F,
                THIS_N,
                PREVIOUS_MN,
                PREVIOUS_MG,
                PREVIOUS_F,
                PREVIOUS_F,
                NEXT_MN,
                NEXT_MG,
                NEXT_F,
                NEXT_N,
                "jahr",
                "monat",
                "woche",
                "of",
            )

        self.refresh_dates()

    def refresh_dates(self):
        """
        Anything that sets an attribute with a datetime relative to the
        present is set here.
        """
        self.now = pendulum.now(self.tz)
        self.today = pendulum.today(self.tz)
        self.this_week = self.today.start_of("week")
        self.next_week = self.this_week.add(weeks=1)
        self.previous_week = self.this_week.subtract(weeks=1)
        self.this_month = self.today.start_of("month")
        self.next_month = self.this_month.add(months=1)
        self.previous_month = self.this_month.subtract(months=1)
        self.this_year = self.today.start_of("year")
        self.next_year = self.this_year.add(years=1)
        self.previous_year = self.this_year.subtract(years=1)

        # Strings with direct date translations
        self.date_phrases = {
            "jetzt": self.now,
            "heute": self.today,
            "morgen": self.today.add(days=1),
            "gestern": self.today.subtract(days=1),
            f"{THIS_MN} monat": self.this_month,
            f"{THIS_MG} monat": self.this_month,
            f"{NEXT_MN} monat": self.next_month,
            f"{NEXT_MG} monat": self.next_month,
            f"{PREVIOUS_MN} monat": self.previous_month,
            f"{PREVIOUS_MG} monat": self.previous_month,
            f"{THIS_F} woche": self.this_week,
            f"{NEXT_F} woche": self.next_week,
            f"{PREVIOUS_F} woche": self.previous_week,
            f"{THIS_N} jahr": self.this_year,
            f"{NEXT_N} jahr": self.next_year,
            f"{PREVIOUS_N} jahr": self.previous_year,
        }

        # Strings with direct period translations
        self.period_phrases = {
            f"{THIS_MN} monat": pendulum.period(self.this_month, self.this_month.end_of("month")),
            f"{THIS_MG} monat": pendulum.period(self.this_month, self.this_month.end_of("month")),
            f"{NEXT_MN} monat": pendulum.period(self.next_month, self.next_month.end_of("month")),
            f"{NEXT_MG} monat": pendulum.period(self.next_month, self.next_month.end_of("month")),
            f"{PREVIOUS_MN} monat": pendulum.period(self.previous_month, self.previous_month.end_of("month")),
            f"{PREVIOUS_MG} monat": pendulum.period(self.previous_month, self.previous_month.end_of("month")),
            f"{THIS_F} woche": pendulum.period(self.this_week, self.this_week.end_of("week")),
            f"{NEXT_F} woche": pendulum.period(self.next_week, self.next_week.end_of("week")),
            f"{PREVIOUS_F} woche": pendulum.period(self.previous_week, self.previous_week.end_of("week")),
            f"{THIS_N} jahr": pendulum.period(self.this_year, self.this_year.end_of("year")),
            f"{PREVIOUS_N} jahr": pendulum.period(self.next_year, self.next_year.end_of("year")),
        }

        def set_phrase(*prefixes, key, value):
            for prefix in prefixes:
                key_effective = f"{prefix} {key}"
                self.date_phrases[key_effective] = value

        for i, day in enumerate(DAY_NAMES_ABBREVIATED):
            set_phrase(NEXT_MN, NEXT_MG, key=day, value=self.today.next(i))
            set_phrase(PREVIOUS_MN, PREVIOUS_MG, key=day, value=self.today.previous(i))

            if self.today.day_of_week == i:
                self.date_phrases[day] = self.today
                set_phrase(THIS_MN, THIS_MG, key=day, value=self.today)
            else:
                self.date_phrases[day] = self.today.next(i)
                set_phrase(THIS_MN, THIS_MG, key=day, value=self.today.next(i))

        for i, month in enumerate(MONTH_NAMES_ABBREVIATED):
            set_phrase(NEXT_MN, NEXT_MG, key=month, value=self.next_month.add(months=(i + 1) - self.next_month.month))
            set_phrase(
                PREVIOUS_MN,
                PREVIOUS_MG,
                key=month,
                value=self.previous_month.subtract(months=(i + 1) - self.previous_month.month),
            )
            self.date_phrases[month] = self.this_month.add(months=(i + 1) - self.this_month.month)
            set_phrase(THIS_MN, THIS_MG, key=month, value=self.this_month.add(months=(i + 1) - self.this_month.month))

            month_phrases = [
                f"{NEXT_MN} {month}",
                f"{NEXT_MG} {month}",
                f"{PREVIOUS_MN} {month}",
                f"{PREVIOUS_MG} {month}",
                month,
                f"{THIS_MN} {month}",
                f"{THIS_MG} {month}",
            ]
            for month_phrase in month_phrases:
                self.period_phrases[month_phrase] = pendulum.period(
                    self.date_phrases[month_phrase], self.date_phrases[month_phrase].end_of("month")
                )
