# Copyright (c) 2023, The Panodata developers and contributors.
# Distributed under the terms of the LGPL license, see LICENSE.

import dataclasses
import datetime as dt
import typing as t

trange = t.Tuple[dt.datetime, t.Optional[dt.datetime]]


@dataclasses.dataclass
class Parser:
    name: str
    fun: t.Callable
