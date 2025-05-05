import re

import tiktoken
from aiohttp import BasicAuth
from googletrans import Translator

from app import setting
from app.service.twillo_voice import fetch_data

translator = Translator(service_urls=['translate.googleapis.com'])


# 2 тут проверка на язык
def is_russian(text: str) -> bool:
    """
    Проверка раскладки
    :param text:
    :return: bool"""
    return bool(re.search(r'[\u0400-\u04FF]', text))

# 3 тут переводчик ru <-> eng
async def translate_text(text: str, dest: bool = False) -> str:
    """
    Переводит текст асинхронно на язык dest ('ru' или 'en'),
    разбивая на чанки по 5000 символов.
    """
    lang = 'ru' if dest else 'en'
    src = 'en' if dest else 'ru'
    max_len = 5000

    async def do_chunk(chunk: str) -> str:
        # (из) src (в) dest
        result = await translator.translate(chunk, src=src, dest=lang)
        return result.text

    if len(text) <= max_len:
        return await do_chunk(text)

    parts = []
    for i in range(0, len(text), max_len):
        parts.append(await do_chunk(text[i:i+max_len]))
    return "".join(parts)

# 4 счетчик токенов
def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# 5 проверка на название проекта
def extract_project_name(text: str) -> str | None:
    """
    Получение названия проекта из контекста
    :param text: сообщение от пользователя
    :return: название проекта, если пользователь о нем упомянал
    """
    m = re.search(r'\b(?:про|о)\s+["«]?([\w\s\-]+?)["»]?(?:[\.!\?]|$)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m2 = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', text)
    if m2:
        return m2.group(1).strip()
    return None

# 6 общий промпт
def sys_prompt(context: str) -> str:
    return (
        f"Ты — консультант по недвижимости на Бали, имитируешь живого представителя девелопера. "
        f"Работаешь только на основе этих данных:\n\n{context}\n\n"
        "Тон общения:\n"
        "- Коротко, живо, дружелюбно; простыми фразами.\n"
        "- Используй уместные эмодзи, но не перегружай ими сообщения.\n"
        "- Если не знаешь имени, сразу спроси. Вот пример вопроса «Здравствуйте, как вас зовут?»\n"
        "- Раз в три сообщения обращайся по имени.\n\n"
        "- После получения имени, отвечай в стиле «Приятно познакомиться [Имя], я консультант по недвижимости LOYO&BONDAR.».\n"
        "Структура диалога:\n"
        "- После имени уточни район: «Какой район вас интересует?»\n"
        "- Затем спроси про тип жилья: «Вилла или апартаменты?»\n"
        "- Если данных мало, задай 1–2 дополнительных вопроса.\n"
        "- Не предлагай сразу созвон: позже, после важных ответов клиента, можно мягко сказать"
        " «Если хотите, можем созвониться и обсудить детали».\n\n"
        "Цель бота — помогать, а не давить на продажу. Будь тактичным, искренним и ненавязчивым."
    )

# 7 разбивка на предложения
def chunks(answer: str) -> list|str:
    """
    Разбивка ответа на чанки, для отправки нескольких сообщений
    :param answer: строка, ответ nlp модели
    :return: list[str] или str
    """
    parts = [line.strip() for line in answer.splitlines() if line.strip()]
    return answer if len(parts) <= 1 else parts

# Проверка на тип данных
async def get_context(form) -> tuple[str, str]:
    """
    Получение номера и текста из request twillo
    :param form: данные приходящие от сервиса twillo
    :return: tuple с номером и текстом
    """
    if form.get("MessageType") == 'audio':
        auth = BasicAuth(setting.SID, setting.TOKEN)
        prompt = await fetch_data(url=form.get('MediaUrl0'), auth=auth)
    else:
        prompt = form.get('Body')
    return prompt, form.get("WaId")
