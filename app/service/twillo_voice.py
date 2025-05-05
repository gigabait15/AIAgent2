import aiohttp

from app.service.translate_audio import audio_to_text


async def fetch_data(**value):
    async with aiohttp.ClientSession() as session:
        async with session.get(**value) as response:
            return await audio_to_text(await response.content.read())
