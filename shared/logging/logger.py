import logging
import structlog


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)

logger = structlog.get_logger()