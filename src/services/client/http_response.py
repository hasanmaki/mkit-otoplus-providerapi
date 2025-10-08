# info: docstrings for http_response.py
"""Module: HttpResponseService.

Description:
This module provides a service for parsing HTTP responses from httpx,
extracting relevant information, and converting them into a standardized
ApiResponseIN format. It handles different content types (JSON, text, etc.)
and provides debugging options for detailed request/response information.
"""

from typing import Any

import httpx

from services.client.sch_response import ApiResponseIN, ResponseMessage
from utils.log_utils import logger_wraps, timeit


class HttpResponseService:
    """Primary parser: httpx.Response -> ApiResponseIN (flat, clean).

    This class is responsible for parsing an httpx.Response object and
    transforming it into a structured ApiResponseIN object. It handles
    different content types, error handling, and metadata extraction.
    """

    def __init__(self, resp: httpx.Response, debug: bool = False):
        """Initializes the HttpResponseService with an httpx.Response object and a debug flag.

        Args:
            resp (httpx.Response): The HTTP response to parse.
            debug (bool, optional):  If True, includes additional debug information in the output. Defaults to False.
        """
        self.resp = resp
        self.debug = debug
        self.last_error: str | None = None

    def _try_parse_json(self) -> tuple[str, Any]:
        """Inner Parser Helper: Parses the response body as JSON.

        Attempts to parse the response body as JSON. If successful, returns
        a dictionary representation. If parsing fails, returns an error message
        and the raw response text (up to the first 500 characters).

        Returns:
            tuple[str, Any]:
                - ResponseMessage.DICT (if successful) or ResponseMessage.ERROR (if parsing fails)
                - Parsed JSON data (as a dict) or an error dict containing the error and raw text.
        """
        try:
            body = self.resp.json()
        except Exception as e:
            self.last_error = f"Invalid JSON: {e}"
            return ResponseMessage.ERROR, {
                "error": self.last_error,
                "raw": self.resp.text[:500] if self.resp.text else None,
            }

        return ResponseMessage.DICT, body if isinstance(body, dict) else {"raw": body}

    def _try_parse_text(self) -> tuple[str, Any]:
        """Inner Parser Helper: Parses the response body as plain text.

        Attempts to parse the response body as plain text. If the body is empty,
        returns ResponseMessage.EMPTY. Otherwise, returns ResponseMessage.TEXT and
        the text content.

        Returns:
            tuple[str, Any]:
                - ResponseMessage.TEXT or ResponseMessage.EMPTY
                - A dict containing the raw text, or None if the text is empty.
        """
        text = (self.resp.text or "").strip()
        if not text:
            return ResponseMessage.EMPTY, {"raw": None}
        return ResponseMessage.TEXT, {"raw": text}

    @timeit
    def parse_body(self) -> tuple[str, Any]:
        """Fallback chain: JSON -> TEXT -> ERROR. Main parser function.

        This method attempts to parse the response body in the following order:
        1.  If the content type is "json", tries to parse it as JSON.
        2.  If the content type is "text", "html", or "xml", tries to parse it as text.
        3.  If both fail, it attempts JSON and text parsing again as a fallback.
        4.  If everything fails, returns an error message.

        Returns:
            tuple[str, Any]:
                - ResponseMessage: A string representing the type of the parsed response (DICT, TEXT, EMPTY, or ERROR).
                - Any: The parsed data (dict or string) or an error dict containing the error and raw text.
        """
        content_type = (self.resp.headers.get("content-type") or "").lower()
        try:
            if "json" in content_type:
                return self._try_parse_json()
            if any(x in content_type for x in ["text", "html", "xml"]):
                return self._try_parse_text()
        except Exception as e:
            self.last_error = f"Parsing failed ({content_type}): {e}"

        # fallback universal
        for parser in (self._try_parse_json, self._try_parse_text):
            response_type, data = parser()
            if response_type != ResponseMessage.ERROR:
                return response_type, data

        # gagal total
        return ResponseMessage.ERROR, {
            "error": self.last_error or "Unknown parsing error",
            "raw": self.resp.text[:500] if self.resp.text else None,
        }

    def _get_flat_meta(self, response_type: str) -> dict[str, Any]:
        """Meta helpers: Extracts metadata from the response.

        Extracts metadata from the HTTP response, such as status code,
        elapsed time, content type, and request/response headers (if debug is enabled).

        Args:
            response_type (str): The type of the response (e.g., ResponseMessage.DICT, ResponseMessage.ERROR).

        Returns:
            dict[str, Any]: A dictionary containing the extracted metadata.
        """
        resp = self.resp
        req = getattr(resp, "request", None)
        meta = {
            "status_code": resp.status_code,
            "elapsed_time_s": getattr(
                getattr(resp, "elapsed", None), "total_seconds", lambda: None
            )(),
            "content_type": resp.headers.get("content-type"),
        }
        if self.debug:
            meta.update({
                "request_headers": dict(getattr(req, "headers", {})) if req else {},
                "response_headers": dict(resp.headers),
                "url": str(resp.url),
                "path": getattr(resp.url, "path", None),
            })
        # optional info yang sebelumnya ada sebagai field
        meta.update({
            "response_type": response_type,
            "description": self.last_error
            if response_type == ResponseMessage.ERROR
            else "ok",
        })
        return meta

    @logger_wraps(level="DEBUG")
    @timeit
    def to_dict(self) -> ApiResponseIN:
        """Public API: Converts the HTTP response to an ApiResponseIN object.

        This is the main public method that orchestrates the parsing process.
        It calls `parse_body` to parse the response body, extracts metadata using
        `_get_flat_meta`, and constructs an ApiResponseIN object with the parsed data.

        Returns:
            ApiResponseIN: A structured representation of the HTTP response.
        """
        response_type, parsed_data = self.parse_body()
        meta = self._get_flat_meta(response_type)

        return ApiResponseIN(
            status_code=self.resp.status_code,
            url=str(self.resp.url.host),
            debug=self.debug,
            meta=meta,
            raw_data=parsed_data,
        )


