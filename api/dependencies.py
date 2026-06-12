import datetime

from litestar.params import FromQuery

from api.user_asset_operations.domain import UserAssetOperationsFilter, NoteFilter
from logic.db_models import AssetOperationType


def operations_filter(
    time__gte: FromQuery[datetime.datetime | None] = None,
    time__lte: FromQuery[datetime.datetime | None] = None,
    op_id: FromQuery[list[int] | None] = None,
    op_type: FromQuery[tuple[AssetOperationType, ...]] = tuple(AssetOperationType),
    address_id: FromQuery[list[int] | None] = None
) -> UserAssetOperationsFilter:
    """
    Request list[int] data like &address_id=1&address_id=2&...
    """
    return UserAssetOperationsFilter(
        time__gte=time__gte,
        time__lte=time__lte,
        op_id=op_id,
        op_type=op_type,
        address_id=address_id,
    )

def note_filter(
    note_time__gte: FromQuery[datetime.datetime | None] = None,
    note_time__lte: FromQuery[datetime.datetime | None] = None,
) -> NoteFilter:
    return NoteFilter(note_time__gte=note_time__gte, note_time__lte=note_time__lte)