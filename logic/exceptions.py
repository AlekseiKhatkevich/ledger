class AssetNotFoundError(Exception):
    def __init__(self, extra: dict | None = None) -> None:
        self.extra = extra if extra is not None else {}


class UserAssetAddressNotFoundError(AssetNotFoundError):
    pass

class UserAssetNotFoundError(AssetNotFoundError):
    pass

class UserAssetOperationNotFoundError(AssetNotFoundError):
    pass


