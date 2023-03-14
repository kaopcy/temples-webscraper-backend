from app.models.temple import Temple

temple_collection = Temple

def temple_formatter(temple) -> dict:
    return {
        "name": str(temple["name"]),
        "description": str(temple["description"])
    }

async def add_temple(temple: dict) -> dict:
    new_temple = await temple_collection.create(temple)
    return new_temple

async def get_all_temples():
    temple =  await temple_collection.all().to_list()
    return temple
