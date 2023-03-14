from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from app.server.database import (
    add_temple,
    get_all_temples
)

from app.models.temple import (
    TempleData,
    Temple
)

router = APIRouter()

@router.post('/' , response_description="temple added")
async def add_temple_route(temple: Temple = Body(...)):
    new_temple = await add_temple(temple)
    return new_temple

@router.get('/' , response_description="get temple")
async def get_all_temples_route() -> Temple:
    temples = await get_all_temples()
    return temples
