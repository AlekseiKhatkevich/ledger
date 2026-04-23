# from functools import cache
#
# import anyio
# from sqlalchemy.ext.automap import automap_base
#
# from db.postgres.connection import ledger_db
#
# LedgerBase = automap_base()
#
#
# @cache
# class LedgerModels:
#     def __init__(self) -> None:
#         self.AssetTicker = LedgerBase.classes.asset_tickers
#
#     async def