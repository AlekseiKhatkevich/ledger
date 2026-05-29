from functools import cache

from temporalio.client import Client
from temporalio.contrib.opentelemetry import OpenTelemetryInterceptor
from temporalio.contrib.pydantic import pydantic_data_converter

from config import settings


@cache
async def get_client() -> Client:
    otel_interceptor = OpenTelemetryInterceptor()
    return await Client.connect(
        settings.TEMPORAL_ADDRESS,
        data_converter=pydantic_data_converter,
        interceptors=[otel_interceptor],
    )
