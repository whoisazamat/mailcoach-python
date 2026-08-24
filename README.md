# Mailcoach Python Client

A Python client for the [Mailcoach](https://www.mailcoach.app) API.

Mirrors the surface of the official [PHP SDK](https://github.com/spatie/mailcoach-sdk-php): every
endpoint it exposes is available here, and nothing beyond it is invented.

## Requirements

Python 3.11+

## Installation

Not on PyPI yet. For now:

```bash
pip install git+https://github.com/whoisazamat/mailcoach-python.git
```

## Quick start

```python
from mailcoach import MailCoachClient

client = MailCoachClient(
    token="your_api_token",
    url_root="https://your-domain.mailcoach.app",
)

for email_list in client.email_lists.get_all():
    print(email_list["uuid"], email_list["name"])
```

`url_root` is your Mailcoach host **without** `/api` — the client appends it.

The client holds a connection pool, so reuse one instance. Close it when you are done, or use it as
a context manager:

```python
with MailCoachClient(token="...", url_root="https://your-domain.mailcoach.app") as client:
    ...
```

Requests time out after 30 seconds. Override with `MailCoachClient(..., timeout=60)`.

## Resources

Every resource hangs off the client. Which operations exist depends on what the API supports —
transactional mails, for instance, have no `add()` because you cannot create one after the fact.

| Attribute | Endpoint | Operations |
|---|---|---|
| `client.email_lists` | `email-lists` | `get_all` `get` `add` `update` `delete` |
| `client.tags` | `email-lists/{email_list_uuid}/tags` | `get_all` `get` `add` `update` `delete` |
| `client.subscribers` | `email-lists/{email_list_uuid}/subscribers` | `get_all` `get` `add` `update` `delete` `find_by_email` `confirm` `unsubscribe` `resubscribe` `resend_confirmation` |
| `client.campaigns` | `campaigns` | `get_all` `get` `add` `update` `delete` `schedule` `send` `send_test` `opens` `clicks` `unsubscribes` `bounces` |
| `client.templates` | `templates` | `get_all` `get` `add` `update` `delete` |
| `client.automation_mails` | `automation-mails` | `get_all` `get` `add` `update` `delete` |
| `client.automations` | `automations/{uuid}/trigger` | `trigger` |
| `client.transactional_mails` | `transactional-mails` | `get_all` `get` `send` |
| `client.transactional_mail_templates` | `transactional-mails/templates` | `get_all` `get` |

`client.tags` exposes `get_all()` and `get()`, which the PHP SDK does not.

## Common operations

`get_all()` returns an iterator and follows the API's pagination links for you, so a listing of any
size is one loop and one page in memory at a time:

```python
for subscriber in client.subscribers.get_all(email_list_uuid="..."):
    print(subscriber["email"])
```

Nested resources take their parent's UUID as a keyword argument. Miss one, or pass one that the
endpoint does not take, and you get a `TypeError` at the call — not a malformed request.

```python
campaign = client.campaigns.get("campaign-uuid")

campaign = client.campaigns.add({
    "name": "Weekly digest",
    "email_list_uuid": "...",
    "html": "<html>...</html>",
})

client.campaigns.update("campaign-uuid", {"name": "Weekly digest, revised"})
client.campaigns.delete("campaign-uuid")
```

`get()`, `add()` and `update()` return the item itself, already unwrapped from the API's `data`
envelope. `delete()` returns nothing.

### Filtering

List endpoints accept filters, passed as a mapping and sent as `?filter[name]=value`. Filters carry
across pages on their own.

```python
recent = client.campaigns.get_all(filters={"status": "sent"})

subscriber = client.subscribers.find_by_email("john@example.com", email_list_uuid="...")
if subscriber is None:
    ...
```

`find_by_email()` returns `None` when nothing matches — the one method here that does, because
finding no subscriber for an address is an ordinary outcome rather than a failure.

### Campaigns

```python
client.campaigns.send_test("campaign-uuid", ["you@example.com"])
client.campaigns.schedule("campaign-uuid", "2026-01-01 18:00:00", {"name": "New year mail"})
client.campaigns.send("campaign-uuid")

for open_event in client.campaigns.opens("campaign-uuid"):
    print(open_event["subscriber"]["email"])
```

`opens()`, `clicks()`, `unsubscribes()` and `bounces()` are paginated iterators, like `get_all()`.

### Subscribers

```python
subscriber = client.subscribers.add(
    {"email": "john@example.com", "first_name": "John"},
    email_list_uuid="...",
)

client.subscribers.confirm(subscriber["uuid"])
client.subscribers.unsubscribe(subscriber["uuid"])
```

A subscriber is created inside an email list but addressed globally afterwards, so `get()`,
`update()` and `delete()` take only its own UUID.

### Transactional mail

```python
client.transactional_mails.send({
    "mail_name": "welcome",
    "to": "john@example.com",
    "subject": "Welcome",
    "replacements": {"first_name": "John"},
})
```

### Automations

```python
client.automations.trigger("automation-uuid", ["subscriber-uuid", "another-subscriber-uuid"])
```

## Errors

Everything the library raises descends from `MailcoachError`, so one `except` catches the lot.
Below it the tree splits by cause, and API failures carry the status and the decoded body rather
than burying them in a message string.

```
MailcoachError
├── RequestError        no usable response: timeout, DNS, TLS, undecodable body
└── APIError            the API answered with a non-2xx status
    ├── AuthenticationError   401, 403
    ├── NotFoundError         404
    ├── ValidationError       422
    └── RateLimitError        429
```

```python
from mailcoach import MailcoachError, RateLimitError, ValidationError

try:
    client.campaigns.add({"name": "No list"})
except ValidationError as error:
    print(error.errors)        # {"email_list_uuid": ["The email list uuid field is required."]}
except RateLimitError as error:
    print(error.retry_after)   # seconds, when the API sends Retry-After
except MailcoachError as error:
    print(error)
```

Every `APIError` carries `status_code` and `body`. A 5xx arrives as a plain `APIError`; branch on
`error.status_code >= 500` if you need to tell server faults apart.

## Development

```bash
pip install -r requirements.txt
pytest          # 152 tests, coverage gate at 100% of lines and branches
ruff check .
mypy
```

Coverage is enforced at 100% for lines and branches, so a new endpoint needs its test to land.
Coverage only proves a line ran, though — correctness of the interesting paths is checked by
mutating the code and confirming a test fails.
