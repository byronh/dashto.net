class DisconnectError(Exception):
    pass


class NotAuthorizedError(DisconnectError):
    pass
