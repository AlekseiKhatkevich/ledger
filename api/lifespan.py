from database.postgres.connection import db

on_startup = ()

on_shutdown = (
    db.close,
)