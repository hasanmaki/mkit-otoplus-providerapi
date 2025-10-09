import logging

from loguru_config import LoguruConfig

from src.infra.cstlog.utils import InterceptHandler

# def add_thread_info(record):
#     thread_name = threading.current_thread().name
#     thread_id = threading.get_ident()
#     record["extra"]["thread_info"] = f"{thread_name}-{thread_id}"
#     return True


# def add_environment_info(record):
#     record["extra"]["env"] = "dev"
#     return True


# def response_filter(record):
#     return record["extra"].get("response_log", False)


def setup_logging() -> None:
    """Setup logging configuration."""
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.INFO)
    log_config = LoguruConfig()
    log_config.load(config_or_file="logging.yaml")

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
