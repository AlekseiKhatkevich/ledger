import asyncio
from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.stdlib import get_logger

from database.postgres.connection import db
from logic.db_models import Note
from logic.embedding import TextEmbeddingService

logger = get_logger()

BATCH_SIZE = 10


async def notes_without_embedding(session: AsyncSession) -> AsyncGenerator[Note, None]:
    stmt = select(Note).where(Note.embedding.is_(None)).order_by(Note.id)
    result = await session.stream(stmt)
    async for row in result:
        yield row[0]


async def main() -> None:
    embedding_service = TextEmbeddingService()
    total = 0
    failed = 0

    async with db.session() as session:
        notes_batch: list[Note] = []
        async for note in notes_without_embedding(session):
            notes_batch.append(note)
            if len(notes_batch) >= BATCH_SIZE:
                texts = [n.note for n in notes_batch]
                try:
                    embeddings = await embedding_service.embed_batch(texts)
                    for n, emb in zip(notes_batch, embeddings, strict=True):
                        n.embedding = emb
                    total += len(notes_batch)
                    await session.commit()
                    logger.info('processed_notes', count=total)
                except Exception:
                    logger.exception('failed_to_embed_batch', note_ids=[n.id for n in notes_batch])
                    failed += len(notes_batch)
                notes_batch = []

        # Process remaining notes
        if notes_batch:
            texts = [n.note for n in notes_batch]
            try:
                embeddings = await embedding_service.embed_batch(texts)
                for n, emb in zip(notes_batch, embeddings, strict=True):
                    n.embedding = emb
                total += len(notes_batch)
                await session.commit()
            except Exception:
                logger.exception('failed_to_embed_batch', note_ids=[n.id for n in notes_batch])
                failed += len(notes_batch)

    logger.info('embedding_fill_complete', total=total, failed=failed)


if __name__ == '__main__':
    asyncio.run(main())