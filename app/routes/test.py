import asyncio
import json
from typing import List

import motor.motor_asyncio
from bson import ObjectId
from fastapi import APIRouter, Query
from pydantic import BaseModel
from pymongo import MongoClient

from app.configs.config import Settings
from app.libs.fetch import fetch
from app.libs.templeScraper import TempleScraperService
from app.models.province import CreateProvinceDTO, Province
from app.models.temple import Temple
from app.services.province import add_province
from app.services.temple import replace_temple_images_by_name

router = APIRouter()

templeScraper = TempleScraperService()


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


@router.get('/', response_description="test ping images_service")
async def test_ping_images_service() -> dict:
    # result = []
    # for i in range(20):
    #     for j in range(20):
    #         await asyncio.sleep(1)
    #         image_response = await fetch(f'{Settings().GOOGLE_IMAGE_SCRAPER_URL}/image?keyword=วัดพระแก้ว')
    #         image_json = image_response.json()
    #         result.append(image_json)
    # return result
    provinces_json = await templeScraper.all()

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


# @router.get('/test_google', response_description="test ping images_service")
# async def test_ping_images_service() -> dict:
#     image_response = await fetch(f'{Settings().GOOGLE_IMAGE_SCRAPER_URL}/image?keyword=วัดพระธาตุ')
#     return image_response.json()

class TestModel(BaseModel):
    name: str
    temples: List["Temple"]
    # province_name: str


PAGE_AMOUNT = 10


@router.get('/aggregation', response_description="aggregation")
async def test_aggregation(page: int, search: str, filter: str) -> List[Province]:
    client = motor.motor_asyncio.AsyncIOMotorClient(Settings().DATABASE_URL)

    database = client.toc
    collection = database.get_collection("province")

    pipeline = [
        {
            "$match": {
                "name": {
                    "$in": list(filter.split(',')) or []
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
                'temple_name': '$temple_info.name',
                'province_name': '$name',
                'detail': '$temple_info.detail',
                'images': '$temple_info.images',
                'images_count': {
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
            '$sort': {
                'province_name': 1,
                'images_count': -1,
                'detail': 1
            }
        }, {
            '$match': {
                'temple_name': {
                    '$regex': search,
                    '$options': 'i'
                }
            }
        }, {
            "$skip": PAGE_AMOUNT * (page-1)
        }, {
            "$limit": PAGE_AMOUNT
        }
    ]

    result = [a async for a in collection.aggregate(pipeline)]
    return result
