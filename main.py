from litestar import Litestar, get


@get("/")
async def readines() -> bool:
    return True


@get("/books/{book_id:int}")
async def get_book333(book_id: int) -> dict[str, int]:
    return {"book_id": book_id}


app = Litestar([readines, get_book333])