# Changelog

## 2.0.2
  * Pull webinars by UUID [#32](https://github.com/singer-io/tap-zoom/pull/32)

## 2.0.1
  * Dependabot update [#26](https://github.com/singer-io/tap-zoom/pull/26)

## 2.0.0
- Removed dependency of jwt from tap logic [#20](https://github.com/singer-io/tap-zoom/pull/20)
- Added dev mode support [#19](https://github.com/singer-io/tap-zoom/pull/19)
- Remove deprecated streams and schema changes & integration tests [#18](https://github.com/singer-io/tap-zoom/pull/18)

## 1.1.2
- Increase wait time interval on RateLimitException [#25](https://github.com/singer-io/tap-zoom/pull/25)

## 1.1.1
- Update backoff logic for RateLimitException [#23](https://github.com/singer-io/tap-zoom/pull/23)
- Update API doc links in README.md [#24](https://github.com/singer-io/tap-zoom/pull/24)

## 1.1.0
- Added following changes as part of this release :
  - Add Top level breadcrumb [#14](https://github.com/singer-io/tap-zoom/pull/14)
  - fix to remove repetitive writing of schema during sync [#17](https://github.com/singer-io/tap-zoom/pull/17)
  - Update the singer-python version to latest
  - Add unit test case [#21](https://github.com/singer-io/tap-zoom/pull/21)
  - Update the config.yml [#15](https://github.com/singer-io/tap-zoom/pull/15)

## [v1.0.0](https://github.com/singer-io/tap-zoom/tree/v1.0.0) (2021-03-15)

[Full Changelog](https://github.com/singer-io/tap-zoom/compare/v0.0.3...v1.0.0)

**Merged pull requests:**

- Adding dummy circle file which only runs json validate [\#10](https://github.com/singer-io/tap-zoom/pull/10) ([asaf-erlich](https://github.com/asaf-erlich))
- Fix schema for report meetings and webinars [\#4](https://github.com/singer-io/tap-zoom/pull/4) ([kekoav](https://github.com/kekoav))

## 0.0.3
  * Fixed typo

## 0.0.2
  * Fixes a bug with the ratelimit behavior and a improperly instantiated exception [#6](https://github.com/singer-io/tap-zoom/pull/6)