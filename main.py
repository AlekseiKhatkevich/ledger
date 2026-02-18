from litestar import Litestar, get


@get("/health")
async def health() -> dict[str, str]:
    return {"status":"ok"}


@get("/books/{book_id:int}")
async def get_book333(book_id: int) -> dict[str, int]:
    return {"book_id": book_id}


app = Litestar([health, get_book333])