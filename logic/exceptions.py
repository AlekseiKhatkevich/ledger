class BaseLedgerApiException(Exception):
    def __init__(self, extra: dict | None = None) -> None:
        self.extra = extra if extra is not None else {}


class AssetNotFoundError(BaseLedgerApiException):
    pass

class UserAssetAddressNotFoundError(AssetNotFoundError):
    pass

class UserAssetNotFoundError(AssetNotFoundError):
    pass

class UserAssetOperationNotFoundError(AssetNotFoundError):
    pass



class BalanceError(BaseLedgerApiException):
   pass


class NotEnoughBalanceToSell(BalanceError):
    pass


