"""vibe coding is amazing.

==================

Utility decorator untuk benchmark fungsi sync maupun async.
Mengukur:
- Execution time (s)
- Memory usage (RSS diff, current RSS, tracemalloc)
- Skoring kualitas ("BAD" | "GOOD" | "EXCELLENT")

Fitur:
- Bisa dipakai di function biasa atau async function
- Adjustable log level (default: DEBUG)
- Bisa return hasil metrik sebagai dict untuk unit test
- Flexible: enable/disable time, memory, tracemalloc

Contoh pemakaian:
-----------------
from benchmark_utils import benchmark

@benchmark(level="INFO")
def heavy_task():
    return [i ** 2 for i in range(100000)]

@benchmark(return_result=True)
async def async_task():
    await asyncio.sleep(0.05)
    return "done"
"""

import inspect
import os
import tracemalloc
from functools import wraps
from time import perf_counter

import psutil
from loguru import logger

# cache process biar ga repeated call
_proc = None


def get_process():
    """Return process object untuk current PID."""
    global _proc
    pid = os.getpid()
    if _proc is None or _proc.pid != pid:
        _proc = psutil.Process(pid)
    return _proc


def score_time(exec_time: float) -> str:
    """Skoring berdasarkan waktu eksekusi."""
    if exec_time < 0.01:
        return "EXCELLENT"
    elif exec_time < 0.1:
        return "GOOD"
    return "BAD"


def score_memory(rss_diff_kb: float) -> str:
    """Skoring berdasarkan memory usage (KB)."""
    if rss_diff_kb < 100:  # <100KB = hemat
        return "EXCELLENT"
    elif rss_diff_kb < 1024:  # <1MB = oke
        return "GOOD"
    return "BAD"


def benchmark(
    track_time=True,
    track_mem=True,
    track_tracemalloc=True,
    proc=None,
    level="DEBUG",
    return_result=False,
):
    """Decorator untuk mengukur performa fungsi.

    Args:
        track_time (bool): aktifkan timing measurement. Default True.
        track_mem (bool): aktifkan RSS memory measurement. Default True.
        track_tracemalloc (bool): aktifkan python heap tracking. Default True.
        proc (psutil.Process): custom process object. Default current process.
        level (str): log level untuk loguru. Default "DEBUG".
        return_result (bool): kalau True, return dict hasil benchmark.
                              kalau False, return hasil fungsi asli.

    Returns:
        function wrapper (sync atau async).
    """

    def decorator(func):
        @wraps(func)
        def sync_wrapped(*args, **kwargs):
            p = proc or get_process()
            if track_tracemalloc:
                tracemalloc.start()
            start_rss = p.memory_info().rss if track_mem else 0
            start_time = perf_counter() if track_time else 0

            result = func(*args, **kwargs)

            end_time = perf_counter() if track_time else 0
            end_rss = p.memory_info().rss if track_mem else 0
            current, peak = (
                tracemalloc.get_traced_memory() if track_tracemalloc else (0, 0)
            )
            if track_tracemalloc:
                tracemalloc.stop()

            exec_time = end_time - start_time
            rss_diff = (end_rss - start_rss) / 1024 if track_mem else 0

            score_t = score_time(exec_time) if track_time else "N/A"
            score_m = score_memory(rss_diff) if track_mem else "N/A"

            msg = (
                f"{func.__name__} | time={exec_time:.6f}s | "
                f"rss_diff={rss_diff:.2f} KB | "
                f"rss_now={p.memory_info().rss / 1024:.2f} KB | "
                f"tracemalloc_current={current / 1024:.2f} KB | "
                f"tracemalloc_peak={peak / 1024:.2f} KB | "
                f"score_time={score_t} | score_memory={score_m}"
            )
            logger.log(level.upper(), msg)

            if return_result:
                return {
                    "exec_time": exec_time,
                    "rss_diff_kb": rss_diff,
                    "rss_now_kb": p.memory_info().rss / 1024,
                    "tracemalloc_current_kb": current / 1024,
                    "tracemalloc_peak_kb": peak / 1024,
                    "score_time": score_t,
                    "score_memory": score_m,
                }
            return result

        @wraps(func)
        async def async_wrapped(*args, **kwargs):
            p = proc or get_process()
            if track_tracemalloc:
                tracemalloc.start()
            start_rss = p.memory_info().rss if track_mem else 0
            start_time = perf_counter() if track_time else 0

            result = await func(*args, **kwargs)

            end_time = perf_counter() if track_time else 0
            end_rss = p.memory_info().rss if track_mem else 0
            current, peak = (
                tracemalloc.get_traced_memory() if track_tracemalloc else (0, 0)
            )
            if track_tracemalloc:
                tracemalloc.stop()

            exec_time = end_time - start_time
            rss_diff = (end_rss - start_rss) / 1024 if track_mem else 0

            score_t = score_time(exec_time) if track_time else "N/A"
            score_m = score_memory(rss_diff) if track_mem else "N/A"

            msg = (
                f"{func.__name__} | time={exec_time:.6f}s | "
                f"rss_diff={rss_diff:.2f} KB | "
                f"rss_now={p.memory_info().rss / 1024:.2f} KB | "
                f"tracemalloc_current={current / 1024:.2f} KB | "
                f"tracemalloc_peak={peak / 1024:.2f} KB | "
                f"score_time={score_t} | score_memory={score_m}"
            )
            logger.log(level.upper(), msg)

            if return_result:
                return {
                    "exec_time": exec_time,
                    "rss_diff_kb": rss_diff,
                    "rss_now_kb": p.memory_info().rss / 1024,
                    "tracemalloc_current_kb": current / 1024,
                    "tracemalloc_peak_kb": peak / 1024,
                    "score_time": score_t,
                    "score_memory": score_m,
                }
            return result

        return async_wrapped if inspect.iscoroutinefunction(func) else sync_wrapped

    return decorator


# from benchmark_utils import benchmark
# import asyncio

# # fungsi sync
# @benchmark(level="INFO")
# def heavy_task():
#     return [i ** 2 for i in range(1000000)]

# # fungsi async
# @benchmark(return_result=True)
# async def async_task():
#     await asyncio.sleep(0.05)
#     return "done"

# if __name__ == "__main__":
#     heavy_task()
#     result = asyncio.run(async_task())
#     print(result)
# ini sample usage jika di fast api ========================================================
# import os, psutil

# # dibuat sekali untuk 1 process FastAPI
# PROC = psutil.Process(os.getpid())
#
# def get_process():
#     return PROC

# pastikan hanya 1 instance process untuk 1 server FastAPI
# from fastapi import FastAPI
# from benchmark_utils import benchmark

# app = FastAPI()

# @benchmark(level="INFO")
# def heavy_task():
#     return [i**2 for i in range(1000000)]

# @app.get("/benchmark")
# async def run_bench():
#     # fungsi biasa juga bisa dipanggil dari route
#     result = heavy_task()
#     return {"status": "ok", "result": result}

# global di module benchmark_utils aja.

# nanti setiap decorator @benchmark otomatis pakai PROC.
