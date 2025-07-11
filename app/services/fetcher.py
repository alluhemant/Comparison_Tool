import httpx
from app.config import settings


async def fetch_data(url: str) -> str:
    timeout = httpx.Timeout(10.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            print(f"HTTP status error while fetching {url}: {e}")
            raise ValueError(f"Failed to fetch {url}: {str(e)}")
        except httpx.RequestError as e:
            print(f"Request error while fetching {url}: {e}")
            raise ValueError(f"Connection error for {url}: {str(e)}")
