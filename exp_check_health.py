"""check connection to specific upstream"""

import asyncio

import httpx


async def check_health(url: str, timeout: float = 1.0) -> bool:
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            print(f"[OK] {url} -> {response.status_code}")
            return True
        except httpx.RequestError as exc:
            print(f"[ERROR] Connection failed: {exc}")
        except httpx.HTTPStatusError as exc:
            print(f"[ERROR] HTTP {exc.response.status_code} from {url}")
        return False


async def main():
    url = "http://10.0.0.3:10003/command"
    ok = await check_health(url)
    if not ok:
        print("Upstream not reachable")


if __name__ == "__main__":
    asyncio.run(main())
