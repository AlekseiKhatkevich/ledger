from typing import Annotated

from litestar import Controller, post, put, delete, get
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.params import FromPath, FromQuery, QueryParameter

from api.dependencies import operations_filter, note_filter
from api.exceptions_handling import base_error_handler_factory
from api.notes.domain import SearchMethod
from api.user_asset_operations.domain import (
    UserAssetOperationData,
    UserAssetOperationDTOOut,
    UserAssetOperationDTOIn,
    UserAssetOperationUpdateDTOIn,
    UserAssetOperationsFilter,
    NettoPositionData,
    UserAssetOperationWithNotesOut,
    NoteFilter, UserAssetOperationSearchByNoteInputArgs,
)
from logic.exceptions import (
    UserAssetNotFoundError,
    UserAssetAddressNotFoundError,
    UserAssetOperationNotFoundError,
    NotEnoughBalanceToSell,
)
from logic.usecases.user_asset_operation import (
    UserAssetOperationInsertUseCase,
    UserAssetOperationUpdateUseCase,
    UserAssetOperationDeleteUseCase,
    UserAssetOperationNettoPositionUseCase,
    UserAssetOperationsByNotesUseCase,
)
from user.domain import User


class UserAssetAddressOperationController(Controller):
    path = 'user_asset_operations'
    tags = ('user_asset_operations', )
    exception_handlers = {
        UserAssetNotFoundError: base_error_handler_factory(
        'User asset does not not exists',
        'User asset with this user_asset_id does not exists for this user',
        'user_asset_not_exists.html',
        ),
        UserAssetAddressNotFoundError: base_error_handler_factory(
            'Public key does not exists',
            'Public key can not be updated as it does not exists. You need to create it first',
            'user_asset_address_not_exists.html',
        ),
        UserAssetOperationNotFoundError: base_error_handler_factory(
            'User asset operation does not exists',
            'Operation with this id does not exists',
            'user_asset_operation_not_exists.html',
        ),
        NotEnoughBalanceToSell: base_error_handler_factory(
            'Balance is to small',
            'You do not have enough balance to sell operation',
            'not_enough_balance.html',
        )
    }
    @post(
        '/',
        dto=UserAssetOperationDTOIn,
        return_dto=UserAssetOperationDTOOut,
    )
    async def create(self, data: DTOData[UserAssetOperationData], kc_user: User) -> UserAssetOperationData:
        user_asset_operation_data = data.create_instance(user_id=kc_user.sub, id=None)
        return await UserAssetOperationInsertUseCase().execute(user_asset_operation_data)

    @put(
        '/',
        dto=UserAssetOperationUpdateDTOIn,
        return_dto=UserAssetOperationDTOOut,
    )
    async def update(self, data: DTOData[UserAssetOperationData], kc_user: User) -> UserAssetOperationData:
        user_asset_operation_data = data.create_instance(user_id=kc_user.sub)
        return await UserAssetOperationUpdateUseCase().execute(user_asset_operation_data)

    @delete('/{_id:int}',)
    async def delete(self, _id: FromPath[int], kc_user: User) -> None:
        return await UserAssetOperationDeleteUseCase().execute(_id, kc_user.sub)

    @get('/netto-position/{user_asset_id:int}', dependencies={'op_filter': Provide(operations_filter)})
    async def netto_position(
            self,
            user_asset_id: FromPath[int],
            kc_user: User,
            op_filter: UserAssetOperationsFilter,
    ) -> NettoPositionData:
        return await UserAssetOperationNettoPositionUseCase().execute(user_asset_id, kc_user.sub, op_filter)

    # todo POST notes create
    # todo пагинация
    # todo More like this new endpoint?
    @get(
        'notes',
        dependencies={'op_filter': Provide(operations_filter), 'note_filter': Provide(note_filter)},
    )
    async def notes(
            self,
            kc_user: User,
            op_filter: UserAssetOperationsFilter,
            note_filter: NoteFilter,
            notes: FromQuery[list[str]],
            search_method: FromQuery[SearchMethod] = SearchMethod.MATCH,
            distance: Annotated[int, QueryParameter(ge=0, le=2)] = 0
    ) -> list[UserAssetOperationWithNotesOut]:
        search_args = UserAssetOperationSearchByNoteInputArgs(
            user_id=kc_user.id,
            notes=notes,
            op_filter=op_filter,
            note_filter=note_filter,
            distance=distance,
            search_method=search_method,
        )
        return await UserAssetOperationsByNotesUseCase.execute(search_args)
