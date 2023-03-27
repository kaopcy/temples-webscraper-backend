import asyncio
import logging

from fastapi_utils.tasks import repeat_every

from app.configs.config import Settings
from app.libs.fetch import fetch
from app.libs.templeScraper import TempleScraperService
from app.models.province import CreateProvinceDTO
from app.services.province import add_province
from app.services.temple import replace_temple_images_by_name

templeScraper = TempleScraperService()

logger = logging.getLogger(__name__)


@repeat_every(seconds=60 * 60 * 24)
async def scraping_temples():
    return None
    provinces_json = await templeScraper.all()
    logger.info("wikipedia finished")
    logger.info(provinces_json)
    for province in provinces_json:
        logger.info(f"scraping image: {province.name}")
        province = await add_province(CreateProvinceDTO(**province))
        for temple_object in province.temples:
            await asyncio.sleep(400)
            try:
                image_response = await fetch(f'{Settings().GOOGLE_IMAGE_SCRAPER_URL}/image?keyword={temple_object.name}')
                image_json = image_response.json()
                if image_json['images'] and len(image_json['images']) >= 3:
                    await replace_temple_images_by_name(temple_object.name, image_json['images'])
            except Exception as err:
                print(err)
