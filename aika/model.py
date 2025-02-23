# Copyright (c) 2023-2025, The Panodata developers and contributors.
# Distributed under the terms of the LGPL license, see LICENSE.

import dataclasses
import datetime as dt
import typing as t

trange = t.Tuple[dt.datetime, t.Optional[dt.datetime]]


@dataclasses.dataclass
class Parser:
    name: str
    fun: t.Callable


@dataclasses.dataclass
class TimeInterval:
    """
    Mange a single time interval.

    The implementation uses `start` and `end`, because
    `from` and `to` are very likely to be reserved words.
    """

    start: dt.datetime
    end: t.Optional[dt.datetime]

    def isoformat(self) -> str:
        """
        Encode as ISO 8601 time interval.
        https://en.wikipedia.org/wiki/ISO_8601#Time_intervals
        """
        buffer = f"{self.start.isoformat()}"
        if self.end:
            buffer += f"/{self.end.isoformat()}"
        return buffer

    def luceneformat(self) -> str:
        """
        Encode as Lucene range query. Example: [20020101 TO 20030101]

        https://lucene.apache.org/core/2_9_4/queryparsersyntax.html#Range%20Searches
        """
        raise NotImplementedError()

    def mathformat(self) -> str:
        """
        Mathematical interval format, as also used by GitHub: `n..n`.

        A integer interval: [𝑎..𝑏] represents all integers in between 𝑎 and 𝑏.

        You can use the range syntax `n..n` to search for values within a range,
        where the first number N is the lowest value and the second is the highest value.

        https://math.stackexchange.com/a/2056522
        https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax#query-for-values-between-a-range
        """
        buffer = f"{self.start.isoformat()}"
        if self.end:
            buffer += f"..{self.end.isoformat()}"
        return buffer
