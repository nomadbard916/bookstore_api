from utils.db_functions import (
    db_get_author,
    db_get_author_from_id,
    db_get_book_with_isbn,
    db_insert_personel,
    db_check_personel,
    db_patch_author_name,
)
from fastapi import Body, File, APIRouter
from models.book import Book
from models.user import User
from models.author import Author
from starlette.status import HTTP_201_CREATED
from starlette.responses import Response
from utils.helper_functions import upload_image_to_server

app_v1 = APIRouter()


@app_v1.post("/user", status_code=HTTP_201_CREATED, tags=["User"])
async def post_user(user: User):
    await db_insert_personel(user)
    return {"result": "personel is created"}


@app_v1.post("/login", tags=["user"])
async def get_user_validation(username: str = Body(...), password: str = Body(...)):
    result = await db_check_personel(username, password)

    return {"is_valid": result}


@app_v1.get(
    "/book/{isbn}",
    response_model=Book,
    response_model_include={"name", "year"},
    tags=["Book"],
)
async def get_book_with_isbn(isbn: str):
    book = await db_get_book_with_isbn(isbn)
    author = await db_get_author(book["author"])

    author_obj = Author(**author)
    book["author"] = author_obj

    result_book = Book(**book)

    return result_book


@app_v1.get("/author/{id}/book")
async def get_authors_books(id: int, order: str = "asc"):
    author = await db_get_author_from_id(id)
    if author is None:
        return {"result": "no author with corresponding id !"}

    books = author["books"]
    if order == "asc":
        books = sorted(books)
    else:
        books = sorted(books, reverse=True)

    return {"books": books}


@app_v1.patch("/author/{id}/name")
async def patch_author_name(id: int, name: str = Body(..., embed=True)):
    await db_patch_author_name(id, name)
    return {"result": "name is updated"}


@app_v1.post("/user/author")
async def post_user_and_author(
    user: User, author: Author, bookstore_name: str = Body(..., embed=True)
):

    return {"user": user, "author": author, "bookstore": bookstore_name}


@app_v1.post("/user/photo")
async def upload_user_photo(response: Response, profile_photo: bytes = File(...)):
    await upload_image_to_server(profile_photo)
    return {"file size": len(profile_photo)}
