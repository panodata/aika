# Backlog

## Iteration +1
- Add German variant of `arbitrary-dateparser`
- Accept durations like `1h30m ago` or `in 45min`
- Release 0.1.0
 
## Iteration +2
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
