import httpx

from app.wa_agent_service.all_service_for_agent import translate_text


class DataResp:
    def __init__(self):
        self.url = 'https://seashell-app-nhpbi.ondigitalocean.app/territory/'

    async def all_project(self):
        """
        Получение данных с сервера
        :return: json данные с сервера
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.url, timeout=5.0)
            return resp.json()

    async def info_project(self, name):
        """
        Получение данных с сервера
        :return: json данные с сервера
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.url+'type/'+name.replace(' ', '%20'), timeout=5.0)
            return resp.json()

    async def set_data(self):
        """
        Получение данных и перевод их в строку
        :return: str
        """
        data = ''
        for i in await self.all_project():
            date = f"{i['construction_end'][5:7]}-{i['construction_end'][:4]}"
            ser_data = (
                f"project name {i['name']} in {i['district']} |construction end {date}|право владения {i['lease_right']}"
                f" year |landtype {i['land_category']} |infrastructure {','.join(i['infrastructure'])}\n")
            data += ser_data
        return await translate_text(data)

    async def set_info_project(self, name):
        """
        Получение данных и перевод их в строку
        :return: str
        """
        data = ''
        for i in await self.info_project(name):
            if i == 'detail':
                return None
            details = i['details']
            land_area = details['land_area'] if details['land_area'] != 'None' else 0
            ocean_view = 'yes' if details['ocean_view'] else 'no'
            has_pool = 'yes' if details['has_pool'] else 'no'
            ser_data = (f"name project:{name}| object type:{i['object_type']}| price:{i['price']}"
                        f"| count room:{details['room_count']}| square:{details['area']}| square area:{land_area}|"
                        f" ocean view:{ocean_view}| pool:{has_pool}| presentation_link:{details['presentation_link']}\n")
            data += ser_data
        return await translate_text(data)


