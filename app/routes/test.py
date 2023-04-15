import asyncio

from fastapi import APIRouter, status

from app.configs.config import Settings
# from app.libs.templeScraper import TempleScraperService
from app.libs._templeScraper import TempleScraperService
from app.libs.fetch import fetch
from app.libs.parser import json_parser
from app.models.province import CreateProvinceDTO, Province
from app.models.temple import Temple
from app.services.province import add_province
from app.services.temple import replace_temple_images_by_name

router = APIRouter()

templeScraper = TempleScraperService()

@router.get('/scrape_temple_with_image', response_description="scrape all temple and also scrape image")
async def scrape_temple_with_image() -> dict:
    provinces_json = await templeScraper.get_all()

    result = []
    for province in provinces_json:
        province = await add_province(CreateProvinceDTO(**province))
        for temple_object in province.temples:
            await asyncio.sleep(1)
            try:
                image_response = await fetch(f'{Settings().GOOGLE_IMAGE_SCRAPER_URL}/image?keyword={temple_object.name}')
                image_json = image_response.json()
                result.append(image_json)
                if image_json['images'] and len(image_json['images']) >= 3:
                    await replace_temple_images_by_name(temple_object.name, image_json['images'])
            except Exception as err:
                print(err)
    return provinces_json

@router.get('/get_unusable_image/{temple_name}')
async def get_unusable_image_by_temple(temple_name: str):
    temple = await Temple.find_one(Temple.name == temple_name)
    if not temple:
        return None

    unusable = []
    usable = []

    unusable_url = []

    async def worker(image_url, index):
        try:
            res = await fetch(image_url)
            res_status = res.status_code
            not_image = "image" not in res.headers.get('content-type')

            if res_status == status.HTTP_404_NOT_FOUND or not_image:
                raise ConnectionAbortedError

            usable.append({
                "url": image_url,
                "status": res_status,
                "index": index
            })
        except Exception as err:
            unusable.append({
                "url": image_url,
                "index": index
            })
            unusable_url.append(image_url)

    await asyncio.gather(*[worker(image_url.url, index) for index, image_url in enumerate(temple.images)])

    new_temple_images = [
        image for image in temple.images if image.url not in unusable_url]

    temple.images = new_temple_images
    await temple.save()
    return unusable_url

@router.get('/remove_unused_image')
async def remove_unused_image():
    all_provinces = await Province.find(fetch_links=True).to_list()

    # for province in all_provinces:
    unusable_url= []
    for temple in all_provinces[2].temples:
        unusable_url.append({
            "name": temple.name,
            "urls": await get_unusable_image_by_temple(temple.name)
        })

    #  = await asyncio.gather(*[ for temple in all_provinces[2].temples])

    return unusable_url

@router.get('/fill_empty_image', response_description="find empty image and refill it")
async def fill_empty_image_route() -> dict:
    provinces_json = await get_empty_image_temples()

    result = []

    for province in provinces_json:
        for temple_object in province['temples']:
            await asyncio.sleep(1)
            try:
                image_response = await fetch(f'{Settings().GOOGLE_IMAGE_SCRAPER_URL}/image?keyword={temple_object.name}')
                image_json = image_response.json()
                result.append(image_json)
                if image_json['images'] and len(image_json['images']) >= 3:
                    await replace_temple_images_by_name(temple_object.name, image_json['images'])
            except Exception as err:
                print(err)

    return provinces_json


@router.get('/get_empty_image_temples')
async def get_empty_image_temples():
    all_provinces = await Province.find(fetch_links=True).to_list()
    non_exist = []
    for index, province in enumerate(all_provinces):
        non_exist.append({
            "name": province.name,
            "temples": []
        })

        for temple in province.temples:
            if(not temple.images or len(temple.images) <= 15):
                non_exist[index]['temples'].append(temple)
    return non_exist
