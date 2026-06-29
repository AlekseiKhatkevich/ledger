from functools import cache, cached_property

import async_hvac
from pydantic import HttpUrl, SecretStr


@cache
class OpenBaoClient:
    def __init__(
            self,
            url: HttpUrl,
            token: SecretStr,
            unseal_keys: tuple[SecretStr, ...],
    ) -> None:
        self.url = url
        self.token = token
        self.unseal_keys = unseal_keys


    @cached_property
    def client(self) -> async_hvac.AsyncClient:
        return async_hvac.AsyncClient(url=self.url, token=self.token.get_secret_value())


    async def unseal(self) -> None:
        if await self.client.is_sealed():
            await self.client.unseal_multi(
                [key.get_secret_value() for key in self.unseal_keys]
            )