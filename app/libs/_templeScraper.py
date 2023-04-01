import csv
from typing import List
import requests
import re
import httpx
import asyncio


async def fetch(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True, timeout=20)
        return response

provinces = {
    "chumporn": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดชุมพร",
    "chaengrai": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดเชียงราย",
    "trang": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดตรัง",
    "trat": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดมหาสารคาม",
    "uttaradit": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดอุตรดิตถ์",
}

data = requests.get(provinces["trat"])

print(data.status_code)

pattern = re.compile('<main[\u0000-\uFFFF]*id="ดูเพิ่ม">ดูเพิ่ม</span>')
result = re.findall(pattern, data.text)

pattern = re.compile('<li>.*</li>')
html_list: List[str] = re.findall(pattern, '\n'.join(result))

print(len(html_list))
# [\u0E00-\u0E60]*


def temple_link(html_str: str):
    # remove class attribute in a tag
    pipeline_str = re.sub(' class=\"[a-zA-Z0-9-_ ]*\"', '', html_str)

    # extract link
    list_str = re.findall('<li><a href=\"[^ ]*\"', pipeline_str)

    # if it isn't exists then use dummy link
    if len(list_str) == 0:
        list_str.append('<li><a href=\"https://www.google.com\"')
    pipeline_str: str = list_str[0]

    # extract link
    pipeline_str = re.findall('\".*\"', pipeline_str)[0][1:-1]
    if '/wiki/' in pipeline_str:
        pipeline_str = 'https://th.wikipedia.org'+pipeline_str
    if '/w/' in pipeline_str:
        pipeline_str = 'https://www.google.com'
    return pipeline_str


def temple_name(html_str: str):
    list_str = re.findall('วัด[\u0E00-\u0E60]*', html_str)
    return list_str[0] if len(list_str) != 0 else ""


def sub_district_name(html_str: str):
    list_str = re.findall('ตำบล[\u0E00-\u0E60]*', html_str)
    return list_str[0] if len(list_str) != 0 else ""


async def temple_detail(temple_link: str):
    detail = '<p>no detail</p>'
    if 'th.wikipedia.org' in temple_link:
        temple_html = await fetch(temple_link)
        pattern = re.compile('<main[\u0000-\uFFFF]*<h2>')
        result = re.search(pattern, temple_html.text)
        if result:
            pattern = re.compile('<p>[\u0000-\uFFFF]*<meta')
            _result = re.search(pattern, result[0])
            if _result:
                _text = re.sub(
                    '<style[\u0000-\uFFFF]*</style>', '', _result[0])
                _text = re.sub('<h2[\u0000-\uFFFF]*</h2>', '', _text)
                _text = re.sub('<sup[\u0000-\uFFFF]*</sup>', '', _text)
                _text = re.sub('<table[\u0000-\uFFFF]*</table>', '', _text)
                _text = re.sub('<meta', '', _text)
                _text = re.sub('\n', '', _text)
                detail = _text
    return detail


all_temple_list = [['link', 'temple_name', 'sub_district', 'detail']]


# for html_str in html_list:
async def worker(html_str):
    name = temple_name(html_str)
    if name == '':
        return
    link = temple_link(html_str)
    sub_district = sub_district_name(html_str)
    detail = await temple_detail(link)
    all_temple_list.append(
        [link, name, sub_district if sub_district else ' ', detail])



loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*[worker(html_str) for html_str in html_list]))


filename = 'temple_list_ver_09.csv'

with open(filename, 'w', newline='', encoding="UTF-8") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerows(all_temple_list)
