from enum import StrEnum
from typing import Any

from loguru import logger
from pydantic import ValidationError

from services.digipos.sch_digipos import DGResBalance
from utils.log_utils import logger_wraps, timeit


class ParsedStatusEnum(StrEnum):
    OK = "OK"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


# ======================================================================
# HELPERS
# ======================================================================
def dict_to_plaintext(d: dict) -> str:
    parts = []
    for k, v in d.items():
        v_str = f"{{{dict_to_plaintext(v)}}}" if isinstance(v, dict) else str(v)
        parts.append(f"{k}:{v_str}")
    return ",".join(parts)


def _base_output(
    meta: dict[str, Any],
    status_code: int,
    parsed: ParsedStatusEnum,
    data: Any,
    debug: bool = False,
) -> str:
    """Formatter standar output (encoded plaintext style)."""
    url = f"({meta.get('url', '-')})"
    path = meta.get("path", "-")

    if debug:
        # tampilkan meta lengkap, tapi buang noise
        safe_meta = {
            k: v
            for k, v in meta.items()
            if k
            not in {
                "request_headers",
                "response_headers",
                "response_history",
                "response_cookies",
                "body_type",
            }
        }
        meta_str = str(safe_meta) if safe_meta else "{}"
        return (
            f"meta={meta_str}"
            f"&url={url}"
            f"&path={path}"
            f"&status_code={status_code}"
            f"&parsed={parsed}"
            f"&data={data}"
        )

    # non-debug: data to plaintext
    data_str = f"{{{dict_to_plaintext(data)}}}" if isinstance(data, dict) else str(data)

    return f"url={url}&path={path}&status_code={status_code}&parsed={parsed}&data={data_str}"


# ======================================================================
# MAIN PARSER
# ======================================================================


@logger_wraps(level="DEBUG")
@timeit
def parse_balance_data(meta: dict[str, Any], body: Any, debug: bool = False) -> str:
    """Parser khusus endpoint balance — handle DICT, error, dll."""
    status_code = meta.get("status_code", 0)
    body_type = meta.get("body_type")

    # --- LOGGING DASAR ---
    if debug:
        logger.debug(f"[BalanceParser] meta={meta}")
        logger.debug(f"[BalanceParser] body_type={body_type}")

    # preview isi body maksimal 100 char biar gak flood log
    raw_preview = str(body)[:100].replace("\n", " ")
    logger.debug(f"[BalanceParser] raw body preview: {raw_preview}")

    # --- CASE: body bukan dict ---
    if body_type != "DICT":
        logger.warning(f"[BalanceParser] Skipped parsing — body_type={body_type}")
        return _base_output(meta, status_code, ParsedStatusEnum.SKIPPED, body, debug)

    # --- CASE: body dict — validasi pakai pydantic ---
    try:
        parsed = DGResBalance(**body).model_dump()
        logger.debug("[BalanceParser] Validation OK.")
        return _base_output(meta, status_code, ParsedStatusEnum.OK, parsed, debug)

    except ValidationError as exc:
        logger.error(f"[BalanceParser] Validation failed: {exc}")
        return _base_output(meta, status_code, ParsedStatusEnum.ERROR, body, debug)
