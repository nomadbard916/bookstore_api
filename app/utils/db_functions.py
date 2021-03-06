from utils.db import execute, fetch
from models.jwt_user import JWTUser


async def db_check_token_user(user: JWTUser):
    query = """select * from users where username = :username"""

    values = {"username": user.username, "password": user.password}

    result = await fetch(query, False, values)

    if result is None:
        return False
    else:
        return True


async def db_check_jwt_username(username):
    query = """select * from users where username = :username"""
    values = {"username": username}

    result = await fetch(query, True, values)
    if result is None:
        return False
    else:
        return True


async def db_insert_personel(user):
    query = """
    --sql
    insert into personel(username,password, mail, role)
    values(:name, :password,:mail, :role)
    --endsql

    """

    values = dict(user)

    await execute(query, False, values)


async def db_check_personel(username, password):
    query = """ --sql
    select * from personel
    where username = :username and password = :password
    --endsql """

    values = {"username": username, "password": password}

    personel = await fetch(query, True, values)

    if personel is None:
        return False
    else:
        return True


async def db_get_book_with_isbn(isbn):
    query = """--sql
        select * from books where isbn=:isbn
    --endsql"""
    values = {"isbn": isbn}
    book = await fetch(query, True, values)

    return book


async def db_get_author(author_name):
    query = """select * from authors where name=:name"""
    values = {"name": author_name}
    author = await fetch(query, True, values)
    return author


async def db_get_author_from_id(id):
    query = """--sql
        SELECT * FROM authors WHERE id=:id
    --endsql"""
    values = {"id": id}
    author = await fetch(query, True, values)

    return author


async def db_patch_author_name(id, name):
    query = """UPDATE authors SET name=:name WHERE id=:id"""
    values = {"name": name, "id": id}
    await execute(query, False, values)
