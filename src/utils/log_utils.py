"""Loguru logging utilities and performance metric decorators.

Features:
- Intercept standard logging to loguru
- METRIC log level for structured performance metrics
- Decorators for entry/exit logging and timing
- MetricsCollector sink for collecting metrics
"""

# TODO: Later when finishing the development, migrate to loguru-config for file-based config.
import functools
import inspect
import json
import logging
import os
import sys
import threading
import time
import tracemalloc
from collections import defaultdict
from collections.abc import Callable
from functools import wraps
from time import perf_counter

import psutil
from loguru import logger


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


class InterceptHandler(logging.Handler):
    """Add default handler to intercept standard logging and redirect to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
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


def add_thread_info(record):
    # Add thread info (name and id) to every log message as a single field
    thread_name = threading.current_thread().name
    thread_id = threading.get_ident()
    record["extra"]["thread_info"] = f"{thread_name}-{thread_id}"
    return True


def add_environment_info(record):
    # Add environment to production logs
    record["extra"]["env"] = "dev"
    return True


def response_filter(record):
    return record["extra"].get("response_log", False)


def setup_logging() -> None:
    """Setup function to initialize loguru logging and METRIC collector with environment-based sinks."""
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logger.remove()
    metril_level_no = 38
    logger.level("METRIC", no=metril_level_no)
    metrics_collector = MetricsCollector()
    logger.add(metrics_collector)

    env = os.getenv("ENV", "development").lower()
    if env == "production":
        # Only log to files in production
        logger.add(".logs/app.log", serialize=True, level="INFO")
        logger.add(".logs/errors.log", level="ERROR")
    else:
        # Log everything to stdout in development
        def dev_filter(record):
            return add_thread_info(record) and add_environment_info(record)

        logger.add(
            sink=sys.stdout,
            level="DEBUG",
            filter=dev_filter,
            format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> | {extra[env]} | {extra[thread_info]}",
            colorize=True,
            backtrace=True,
            diagnose=True,
            enqueue=True,
            serialize=False,
            catch=True,
        )
    logger.add(
        sink=".logs/response.log",
        filter=response_filter,
        level="INFO",
        serialize=True,
        compression="zip",
        retention="10 days",
        rotation="1 week",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message} | {extra} | {function}",
    )


# decorators Group===========================================> add more functionality under this sections


def logger_wraps(
    *, entry: bool = True, exit: bool = True, level: str = "DEBUG"
) -> Callable:
    """Decorator to log entry and exit of a function.

    Parameters
    ----------
    entry : bool, optional
        Whether to log function entry (default: True).
    exit : bool, optional
        Whether to log function exit (default: True).
    level : str, optional
        Logging level to use (default: "DEBUG").

    Returns:
    -------
    Callable
        A decorator that wraps the target function with logging.
    """

    def wrapper(func: Callable) -> Callable:
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, f"Entering '{name}' (args={args}, kwargs={kwargs})")
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, f"Exiting '{name}' (result={result})")
            return result

        return wrapped

    return wrapper


def timeit(func: Callable) -> Callable:
    """Decorator to measure and log the execution time of a function.

    Usage:
    -------
    @timeit
    def my_function():
        ...
    # Will log DEBUG with execution time.
    Also logs module, class (if any), and line number.
    """

    @functools.wraps(func)
    def sync_wrapped(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        exec_time = end - start
        module = func.__module__
        line_no = func.__code__.co_firstlineno
        qualname = func.__qualname__
        logger.debug(
            f"Function '{func.__name__}' executed in {exec_time:.6f} s "
            f"(module={module}, qualname={qualname}, line={line_no})"
        )
        return result

    @functools.wraps(func)
    async def async_wrapped(*args, **kwargs):
        start = perf_counter()
        result = await func(*args, **kwargs)
        end = perf_counter()
        exec_time = end - start
        module = func.__module__
        line_no = func.__code__.co_firstlineno
        qualname = func.__qualname__
        logger.debug(
            f"Function '{func.__name__}' executed in {exec_time:.6f} s "
            f"(module={module}, qualname={qualname}, line={line_no})"
        )
        return result

    if inspect.iscoroutinefunction(func):
        return async_wrapped
    else:
        return sync_wrapped


def metric(metric_name: str) -> Callable:
    r"""Decorator to log execution time as METRIC log level for performance monitoring.

    Usage:
    -------
    from src.log_utils import metric

    @metric("db_query_time")
    def query_db():
        ...

    # Will log METRIC with metric_name="db_query_time" and value=execution_time

    You can collect all metrics using metrics_collector.save_metrics()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = perf_counter()
            result = func(*args, **kwargs)
            exec_time = perf_counter() - start
            logger.bind(metric_name=metric_name, value=exec_time).log(
                "METRIC", f"{metric_name} executed in {exec_time:.4f}s"
            )
            return result

        return wrapper

    return decorator


def mini_benchmark(func):
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())

        # start
        tracemalloc.start()
        start_time = time.perf_counter()
        rss_before = process.memory_info().rss

        result = func(*args, **kwargs)

        # end
        rss_after = process.memory_info().rss
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        logger.debug(
            f"{func.__name__} | "
            f"time={end_time - start_time:.6f}s | "
            f"rss_diff={(rss_after - rss_before) / 1024:.2f} KB | "
            f"rss_now={rss_after / 1024:.2f} KB | "
            f"tracemalloc_current={current / 1024:.2f} KB | "
            f"tracemalloc_peak={peak / 1024:.2f} KB"
        )
        return result

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())

        # start
        tracemalloc.start()
        start_time = time.perf_counter()
        rss_before = process.memory_info().rss

        result = await func(*args, **kwargs)

        # end
        rss_after = process.memory_info().rss
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        logger.debug(
            f"{func.__name__} | "
            f"time={end_time - start_time:.6f}s | "
            f"rss_diff={(rss_after - rss_before) / 1024:.2f} KB | "
            f"rss_now={rss_after / 1024:.2f} KB | "
            f"tracemalloc_current={current / 1024:.2f} KB | "
            f"tracemalloc_peak={peak / 1024:.2f} KB"
        )
        return result

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
