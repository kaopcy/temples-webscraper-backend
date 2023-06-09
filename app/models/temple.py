from beanie import Document, Indexed, PydanticObjectId
from typing import List, Optional


from pydantic import BaseModel, Field


class Images(BaseModel):
    url: str = Field(...)
    src: str = Field(...)


class Temple(Document):
    name: str = Field(...)
    link: str = Field(...)
    detail: str = Field(...)
    images: Optional[List["Images"]]

    class Collection:
        name = 'temple'

    class Config:
        schema_extra = {
            "example": {
                "name": "วัดพลู",
                "detail": "วัดนี้สวยมากแม่ก",
                "images": [
                    {
                        "url": "www.image.com",
                        "src": "www.src.image.com"
                    },
                    {
                        "url": "www.image.com",
                        "src": "www.src.image.com"
                    }
                ]
            }
        }


class TempleName(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id")
    name: str = Field(...)


class CreateTempleDto(BaseModel):
    name: str = Field(...)
    link: str = Field(...)
    detail: str = Field(...)
    images: Optional[List["Images"]]


class TempleResponse(BaseModel):
    id: str = Field(None , alias="_id")
    temple_name: str = Field(...)
    province_name: str = Field(...)
    detail: str = Field(...)
    images: Optional[List[Images]]
    images_count: int
