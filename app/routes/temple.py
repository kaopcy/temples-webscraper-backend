from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from app.services.temple import (
    add_temple,
    get_all_temples,
    update_temple,
    get_temple_by_name,
    get_temple_by_query
)

from app.models.temple import (
    Temple
)

router = APIRouter()


@router.post('/', response_description="temple added")
async def add_temple_route(temple: Temple = Body(...)):
    new_temple = await add_temple(temple)
    return new_temple

@router.get('/{temple_name}' , response_description="get temple by name")
async def get_temple_by_name_route(temple_name: str) -> Temple :
    return await get_temple_by_name(temple_name.lower())


@router.put('/', response_description="temple added")
async def add_temple_route(temple: Temple = Body(...)):
    updated_temple = await update_temple(temple)
    return updated_temple


@router.get('/', response_description="get temple")
async def get_all_temples_route() -> Temple:
    temples = await get_all_temples()
    return temples

@router.get('/search/{query}', response_description="search temple")
async def get_temple_by_query_route(query: str) -> Temple:
    temples = await get_temple_by_query(query)
    return temples
