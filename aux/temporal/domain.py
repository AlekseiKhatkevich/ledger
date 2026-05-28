import dataclasses
import constants


@dataclasses.dataclass
class UpdatePricesWorkflowParams:
    tickers: set[str]
    batch_size: int = constants.LEDGER_PRICES_BATCH_SIZE
