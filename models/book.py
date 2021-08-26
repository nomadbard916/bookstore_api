from pydantic.fields import Field
from utils.const import ISBN_DESCRIPTION
from models.author import Author
from pydantic import BaseModel


class Book(BaseModel):
    isbn: str = Field(None, description=ISBN_DESCRIPTION)
    name: str
    author: Author
    year: int = Field(None, gt=1900, lt=2100)
