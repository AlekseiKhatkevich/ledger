from temporalio.client import Client
from temporalio.contrib.opentelemetry import OpenTelemetryInterceptor
from temporalio.contrib.pydantic import pydantic_data_converter

from config import settings

_otel_interceptor = OpenTelemetryInterceptor()

async def get_client() -> Client:
    return await Client.connect(
        settings.TEMPORAL_ADDRESS,
        data_converter=pydantic_data_converter,
        interceptors=[_otel_interceptor],
    )
