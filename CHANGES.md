# Changelog

## in progress
- Maintenance: Add support for macOS, Windows, and Python 3.12 & 3.13
- Added new "dudp" parser, using `python-dateutil` and `dateparser`
- Naming things: Use `TimeIntervalParser`, and return `TimeInterval` objects
- Improved compatibility and correctness
- Added support for shorthand notations for weeks, months, years,
  like `2025W01`, `2025M02`, `2025Q03`, `2025`
- arbitrary-dateparser: Vendorize vanilla version 0.0.4

## 2023-08-23 v0.1.0
- Initial thing, using `arbitrary-dateparser` and `DateRangeParser` packages
- Add German variants of `arbitrary-dateparser` and `DateRangeParser`
- Add `parse_single` method, for parsing a single point in time
