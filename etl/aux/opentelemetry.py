import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from temporalio.contrib.opentelemetry import TracingInterceptor

from config import settings


def setup_opentelemetry() -> TracingInterceptor:
    """
    Configure OpenTelemetry SDK with OTLP exporter, instrument
    httpx, SQLAlchemy, asyncpg and logging, and return a
    TracingInterceptor for Temporal client/worker.
    """
    # Create a Resource with the service name for identifying spans in Jaeger.
    resource = Resource.create(
        attributes={
            "service.name": settings.OTEL_SERVICE_NAME,
        },
    )

    # Create a TracerProvider with batch span processor sending to Jaeger via OTLP gRPC.
    tracer_provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Set the global tracer provider so instrumentations pick it up automatically.
    trace.set_tracer_provider(tracer_provider)

    # Instrument httpx client — captures all outgoing HTTP requests as spans.
    HTTPXClientInstrumentor().instrument()

    # Instrument asyncpg — captures driver-level database query details as spans.
    # AsyncPGInstrumentor().instrument()  to much noize

    # Instrument logging — automatically injects trace_id / span_id into log records.
    LoggingInstrumentor().instrument(set_logging_format=True)

    # Ensure the root logger level is set; the logging instrumentor does not change log levels.
    logging.getLogger().setLevel(logging.INFO)

    # Return Temporal's TracingInterceptor that creates spans for
    # Workflow and Activity invocations and propagates trace context.
    return TracingInterceptor()
