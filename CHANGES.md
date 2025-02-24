# Changelog

## in progress
- Naming things: Renamed argument `snap_days` to `snap_hours`
- Formatting: Added formatter for Opsgenie API query clause
- Formatting: Added formatter for GitHub Search API query clause
- `TimeInterval`: Made `end` argument optional

## 2025-02-24 v0.2.1
- Emit better error message when German locales are not installed

## 2025-02-24 v0.2.0
- Maintenance: Add support for macOS, Windows, and Python 3.12 & 3.13
- dudp-parser: Added new "dudp" parser, using `python-dateutil` and `dateparser`
- Naming things: Use `TimeIntervalParser`, and return `TimeInterval` objects
- Improved compatibility and correctness
- Added support for shorthand notations for weeks, months, years,
  like `2025W01`, `2025M02`, `2025Q03`, `2025`
- arbitrary-dateparser: Vendorize vanilla version 0.0.4
- dudp-parser: Added tests and documentation verifying time deltas

## 2023-08-23 v0.1.0
- Initial thing, using `arbitrary-dateparser` and `DateRangeParser` packages
- Add German variants of `arbitrary-dateparser` and `DateRangeParser`
- Add `parse_single` method, for parsing a single point in time
