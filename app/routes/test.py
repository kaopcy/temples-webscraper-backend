from fastapi import APIRouter

from app.libs.fetch import fetch
from app.configs.config import Settings

router = APIRouter()

@router.get('/' , response_description="test ping images_service")
async def test_ping_images_service() -> dict:
    temple_name = "วัดสุขใจ"
    test_api  = await fetch(f'{Settings().GOOGLE_IMAGE_SCRAPER_URL}/image?keyword={temple_name}')
    return test_api.json()

