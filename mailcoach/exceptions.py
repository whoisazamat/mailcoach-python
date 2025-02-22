class MailcoachError(Exception):
    pass


class AuthenticationError(MailcoachError):
    pass


class RequestError(MailcoachError):
    pass
