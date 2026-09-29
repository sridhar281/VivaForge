from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """
    Consistent shape for every error the API returns (section 24: never leak
    raw stack traces; always give the client something useful and safe).
    """
    detail: str
