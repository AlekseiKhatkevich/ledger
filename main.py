from litestar import Litestar, get


@get("/health")
async def health() -> dict :
    return {"status":"ok"}


@get("/books/{book_id:int}")
async def get_book333(book_id: int) -> dict[str, int]:
    return {"book_id": book_id}

@get("/t")
async def healtht() -> dict :
    return {"status":"ok"}

@get("/d")
async def healtht1() -> dict :
    return {"status":"ok"}



app = Litestar([health, get_book333, healtht, healtht1])