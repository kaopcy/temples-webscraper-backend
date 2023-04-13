from typing import List

from pydantic import BaseModel, Field

from beanie import Document, Link
from app.models.temple import Temple, CreateTempleDto


class Province(Document):
    name: str = Field(...)
    temples: List[Link[Temple]]

    class Collection:
        name = 'province'


class CreateProvinceDTO(BaseModel):
    name: str = Field(...)
    temples: List[CreateTempleDto]

class ProvinceNameDTO(BaseModel):
    name: str
    temples: List[str]

    class Settings:
        projection = {"name": 1, "temples": "$temples.name"}

