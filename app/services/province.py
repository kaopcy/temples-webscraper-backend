from beanie import WriteRules
from beanie.operators import Set
from typing import List

from app.models.province import Province, CreateProvinceDTO
from app.models.temple import Temple


async def add_province(provinceReq: CreateProvinceDTO) -> Province:
    province = await Province.find_one(Province.name == provinceReq.name, fetch_links=True)
    if not province:
        province = Province(name=provinceReq.name, temples=[])

    for new_temple in provinceReq.temples:
        await Temple.find_one(Temple.name == new_temple.name) \
            .upsert(Set({**new_temple.dict()}), on_insert=Temple(**new_temple.dict()))
        newTemple = await Temple.find_one(Temple.name == new_temple.name)

        if newTemple.id not in [t.id for t in province.temples]:
            province.temples.append(newTemple)

    await province.save()
    province = await Province.find_one(Province.name == provinceReq.name, fetch_links=True)
    return province


async def get_all_provinces() -> List[Province]:
    provinces = await Province.find(fetch_links=True).to_list()

    return provinces


async def get_province_by_name(name: str) -> Province:
    province = await Province.find_one(Province.name == name, fetch_links=True)
    return province

