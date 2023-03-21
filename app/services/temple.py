from typing import List

from app.models.temple import Temple, Images
from app.models.province import Province


def temple_formatter(temple) -> dict:
    return {
        "name": str(temple["name"]),
        "detail": str(temple["detail"])
    }


async def add_temple(temple: dict) -> dict:
    new_temple = await Temple.create(temple)
    return new_temple


async def update_temple(temple: dict) -> dict:

    existed_temple = await Temple.find_one(Temple.name == temple.name)
    if not existed_temple:
        return None

    await existed_temple.set({Temple.name: temple.name,
                              Temple.detail: temple.detail, Temple.link: temple.link})
    return existed_temple


async def get_all_temples():
    return await Temple.all().to_list()


async def get_temple_by_name(temple_name: str) -> Temple:
    return await Temple.find_one(Temple.name == temple_name)


async def replace_temple_images_by_name(temple_name: str, images: List[Images]) -> Temple:
    temple = await Temple.find_one(Temple.name == temple_name)
    temple.images = images
    await temple.save()
    return temple
