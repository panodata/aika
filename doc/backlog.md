# Backlog

## Iteration +1
- Add German variant of `arbitrary-dateparser`
- Accept time definitions like `-1d` or `+45min3s`
- Accept durations like `1h30m ago` or `in 45min`
- Special treatments for `{last,this,next} week'

## Iteration +2
- KQL: `@timestamp >= "now-1d/d+11h" AND @timestamp <= "now-1d/d+13h"` searches for all
  @timestamps between in a 2-hour range based on midnight UTC+11h
  -- https://discuss.elastic.co/t/lucene-syntax-equivalent-for-today-does-it-exist/204699/4
- KQL: `2017-08-14T11:56:02||-5m`
  -- https://discuss.elastic.co/t/time-range-raw-timestamp-minus-time/96964/2

## Iteration +3
- Add CLI interface
  - Input: Date range expression
  - Output:
    - Format: ISO8601 time intervals: https://en.wikipedia.org/wiki/ISO_8601#Time_intervals
    - Format: Humanized variant, using `arrow.humanize()`
    - Container: Text, JSON, etc.
- Get locale right, for both timezone handling and humanized output
  - aika/core: FIXME: Do not set timezone explicitly.
  - `arrow.humanize()`
- Synchronize splitters/separators from both libraries
- Do not require locales for other languages to be installed.
  If not, handle it gracefully.
