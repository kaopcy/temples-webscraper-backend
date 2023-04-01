from functools import reduce
import asyncio

from fastapi import APIRouter

from app.libs.fetch import fetch
from app.models.temple import Temple

router = APIRouter()


@router.get('/')
async def remove_unloadable_image():
    result_temples = []

    all_temples = await Temple.find_all().to_list()

    async def temple_worker(temple_name):
        temple = await Temple.find_one(Temple.name == temple_name)
        fetchable = []
        unfetchable = []

        async def image_worker(image, index):
            try:
                res = await fetch(image.url)
                if(res.status_code is not 200):
                    raise ConnectionAbortedError()

                fetchable.append(image)
            except Exception as err:
                unfetchable.append({
                    "index": index,
                    "status": "unknown",
                    "image": image.url
                })

        await asyncio.gather(*[image_worker(image, index) for index, image in enumerate(temple.images)])
        # temple.images = fetchable
        # await temple.save()
        result_temples.append({
            "fetchable": fetchable,
            "unfetchable": unfetchable,
        })

    await asyncio.gather(*[temple_worker(temple.name) for temple in all_temples[0:20]])

    return result_temples
