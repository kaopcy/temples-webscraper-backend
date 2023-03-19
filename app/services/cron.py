import logging
from fastapi_utils.tasks import repeat_every

from app.libs.templeScraper import TempleScraperService
from app.models.province import CreateProvinceDTO, Province
from app.models.temple import Temple
from app.services.province import add_province

templeScraper = TempleScraperService()

logger = logging.getLogger(__name__)

@repeat_every(seconds=60 * 60)
async def scraping_temples():
    provinces_json = await templeScraper.all()
    
    
    for province in provinces_json:
        province =  await add_province(CreateProvinceDTO(**province))
        for temple_object in province.temples:
            temple = await temple_object.fetch()
            logger.info(f'{temple.name}')      
            print(temple.name)
            
