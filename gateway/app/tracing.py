from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

import importlib

# Import Resource from whichever location is available (different opentelemetry versions)
_res_mod = None
for mod_name in ("opentelemetry.sdk.resources", "opentelemetry.resources"):
    try:
        _res_mod = importlib.import_module(mod_name)
        break
    except ImportError:
        _res_mod = None

if _res_mod is None:
    raise ImportError("cannot import Resource from opentelemetry resources modules")

Resource = getattr(_res_mod, "Resource")

from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


resource = Resource.create({
    "service.name": "streamops-gateway"
})


provider = TracerProvider(
    resource=resource
)


processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint="http://streamops-jaeger:4317",
        insecure=True
    )
)


provider.add_span_processor(processor)

trace.set_tracer_provider(provider)


tracer = trace.get_tracer(__name__)