from beanie import Document

# pydantic used for make datamodel come with data validation
from pydantic import BaseModel , Field

class Temple(Document):
    name: str = Field(...)
    description: str = Field(...)
    imageLinks: List()


    class Collection:
        name = 'temple'

    class Config:
        schema_extra = {
            "example": {
                "name": "วัดพลู",
                "description": "วัดนี้สวยมากแม่ก"
            }
        }

# this class used to defined how each route return templeData
class TempleData(BaseModel):
    name: str
    description: str
    class Config:
        schema_extra = {
            "example": {
                "name": "วัดพลู",
                "description": "วัดนี้สวยมากแม่ก"
            }
        }
