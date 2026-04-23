from functools import cache
from typing import Any

from sqlalchemy.ext.automap import automap_base
import anyio

from db.postgres.connection import ledger_db

LedgerBase = automap_base()

__all__ = (
    'ledger_models',
)

@cache
class LedgerModels:
    def __init__(self) -> None:
        anyio.run(ledger_db.prepare_automap, LedgerBase)
        self.AssetTicker = LedgerBase.classes.asset_tickers


ledger_models: LedgerModels
def __getattr__(name: str) -> Any:
    if name == 'ledger_models':
        return LedgerModels()
    raise AttributeError(f'Module {__name__} has no attribute {name}')
