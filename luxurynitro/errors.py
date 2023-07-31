from httpx import Response

class Error(Exception):
    """
    Super-class for errors in the library.
    """

class RetryTimeout(Error):
    """
    Request has failed more than the `self.max_retries` value.
    """
    def __init__(self, message:str, errors:list) -> None:
        self.errors = errors
        self.message = message
    
    def __str__(self) -> str:
        return self.message

class APIError(Error):
    """
    Error from the API.
    """
    def __init__(self, message:str, response:Response) -> None:
        self.message = message
        self.response = response
    
    def __str__(self) -> str:
        return self.message

class ValidationError(Error):
    """
    Argument validation failed.
    """