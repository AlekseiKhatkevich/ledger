from litestar import Litestar

from config import settings
from database.postgres.connection import db


def set_settings(app:Litestar) -> None:
    app.state.settings = settings

on_startup = [set_settings,]

on_shutdown = [db.close,]