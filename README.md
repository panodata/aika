# Aika

[![Status][badge-status]][project-pypi]
[![CI][badge-ci]][project-ci]
[![Coverage][badge-coverage]][project-coverage]
[![Downloads per month][badge-downloads-per-month]][project-downloads]

[![License][badge-license]][project-license]
[![Release Notes][badge-release-notes]][project-release-notes]
[![PyPI Version][badge-package-version]][project-pypi]
[![Python Versions][badge-python-versions]][project-pypi]

## About

Time interval parsing utilities for multiple languages.

## Details

Aika provides date- and time-range parsing utilities for multiple languages.
It is based on [dateparser], [arbitrary-dateparser], and [DateRangeParser],
and aims for [DWIM]-like convenience and usefulness.

Currently, it supports 200 language locales through `dateparser`, and more
specific support for English and German through `arbitrary-dateparser`.
Contributions for other languages are welcome.


## Setup

Install the most recent version of Aika.
```shell
pip install --upgrade aika
```


## Usage

```doctest
>>> import datetime as dt
>>> from aika import TimeIntervalParser
>>> 
>>> ti = TimeIntervalParser()
>>>
>>> ti.parse("Sat - Tue")
>>> (dt.datetime(2023, 8, 26, 0, 0), dt.datetime(2023, 8, 29, 23, 59, 59, 999999))
>>>
>>> ti.parse_single("1. Juli")
>>> dt.datetime(2023, 7, 1, 0, 0)
```


### Example Expressions

Aika understands all types of date-/time-range expressions like provided by the
packages it is based upon, and works with single dates too. This section enumerates
a few examples.

#### dateparser

##### Calendar notations
- Week: 2025W01
- Month: 2025M02, 2025-02
- Quarter: 2025Q03
- Year: 2025

##### Time deltas
- Day: `-1d`, `-1 day`
- Week: `-1w`, `-1 week`
- Month: `-1M`, `-1 month`
- Year: `-1y`, `-1 year`
- Quarter: `-3M`, `-3 months`
- Mixed: `-3d3h5m30s`

#### arbitrary-dateparser » English

- now
- today
- last week to next friday
- tomorrow - next week
- next month
- december
- July to December
- jul 1 to jul 7
- Sat - Tue
- in March
- 2024-08-20

#### arbitrary-dateparser » German

- jetzt
- heute
- letzte woche bis nächsten freitag
- morgen - nächste woche
- nächster monat
- dezember
- Juli-Dezember
- jul 1 to jul 7
- von Samstag bis Dienstag
- im März
- 20\. August 2024
- 20.8.2024
- 20.08.2024

#### DateRangeParser » English

- 1st july
- March 2024
- July to December
- 27th-29th June 2010
- 30 May to 9th Aug
- 3rd Jan 1980 -- 2nd Jan 2013
- Wed 23 Jan -> Sat 16 February 2013
- Tuesday 29 May - Sat 2 June 2012
- From 1 to 9 Jul
- jul 1 to jul 9
- 14th July 1988
- Jan 2011 - Mar 2014 
- 07:00 Tue 7th June - 17th July 3:30pm
  <br>**Caveat**: Times will currently be ignored.

#### DateRangeParser » German

- 1\. Juli
- 1\. bis 7. Juli
- März 2024
- Juli bis Dezember
- Vom 3. März bis zum 9. März 2024


## Advanced Usage

By specifying `default_start_time` and `default_end_time` arguments, the
daterange boundaries will snap to the given times when they otherwise would be
"beginning of day" (00:00) or "end of day" (23:59).

```python
import datetime as dt
from aika import TimeIntervalParser

dr = TimeIntervalParser(
    snap_hours=True,
    default_start_time=dt.time(hour=9),
    default_end_time=dt.time(hour=17),
)
dr.parse("Sat - Tue")
```
```python
(datetime(2023, 8, 26, 9, 0), datetime(2023, 8, 29, 17, 0))
```


## Troubleshooting

If you see an error message like `locale.Error: unsupported locale setting` for
code like this,
```python
import locale

locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
```

you will need to generate the German locales.
```shell
apt-get update
apt-get install --yes tzdata locales
locale-gen de_DE.UTF-8
```


## Development

Acquire source code and install development sandbox.
```shell
git clone https://github.com/panodata/aika
cd aika
uv venv --seed --python 3.11
source .venv/bin/activate
uv pip install --editable='.[develop,docs,test]'
```

Run linters and software tests:
```shell
source .venv/bin/activate
poe check
```


## Etymology

Aika means "time" in the Finnish language.

## Acknowledgements

- [Elias Dorneles] and contributors for conceiving and maintaining [dateparser].
- [Michael Phelps] for conceiving [arbitrary-dateparser].
- [Robin Wilson] and contributors for conceiving and maintaining [DateRangeParser].


[arbitrary-dateparser]: https://pypi.org/project/arbitrary-dateparser/
[dateparser]: https://pypi.org/project/dateparser/
[DateRangeParser]: https://pypi.org/project/DateRangeParser/
[DWIM]: https://en.wikipedia.org/wiki/DWIM
[Elias Dorneles]: https://github.com/eliasdorneles
[Michael Phelps]: https://github.com/nottheswimmer
[Robin Wilson]: https://github.com/robintw

[badge-ci]: https://github.com/panodata/aika/actions/workflows/main.yml/badge.svg
[badge-coverage]: https://codecov.io/gh/panodata/aika/branch/main/graph/badge.svg
[badge-downloads-per-month]: https://pepy.tech/badge/aika/month
[badge-license]: https://img.shields.io/github/license/panodata/aika
[badge-package-version]: https://img.shields.io/pypi/v/aika.svg
[badge-python-versions]: https://img.shields.io/pypi/pyversions/aika.svg
[badge-release-notes]: https://img.shields.io/github/release/panodata/aika?label=Release+Notes
[badge-status]: https://img.shields.io/pypi/status/aika.svg
[project-ci]: https://github.com/panodata/aika/actions/workflows/main.yml
[project-coverage]: https://app.codecov.io/gh/panodata/aika
[project-downloads]: https://pepy.tech/project/aika/
[project-license]: https://github.com/panodata/aika/blob/main/LICENSE
[project-pypi]: https://pypi.org/project/aika
[project-release-notes]: https://github.com/panodata/aika/releases
