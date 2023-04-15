import asyncio
import re
from typing import List

import httpx
import requests


async def fetch(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True, timeout=20)
        return response

provinces = {
    "mahasarakam": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดมหาสารคาม",
    "mukdaharn": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดมุกดาหาร",
    "maehongson": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดแม่ฮ่องสอน",
    "yasothon": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดยโสธร",
}


def write(name, content):
    with open(name, 'w', newline='', encoding="utf-8") as csvfile:
        csvfile.write(content)


class TempleScraperService:
    def temple_link(self, html_str: str):
        pipeline_str = re.sub(' class=\"[a-zA-Z0-9-_ ]*\"', '', html_str)

        list_str = re.findall('<li><a href=\"[^ ]*\"', pipeline_str)

        if len(list_str) == 0:
            list_str.append('<li><a href=\"https://www.google.com\"')
        pipeline_str: str = list_str[0]

        pipeline_str = re.findall('\".*\"', pipeline_str)[0][1:-1]
        if '/wiki/' in pipeline_str:
            pipeline_str = 'https://th.wikipedia.org'+pipeline_str
        if '/w/' in pipeline_str:
            pipeline_str = 'https://www.google.com'
        return pipeline_str

    def temple_name(self, html_str: str):
        list_str = re.findall('วัด[\u0E00-\u0E60]*', html_str)
        return list_str[0] if len(list_str) != 0 else ""

    def sub_district_name(self, html_str: str):
        list_str = re.findall('ตำบล[\u0E00-\u0E60]*', html_str)
        return list_str[0] if len(list_str) != 0 else ""

    async def temple_detail(self, temple_link: str):
        if 'th.wikipedia.org' in temple_link:
            temple_html = await fetch(temple_link)
            pattern = re.compile(
                '<div class="mw-parser-output"[\u0000-\uFFFF]*</div>')
            if(re.search(pattern, temple_html.text)) and not re.search(r'อาจหมายถึง', temple_html.text):
                result = re.findall(pattern, temple_html.text)[0]

                pattern = re.compile('<p>[\u0000-\uFFFF]*</p>')
                result = ''.join(re.findall(pattern, result))

                result = re.sub('<meta [\u0000-\uFFFF]*?>', '', result)
                result = re.sub('<h2>[\u0000-\uFFFF]*', '', result)
                result = re.sub('<sup[\u0000-\uFFFF]*?</sup>', '', result)
                result = re.sub('href="[\u0000-\uFFFF]*?"', '', result)

                return result
        return '<p>no detail</p>'

    # async def temple_detail(self, temple_link: str):
    #     detail = '<p>no detail</p>'
    #     if 'th.wikipedia.org' in temple_link:
    #         temple_html = requests.get(temple_link)
    #         pattern = re.compile('<main[\u0000-\uFFFF]*<h2>')
    #         result = re.search(pattern, temple_html.text)
    #         if result:
    #             pattern = re.compile('<p>[\u0000-\uFFFF]*<meta')
    #             _result = re.search(pattern, result[0])
    #             if _result:
    #                 _text = re.sub('<style[\u0000-\uFFFF]*</style>', '', _result[0])
    #                 _text = re.sub('<h2[\u0000-\uFFFF]*</h2>', '', _text)
    #                 _text = re.sub('<sup[\u0000-\uFFFF]*</sup>', '', _text)
    #                 _text = re.sub('<table[\u0000-\uFFFF]*</table>', '', _text)
    #                 _text = re.sub('<meta', '', _text)
    #                 _text = re.sub('\n', '', _text)
    #                 detail = _text
    #     return detail

    async def get(self, province):

        data = requests.get(provinces[province])
        pattern = re.compile(
            '<main[\u0000-\uFFFF]*id="ดูเพิ่ม">ดูเพิ่ม</span>')
        result = re.findall(pattern, data.text)

        pattern = re.compile('<li>.*</li>')
        html_list: List[str] = re.findall(pattern, '\n'.join(result))

        all_temple_list = []

        async def worker(html_str):
            name = self.temple_name(html_str)
            if name == '':
                return
            link = self.temple_link(html_str)
            sub_district = self.sub_district_name(html_str)
            detail = await self.temple_detail(link)
            all_temple_list.append({
                "link": link,
                "name": name,
                "sub_district": sub_district if sub_district else ' ',
                "detail": detail
            })

        await asyncio.gather(*[worker(html_str) for html_str in html_list])

        return all_temple_list

    async def get_all(self):
        all = []
        for (key, val) in provinces.items():
            print(key)
            all.append({
                "name": key,
                "temples": await self.get(key)
            })

        return all