class ResponseParserFactory:
    """Factory to enable injection via FastAPI dependency system.

    This class is a factory that creates instances of the HttpResponseService.
    It is designed to be used with FastAPI's dependency injection system,
    allowing you to easily inject a response parser into your API endpoints.
    """

    def __init__(self, parser_cls: type[HttpResponseService] = HttpResponseService):
        """Initializes the ResponseParserFactory with a parser class.

        Args:
            parser_cls (type[HttpResponseService], optional): The class to use for parsing HTTP responses. Defaults to HttpResponseService.
        """
        self.parser_cls = parser_cls

    def __call__(self, resp: httpx.Response, debug: bool = False) -> ApiResponseIN:
        """Creates and returns an ApiResponseIN object using the configured parser class.

        Args:
            resp (httpx.Response): The HTTP response to parse.
            debug (bool, optional): If True, includes additional debug information in the output. Defaults to False.

        Returns:
            ApiResponseIN: A structured representation of the HTTP response.
        """
        return self.parser_cls(resp, debug).to_dict()


def response_to_dict(
    resp: httpx.Response, debugresponse: bool = False
) -> dict[str, Any]:
    """Wrapper simple (non-DI usecase): Converts an HTTP response to a dictionary.

    A simple wrapper function that creates an HttpResponseService instance,
    converts the response to an ApiResponseIN object, and then converts the
    ApiResponseIN object to a dictionary. This is useful when you don't need
    to use the dependency injection capabilities of the ResponseParserFactory.

    Args:
        resp (httpx.Response): The HTTP response to parse.
        debugresponse (bool, optional): If True, includes additional debug information in the output. Defaults to False.

    Returns:
        dict[str, Any]: A dictionary representation of the HTTP response.
    """
    return HttpResponseService(resp, debugresponse).to_dict().model_dump()
