class ApplicationException(Exception):

    default_status: int
    default_message: str

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        messages = message
        self.messages = messages or self.default_message
        self.status_code = status_code or self.default_status
        self.payload = payload

    def __str__(self):
        return f"{self.__class__.__name__}: {self.messages}"


class MalformedRequestException(ApplicationException):

    default_status: int = 404
    default_message: str = "malformed request body"


class MissingResourceException(ApplicationException):

    default_status: int = 404
    default_message: str = "the resource you requested cannot be found"


class InvalidArgumentError(ApplicationException):

    default_status: int = 400
    default_message: str = "user passed an invalid argument"


def throw_mre(id: int, model_class):
    msg = f"No {model_class.__name__} with id={id}"
    raise MissingResourceException(msg)
