class MissingContentLengthError(Exception):
    """Raised when the Content-Length header is missing or invalid."""
    pass

class FileTooLargeError(Exception):
    """Raised when the file size exceeds the allowed limit."""
    pass

class NoSupportedFormatAvailable(Exception):
    """Raised when there was no supported format available to download"""
    pass

class InitialLinkFormatError(Exception):
    """Raised when there is a problem with differentiating the link provider"""
    pass

class InstagramError(Exception):
    """Raised when there is a problem with instagram"""
    pass

class FacebookError(Exception):
    """Raised when there is a problem with facebook"""
    pass

class RedditError(Exception):
    """Raised when there is a problem with reddit"""
    pass