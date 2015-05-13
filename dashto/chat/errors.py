class ClientError(Exception):
    pass


class ServerError(Exception):
    pass


class DisconnectError(ClientError):
    pass


class NotAuthorizedError(DisconnectError):
    pass


class FatalServerError(ServerError):
    pass
