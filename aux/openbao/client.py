from functools import cache, wraps
from typing import Optional

import async_hvac
from pydantic import HttpUrl, SecretStr

from config import settings


def retry_on_auth_error(func):
    """Re-authenticate openbao client in case temporary token got outdated"""
    @wraps(func)
    async def wrapper(self: 'OpenBaoClient', *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except (async_hvac.exceptions.Forbidden, async_hvac.exceptions.Unauthorized):
            await self.authenticate()
            return await func(self, *args, **kwargs)

    return wrapper

@cache
class OpenBaoClient:
    def __init__(
            self,
            url: HttpUrl,
            unseal_keys: tuple[SecretStr, ...],
            root_token: Optional[SecretStr],
            approle_id: Optional[SecretStr],
            approle_secret_id: Optional[SecretStr],
    ) -> None:
        self.url = url
        self.unseal_keys = unseal_keys
        self.root_token = root_token
        self.approle_id = approle_id
        self.approle_secret_id = approle_secret_id
        self._client = None
        # async_hvac.exceptions.UnauthorizedError

    async def get_client(self) -> async_hvac.AsyncClient:
        if self._client is None:
            self._client = async_hvac.AsyncClient(url=self.url)
            await self.authenticate()
        return self._client

    async def authenticate(self) -> async_hvac.AsyncClient:
        await self._client.auth_approle(
            self.approle_id.get_secret_value(),
            self.approle_secret_id.get_secret_value(),
        )
        return self._client

    async def unseal(self) -> None:
        async with async_hvac.AsyncClient(
                url=self.url,
                token=self.root_token.get_secret_value()
        ) as root_client:
            if await root_client.is_sealed():
                await root_client.unseal_multi(
                    [key.get_secret_value() for key in self.unseal_keys]
                )

    @retry_on_auth_error
    async def do_something(self):
        pass


openbao_client: OpenBaoClient


def __getattr__(name: str) -> OpenBaoClient:
    """Lazy initialization of openbao_client singleton."""
    if name == 'openbao_client':
        return OpenBaoClient(
            url=settings.BAO_ACCESS_ADDR,
            unseal_keys=settings.BAO_UNSEAL_KEYS,
            root_token=settings.BAO_ROOT_KEY,
            approle_id=settings.BAO_APPROLE_ID,
            approle_secret_id=settings.BAO_APPROLE_SECRET_ID,
        )
    raise AttributeError(f'Module {__name__} has no attribute {name}')