from app.models.temple import Temple
from app.models.province import Province

temple_collection = Temple


def temple_formatter(temple) -> dict:
    return {
        "name": str(temple["name"]),
        "detail": str(temple["detail"])
    }


async def add_temple(temple: dict) -> dict:
    new_temple = await temple_collection.create(temple)
    return new_temple


async def update_temple(temple: dict) -> dict:

    existed_temple = await temple_collection.find_one(temple_collection.name == temple.name)
    if not existed_temple:
        return None

    await existed_temple.set({Temple.name: temple.name,
                              Temple.detail: temple.detail, Temple.link: temple.link})
    return existed_temple


async def get_all_temples():
    temple = await temple_collection.all().to_list()
    return temple
