import httpx

async def fetch(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True , timeout=20)
        return response