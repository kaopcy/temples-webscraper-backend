import logging
from typing import List
from collections import namedtuple


from fastapi import APIRouter

from app.services.province import (
    add_province,
    get_all_provinces,
    get_province_by_name
)
from app.services.temple import (
    replace_temple_images_by_name
)

from app.configs.config import Settings

from app.models.temple import (Temple)
from app.models.province import (Province, CreateProvinceDTO)

from app.libs.templeScraper import TempleScraperService
from app.libs.asynchronous import async_caller
from app.libs.fetch import fetch

import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

templeScraper = TempleScraperService()


@router.post('/', response_description="get temple")
async def add_provinces_route(provinceReq: CreateProvinceDTO) -> Province:
    new_province = await add_province(provinceReq)
    return new_province


@router.get('/', response_description="get temple")
async def add_provinces_route() -> List[Province]:
    logger.info('get province route')
    provinces = await get_all_provinces()
    return provinces


@router.get('/test', response_description="test")
async def test():
    provinces_json = await templeScraper.all()

    for province in provinces_json:
        province = await add_province(CreateProvinceDTO(**province))
        await asyncio.sleep(100)
        for temple_object in province.temples:
            try:
                image_response = await fetch(f'{Settings().GOOGLE_IMAGE_SCRAPER_URL}/image?keyword={temple_object.name}')
                image_json = image_response.json()
                await replace_temple_images_by_name(temple_object.name, image_json)
            except Exception as err:
                print(err)


@router.get('/{province_name}', response_description="get ")
async def get_province_by_name_route(province_name: str) -> Province:
    province = await get_province_by_name(province_name)

    def sortfn(a: Temple):
        return len(a.detail) < 20
    province.temples.sort(key=sortfn)
    return province
