from beanie import WriteRules
from beanie.operators import (Set, In)
from typing import List

import csv
import os

from app.models.province import Province, CreateProvinceDTO, ProvinceNameDTO
from app.models.temple import Temple

from app.libs.translator import province_to_thai


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


async def get_csv_from_provinces(provinces: List[str]) -> Province:
    provinces.sort()

    provinces = await Province.find(In(Province.name, provinces), projection_model=ProvinceNameDTO, fetch_links=True).to_list()
    csv_list = [['จังหวัด', 'วัด']]
    for province in provinces:
        province_name = province_to_thai(province.name)
        for temple in province.temples:
            csv_list.append([province_name, temple])

    return '\uFEFF' + "\n".join([",".join(row) for row in csv_list])
