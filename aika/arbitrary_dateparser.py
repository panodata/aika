"""
Contains the DateParser module and relevant constants.
"""

import calendar
import re
from itertools import product

import pendulum
from pendulum import WeekDay

MONTH_NAMES = [calendar.month_name[x].lower() for x in range(1, 13)]
MONTH_NAMES_ABBREVIATED = [calendar.month_abbr[x].lower() for x in range(1, 13)]

# Start with Sunday for Indexing.
DAY_NAMES = [calendar.day_name[x].lower() for x in range(7)]
DAY_NAMES_ABBREVIATED = [calendar.day_abbr[x].lower() for x in range(7)]


class DateParser:
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
        self.splitters = {" to ", " - ", " through "}

        self.period_transformations = [lambda s: s.lower(), lambda s: s.strip()]

        # These variables modify dates
        self.pre_word_replace_date_transformations = [lambda s: s.lower(), lambda s: s.strip()]

        # Formats are separated by spaces only. So convert any other separator
        # you want to a space.
        self.space_strings = {"-", "/", ".", ","}

        self.replaced_words = {"last": "previous", "current": "this"}

        for i, day in enumerate(DAY_NAMES):
            self.replaced_words[day] = DAY_NAMES_ABBREVIATED[i]
        for i, month in enumerate(MONTH_NAMES):
            self.replaced_words[month] = MONTH_NAMES_ABBREVIATED[i]

        # These variables modify dates
        self.post_word_replace_date_transformations = [
            lambda s: " ".join(x for x in s.split(" ") if x in self.unfiltered_words or not x.isalpha()),  # type: ignore[has-type]
        ]

        self.regex_replacements = {
            re.compile(x): y
            for x, y in {
                r"(\d)st": r"\1",
                r"(\d)nd": r"\1",
                r"(\d)rd": r"\1",
                r"(\d)th": r"\1",
                r"\s+": " ",
            }.items()
        }

        _day_formats = ("DD", "D")  # {d}
        _month_formats = ("MMMM", "MMM", "MM")  # {m}
        _year_formats = ("YYYY", "YY")  # {y}
        _time_formats = ("LT", "LTS")  # {t}

        # All format templates must use title case. Conversion will be handled.
        if format_templates is None:
            format_templates = {
                # Yearless
                "{m} {d}",
                "{d} [Of] {m}",
                # Monthless
                # 'DDDD [Day Of] YYYY',  # noqa: ERA001
                # Dayless
                # '{m} YYYY',  # noqa: ERA001
                # Full
                "{m} {d} {y}",
                "{d} [Of] {m} {y}",
            }
            format_templates.update(
                # {'%s {t}' % x for x in format_templates}  # noqa: ERA001
                # | {'%s [At] {t}' % x for x in format_templates}
            )

        self.date_formats = list(
            {
                f.format(d=d, m=m, y=y, t=t)
                for d, m, y, t, f in product(
                    _day_formats, _month_formats, _year_formats, _time_formats, format_templates
                )
            }
        )

        # Unfortunately this appears to be necessary for consistent behavior
        def _format_sorter(fmt):
            priority = 0
            priority += ("YYYY" in fmt) * 1000
            priority += ("MMM" in fmt) * 100
            priority += ("MMM" not in fmt and "MM" in fmt) * 10
            priority += ("DD" in fmt) * 1
            priority += int(1 / len(fmt))
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
                "now",
                "today",
                "tomorrow",
                "yesterday",
                "this",
                "previous",
                "next",
                "year",
                "month",
                "week",
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
            "now": self.now,
            "today": self.today,
            "tomorrow": self.today.add(days=1),
            "yesterday": self.today.subtract(days=1),
            "this month": self.this_month,
            "next month": self.next_month,
            "previous month": self.previous_month,
            "this week": self.this_week,
            "next week": self.next_week,
            "previous week": self.previous_week,
            "this year": self.this_year,
            "next year": self.next_year,
            "previous year": self.previous_year,
        }

        # Strings with direct period translations
        self.period_phrases = {
            "this month": pendulum.Interval(self.this_month, self.this_month.end_of("month")),
            "next month": pendulum.Interval(self.next_month, self.next_month.end_of("month")),
            "previous month": pendulum.Interval(self.previous_month, self.previous_month.end_of("month")),
            "this week": pendulum.Interval(self.this_week, self.this_week.end_of("week")),
            "next week": pendulum.Interval(self.next_week, self.next_week.end_of("week")),
            "previous week": pendulum.Interval(self.previous_week, self.previous_week.end_of("week")),
            "this year": pendulum.Interval(self.this_year, self.this_year.end_of("year")),
            "previous year": pendulum.Interval(self.next_year, self.next_year.end_of("year")),
        }

        for i, day in enumerate(DAY_NAMES_ABBREVIATED):
            self.date_phrases[f"next {day}"] = self.today.next(WeekDay(i))
            self.date_phrases[f"previous {day}"] = self.today.previous(WeekDay(i))

            if self.today.day_of_week == i:
                self.date_phrases[day] = self.today
                self.date_phrases[f"this {day}"] = self.today
            else:
                self.date_phrases[day] = self.today.next(WeekDay(i))
                self.date_phrases[f"this {day}"] = self.today.next(WeekDay(i))

        for i, month in enumerate(MONTH_NAMES_ABBREVIATED):
            self.date_phrases[f"next {month}"] = self.next_month.add(months=(i + 1) - self.next_month.month)
            self.date_phrases[f"previous {month}"] = self.previous_month.subtract(
                months=(i + 1) - self.previous_month.month
            )
            self.date_phrases[month] = self.this_month.add(months=(i + 1) - self.this_month.month)
            self.date_phrases[f"this {month}"] = self.this_month.add(months=(i + 1) - self.this_month.month)

            for month_phrase in (f"next {month}", f"previous {month}", month, f"this {month}"):
                self.period_phrases[month_phrase] = pendulum.Interval(
                    self.date_phrases[month_phrase], self.date_phrases[month_phrase].end_of("month")
                )

    def __call__(self, string, refresh=True):
        _unmodified_string = string

        if refresh:
            self.refresh_dates()

        if not self.support_periods:
            return self._normalize_and_convert(string)

        for f in self.period_transformations:
            string = f(string)

        for word, replacement in self.replaced_words.items():
            string = string.replace(word, replacement)

        try:
            return self.period_phrases[string]
        except KeyError:
            datetimes = self.split_datetime_string(string)

        if len(datetimes) == 1:
            dt = self._normalize_and_convert(string)
            return self._handle_singlet(dt)

        elif len(datetimes) == 2:
            str_1 = self.normalize_date(datetimes[0])
            str_2 = self.normalize_date(datetimes[1])

            try:
                dt_1 = min(self.period_phrases[str_1])
            except KeyError:
                dt_1 = self.convert_normalized_date(str_1, False)

            try:
                dt_2 = max(self.period_phrases[str_2])
            except KeyError:
                dt_2 = self.convert_normalized_date(str_2, False)

            start, end = min(dt_1, dt_2), max(dt_1, dt_2)
            return pendulum.Interval(start, end)

        raise ValueError(f"Cannot parse string: {string} (original: {_unmodified_string})")

    def _handle_singlet(self, dt):
        if self.always_return_period:
            return pendulum.Interval(dt, dt.end_of("day"))
        else:
            return dt

    def _normalize_and_convert(self, string, refresh=False):
        string = self.normalize_date(string)
        return self.convert_normalized_date(string, refresh)

    def split_datetime_string(self, string):
        return sorted((string.split(x) for x in self.splitters), key=lambda split: len(split), reverse=True)[0]

    def normalize_date(self, string):
        for f in self.pre_word_replace_date_transformations:
            string = f(string)

        for space_string in self.space_strings:
            string = string.replace(space_string, " ")

        for word, replacement in self.replaced_words.items():
            string = string.replace(word, replacement)

        for f in self.post_word_replace_date_transformations:
            string = f(string)

        for pattern, replacement in self.regex_replacements.items():
            string = pattern.sub(replacement, string)

        return string

    def convert_normalized_date(self, string, refresh=True):
        if refresh:
            self.refresh_dates()

        # Try a known key phrase
        try:
            return self.date_phrases[string]
        except KeyError:
            pass

        # Try all of the known date formats
        for date_format in self.date_formats:
            try:
                dt = pendulum.from_format(string.title(), date_format)

                # Try to get behavior closer to the datetime module
                if self.strict:
                    no_brackets = date_format.replace("[", "").replace("]", "")
                    if len(no_brackets) != len(string):
                        continue

                # Bug fix: "Jan 1 18" being parsed as 01 01 0018
                if not self.strict and dt.year < 100:
                    has_full_year = any(len(x) == 4 and x.isnumeric() for x in string.split(" "))
                    if not has_full_year:
                        dt = dt.add(years=2000)
                return dt
            except ValueError:
                pass

        raise ValueError(f"Unsupported date string {string}")
