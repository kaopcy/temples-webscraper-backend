import csv
import re
import os
import asyncio

from typing import List
from functools import reduce

from app.libs.fetch import fetch


class TempleScraperService:
    async def __get_results_by_province(self, url):
        data = await fetch(url)

        pattern = re.compile(
            '<main[\u0000-\uFFFF]*id="ดูเพิ่ม">ดูเพิ่ม</span>')
        result = re.findall(pattern, data.text)

        pattern = re.compile('<li>.*</li>')
        result = re.findall(pattern, '\n'.join(result))

        result = re.sub(' <a href=\".*ตำบล.*/a>', ' ตำบล', '\n'.join(result))
        result = re.sub('<li>.*? \(ไม่มีหน้า\)\">', '<li>', result)
        result = re.sub(' ตำบล.*', '</li>', result)

        result = re.sub('<li><a href=\"', '<li>', result)
        result = re.sub('\" c', '<\"c', result)
        result = re.sub('\"class=\".*\"', '', result)
        result = re.sub('\"( )?t', ' <\"t', result)
        result = re.sub('<\"( )?title=\".*\">', '', result)

        result = re.sub('/wiki/', "https://th.wikipedia.org/wiki/", result)
        result = re.sub('<li>วัด', '<li>https://www.google.com วัด', result)
        result = re.sub('( )?วัด', ' <h_0>วัด', result)
        result = re.sub('</li>', '</h_0></li>', result)

        result = re.sub(' \(.*\)', '', result)
        result = re.sub('<(/a)?>', '', result)

        return result.split('\n')

    async def __get_further_detail(self, temples_html):
        detailed_temple = []

        async def worker(temple_html):
            if 'th.wikipedia.org' in temple_html:
                temple_url = re.search(
                    f'https://th.wikipedia.org/.* ', temple_html)[0]
                new_temple_data = await fetch(temple_url)
                pattern = re.compile('<main[\u0000-\uFFFF]*<h2>')
                result = re.search(pattern, new_temple_data.text)
                temple_detail = '<h_1><p>no detail</p></h_1>'
                if result:
                    pattern = re.compile('<p>[\u0000-\uFFFF]*<meta')
                    _result = re.search(pattern, result[0])
                    if _result:
                        _text = re.sub(
                            '<style[\u0000-\uFFFF]*</style>', '', _result[0])
                        _text = re.sub(
                            '<h2[\u0000-\uFFFF]*</h2>', '', _text)
                        _text = re.sub(
                            '<sup[\u0000-\uFFFF]*</sup>', '', _text)
                        _text = re.sub(
                            '<table[\u0000-\uFFFF]*</table>', '', _text)
                        _text = re.sub('<meta', '', _text)
                        _text = re.sub('\n', '', _text)
                        temple_detail = _text
                updated_temple = re.sub(
                    '</li>', '<h_1>'+temple_detail+'</h_1></li>', temple_html)

                detailed_temple.append(updated_temple)

        await asyncio.gather(*[worker(temple_html) for temple_html in temples_html])
        return detailed_temple

    def __clean_data(self, temples_html, temples_html_with_detail) -> List[dict]:
        for temple_str in temples_html:
            if 'google.com' in temple_str:
                temple_detail = '<h_1><p>no detail</p></h_1>'
                updated_temple = re.sub(
                    '</li>', '<h_1>'+temple_detail+'</h_1></li>', temple_str)
                temples_html_with_detail.append(updated_temple)

        arranged_result = []
        for temple in temples_html_with_detail:
            if 'no detail' not in temple:
                arranged_result.insert(0, temple)
            else:
                arranged_result.append(temple)

        all_temple_list = []
        for temple in arranged_result:
            link = re.findall('<li>.* <h_0>วัด', temple)[0]
            link = re.sub(' <?h_0>วัด', '', link)
            link = re.sub('<li>', '', link)

            temple_name = re.findall(
                '<h_0>วัด[\u0000-\uFFFF]*</h_0>', temple)[0]
            temple_name = re.sub('</?h_0>', '', temple_name)

            detail = re.findall('<h_1>[\u0000-\uFFFF]*</h_1>', temple)[0]
            detail = re.sub('</?h_1>', '', detail)
            all_temple_list.append({
                "link": link,
                "name": temple_name,
                "detail": detail,
            })
        return all_temple_list

    async def write_csv_file(self, name, data):
        dir = os.path.join(os.path.split(
            os.path.abspath(__file__))[0], 'data')

        os.makedirs(dir, exist_ok=True)

        with open(os.path.join(dir, f"{name}.csv"), 'w', newline='', encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(data)

    async def to_csv_file(self, url):
        json = await self.to_json(url)
        if type(json) is list and len(json) > 0:
            # convert json to csv
            csv = reduce(lambda acc, cur: [
                         *acc, [*cur.values()]], json, [[*json[0].keys()]])

            await self.write_csv_file(url.split('.')[-2].split('/')[-1], csv)
            return csv
        return [[]]

    async def to_json(self,  url):
        temples_html = await self.__get_results_by_province(url)
        temples_html_with_detail = await self.__get_further_detail(temples_html)

        cleaned_temple_data = self.__clean_data(
            temples_html, temples_html_with_detail)
        return cleaned_temple_data

    async def all(self):
        provinces = {
            # "chumporn": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดชุมพร",
            # "chaengrai": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดเชียงราย",
            # "trang": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดตรัง",
            "trat": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดตราด",
            # "uttaradit": "https://th.wikipedia.org/wiki/รายชื่อวัดในจังหวัดอุตรดิตถ์",
        }

        async def worker(province, province_url):
            json = await self.to_json(province_url)
            return {
                "name": province,
                "temples": json
            }

        return await asyncio.gather(*[worker(province, province_url) for (province, province_url) in provinces.items()])
