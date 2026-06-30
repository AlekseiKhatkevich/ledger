from typing import Any, ChainMap

import msgspec


class OpenBaoSecretMetadata(msgspec.Struct, kw_only=True):
    """Metadata of a secret version in OpenBao KV v2."""

    created_time: str
    custom_metadata: dict[str, Any] | None = None
    deletion_time: str = ''
    destroyed: bool = False
    version: int


class OpenBaoSecretData(msgspec.Struct, kw_only=True):
    """Inner data payload of an OpenBao secret response."""

    data: dict[str, str]
    metadata: OpenBaoSecretMetadata


class OpenBaoSecretResponse(msgspec.Struct, kw_only=True):
    """Full OpenBao read secret response (KV v2)."""

    request_id: str
    lease_id: str = ''
    renewable: bool = False
    lease_duration: int = 0
    data: OpenBaoSecretData
    wrap_info: Any = None
    warnings: list[str] | None = None
    auth: Any = None


class OpenBaoSecretResponseBatch(msgspec.Struct):
    responses: list[OpenBaoSecretResponse]

    @property
    def response_dict(self) -> ChainMap[str, str]:
        return ChainMap(*(resp.data.data for resp in self.responses))
