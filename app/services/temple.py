from typing import List

import motor.motor_asyncio
from beanie.operators import Text
from bson.json_util import dumps

from app.configs.config import Settings
from app.models.province import Province
from app.models.temple import Images, Temple, TempleName, TempleResponse

from app.libs.parser import json_parser


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

    client = motor.motor_asyncio.AsyncIOMotorClient(Settings().DATABASE_URL)

    database = client.toc
    collection = database.get_collection("province")

    pipeline = [
        {
            '$lookup': {
                'from': 'temple',
                'localField': 'temples.$id',
                'foreignField': '_id',
                'as': 'temple_info'
            }
        }, {
            '$unwind': {
                'path': '$temple_info'
            }
        }, {
            '$project': {
                'name': '$temple_info.name',
                'detail': '$temple_info.detail',
                '_id': '$temple_info._id',
                'images': '$temple_info.images',
                'link': '$temple_info.link',
                'provinceName': '$name'
            }
        }, {
            '$match': {
                'name': {
                    '$regex': temple_name,
                    '$options': 'i'
                }
            }
        }
    ]

    result = [a async for a in collection.aggregate(pipeline)]
    print(result)

    return json_parser([] if len(result) <= 0 else result[0])


async def get_temple_by_query(query: str) -> List[str]:
    return [temple for temple in await Temple.find_all(projection_model=TempleName).to_list() if query in temple.name]


async def replace_temple_images_by_name(temple_name: str, images: List[Images]) -> Temple:
    temple = await Temple.find_one(Temple.name == temple_name)
    temple.images = images
    await temple.save()
    return temple

PAGE_AMOUNT = 10


async def get_temple_by_filter_sort_search(page: int, search: str, filter: str):
    # use motor instead because beanie can't perform normal aggregation
    client = motor.motor_asyncio.AsyncIOMotorClient(Settings().DATABASE_URL)

    database = client.toc
    collection = database.get_collection("province")

    pipeline = [
        {
            "$match": {
                "name": {
                    "$in": filter
                }
            }
        },
        {
            '$lookup': {
                'from': 'temple',
                'localField': 'temples.$id',
                'foreignField': '_id',
                'as': 'temple_info'
            }
        }, {
            '$unwind': {
                'path': '$temple_info'
            }
        }, {
            '$project': {
                "_id": "$temple_info._id",
                'name': '$temple_info.name',
                'provinceName': '$name',
                'link': '$temple_info.link',
                'detail': "$temple_info.detail",
                'images': "$temple_info.images",
                # 'detail': {"$substrCP": ['$temple_info.detail', 0, 200]},
                'images': {"$slice": ['$temple_info.images', 4]},
                "wordCount": {"$strLenCP": "$temple_info.detail"},
                'imagesCount': {
                    '$cond': [
                        {
                            '$ifNull': [
                                '$temple_info.images', False
                            ]
                        }, {
                            '$size': '$temple_info.images'
                        }, 0
                    ]
                }
            }
        }, {
            '$match': {
                'name': {
                    '$regex': search,
                    '$options': 'i'
                }
            }
        }, {
            '$sort': {
                'wordCount': -1,
                'provinceName': 1,
                'imagesCount': -1,
            }
        }, {
            "$group": {
                "_id": None,
                "data": {
                    "$push": "$$ROOT",
                },
                "count": {
                    "$sum": 1,
                },
            }
        }, {
            "$project": {
                "_id": 0,
                "data": {
                    "$slice": ["$data", PAGE_AMOUNT * (page-1), 10]
                },
                "options": {
                    "totalTemples": "$count",
                    "totalPages": {
                        "$toInt": {
                            "$ceil": {
                                "$divide": ["$count", 10],
                            },
                        }
                    },
                    "nextPage": {
                        "$cond": [
                            {
                                "$lt": [page, {
                                    "$toInt": {
                                        "$ceil": {
                                            "$divide": ["$count", 10],
                                        },
                                    }
                                }],
                            },
                            page+1,
                            None,
                        ],
                    },
                },
            }
        }
    ]
    result = [a async for a in collection.aggregate(pipeline)]
    print(result)

    return json_parser([] if len(result) <= 0 else result[0])
