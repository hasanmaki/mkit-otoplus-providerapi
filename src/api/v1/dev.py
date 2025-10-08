from typing import Any
from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/test", tags=["test"])


router = APIRouter(prefix="/test", tags=["test"])


@router.get("/test_response")
async def test_response(**kwargs: Any | None):  # Accept kwargs
    async with httpx.AsyncClient() as client:
        params: dict[str, Any] = {
            "username": "WIR6289504",
            **kwargs,
        }
        host = "http://10.0.0.3:10003/"
        endpoints = "/balance"
        ful_url = urljoin(host, endpoints)
        try:
            response = await client.get(url=ful_url, timeout=5, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"An error occurred while requesting {exc.request.url!r}: {exc.response.text}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while requesting {exc.request.url!r}.",
            ) from exc
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"General Exception - {e}"
            ) from e
        else:
            return response.json()
