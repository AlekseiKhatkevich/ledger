class AssetNotFoundError(Exception):
    def __init__(self, extra: dict | None = None) -> None:
        self.extra = extra if extra is not None else {}


class UserAssetAddressNotFoundError(AssetNotFoundError):
    pass

class UserAssetNotFoundError(AssetNotFoundError):
    pass

class UserAssetOperationNotFoundError(AssetNotFoundError):
    pass



class BalanceError(Exception):
    def __init__(self, extra: dict | None = None) -> None:
        self.extra = extra if extra is not None else {}


class NotEnoughBalanceToSell(BalanceError):
    pass


