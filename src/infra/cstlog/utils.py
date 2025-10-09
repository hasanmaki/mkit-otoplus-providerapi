"""setup loguru logging."""

import inspect
import json
import logging
from collections import defaultdict

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class MetricsCollector:
    r"""Logger sink to collect METRIC level logs into a structured format.

    Example:
        start = perf_counter()
        # ...do something...
        exec_time = perf_counter() - start
        logger.bind(metric_name="custom_block", value=exec_time).log("METRIC", "Custom block timing")
    """

    def __init__(self) -> None:
        self.metrics = defaultdict(list)

    def __call__(self, message) -> None:
        record = message.record
        if record["level"].name != "METRIC":
            return
        extra = record["extra"]
        if "metric_name" in extra and "value" in extra:
            self.metrics[extra["metric_name"]].append({
                "value": extra["value"],
                "timestamp": record["time"].timestamp(),
            })

    def save_metrics(self, path: str = "metrics.json") -> None:
        with open(path, "w") as f:
            json.dump(dict(self.metrics), f, indent=2)
