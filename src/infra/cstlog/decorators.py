"""Loguru logging utilities and performance metric decorators.

Features:
- Intercept standard logging to loguru
- METRIC log level for structured performance metrics
- Decorators for entry/exit logging and timing
- MetricsCollector sink for collecting metrics
"""

import functools
import inspect
import os
import time
import tracemalloc
from collections.abc import Callable
from functools import wraps
from time import perf_counter

import psutil
from loguru import logger


def logger_wraps(
    *, entry: bool = True, exit: bool = True, level: str = "DEBUG"
) -> Callable:
    """Decorator untuk mencatat entry dan exit fungsi (sync atau async).

    Parameters
    ----------
    entry : bool, optional
        Mencatat saat fungsi dimasuki (default: True).
    exit : bool, optional
        Mencatat saat fungsi selesai (default: True).
    level : str, optional
        Logging level yang digunakan (default: "DEBUG").
    """

    def wrapper(func: Callable) -> Callable:
        name = func.__name__
        logger_ = logger.opt(depth=1)

        def log_entry(*args, **kwargs):
            if entry:
                logger_.log(level, f"Entering '{name}' (args={args}, kwargs={kwargs})")

        def log_exit(result):
            if exit:
                logger_.log(level, f"Exiting '{name}' (result={result})")

        @functools.wraps(func)
        def sync_wrapped(*args, **kwargs):
            """Wrapper untuk fungsi sinkronus."""
            log_entry(*args, **kwargs)
            result = func(*args, **kwargs)
            log_exit(result)
            return result

        @functools.wraps(func)
        async def async_wrapped(*args, **kwargs):
            """Wrapper untuk fungsi asinkronus."""
            log_entry(*args, **kwargs)
            result = await func(*args, **kwargs)
            log_exit(result)
            return result

        # Logika switch berdasarkan tipe fungsi
        if inspect.iscoroutinefunction(func):
            return async_wrapped
        else:
            return sync_wrapped

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
