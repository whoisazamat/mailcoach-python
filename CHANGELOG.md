# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-08-25

First release.

### Added

- `MailCoachClient` covering email lists, tags, subscribers, campaigns, templates, automation
  mails, automations and transactional mails — mirroring the surface of the official PHP SDK.
- Typed exception hierarchy under `MailcoachError`: `AuthenticationError`, `NotFoundError`,
  `ValidationError` (with per-field `.errors`), `RateLimitError` (with `.retry_after`), and
  `APIError` carrying `status_code` and the decoded `body`.
- `get_all()` returns an iterator and follows the API's pagination links, one page in memory
  at a time.
- Filtering on list endpoints via `filters={...}`, sent as `?filter[name]=value`.
- Retrying in the transport: `Retry-After` is honoured on 429, connection errors and 5xx back
  off exponentially, bounded by `max_attempts` and `max_retry_wait`.
- Connection pooling through a single `requests.Session`, a 30 second default timeout, and
  context-manager support on the client.
- `py.typed`, so the annotations are visible to consumers' type checkers.

[Unreleased]: https://github.com/whoisazamat/mailcoach-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/whoisazamat/mailcoach-python/releases/tag/v0.1.0
