from models.author import Author
from pydantic import BaseModel


class Book(BaseModel):
    isbn: str
    name: str
    author: Author
    year: int
    # isbn: str = Schema(None, description=ISBN_DESCRIPTION)
    # name: str                                                                          , password: str =     (...)):
    # author: Author
    # year: int = Schema(None, gt=1900, lt=2100)
