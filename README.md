# Mailcoach Python Client

A simple Python wrapper for the Mailcoach API.

## Features

- [x] email lists  
- [x] tags  
- [x] campaigns  
- [ ] subscribers  
- [ ] subscriber import  
- [ ] templates  
- [ ] transactional  
- [ ] send  
- [ ] suppressions 

## Usage

```python
from mailcoach.client import MailCoachClient

# initialize client
client = MailCoachClient(
    token="your_api_token",
    url_root="https://your-mailcoach-instance.com/api/v1",
)

# get one email list
res = client.email_lists.get("email_list_uuid")

# list all
for email in client.email_lists.get_all():
    print(email["uuid"], email["name"])
