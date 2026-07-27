from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


resource = Resource.create(
    {
        "service.name": "streamops-integrity-service"
    }
)


provider = TracerProvider(
    resource=resource
)


processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint="http://jaeger:4317",
        insecure=True
    )
)


provider.add_span_processor(processor)

trace.set_tracer_provider(provider)


tracer = trace.get_tracer(__name__)