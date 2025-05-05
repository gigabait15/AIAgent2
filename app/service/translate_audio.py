import asyncio
from io import BytesIO

import speech_recognition as sr
from pydub import AudioSegment


def _sync_audio_to_text(audio_data: bytes) -> str:
    """
    Преобразует байтовое аудио в текст с использованием Google Speech Recognition.

    :param audio_data: Аудио в формате байтов.
    :return: Распознанный текст.
    :raises RuntimeError: В случае ошибки распознавания или сетевого запроса.
    """
    # Преобразование байтового аудиофайла в формат WAV
    audio_data = AudioSegment.from_file(BytesIO(audio_data))
    audio_wav = BytesIO()
    audio_data.export(audio_wav, format="wav")
    audio_wav.seek(0)  # Перемещение указателя в начало файла

    # Инициализация распознавателя речи
    recognizer = sr.Recognizer()

    # Загрузка WAV-файл в recognizer
    with sr.AudioFile(audio_wav) as source:
        audio_content = recognizer.record(source)  # Чтение аудио

    # Попытка распознавания речи
    try:
        return recognizer.recognize_google(audio_content, language="ru-RU")
    except (sr.UnknownValueError, sr.RequestError, Exception):
        return None


async def audio_to_text(audio_data: bytes) -> str | None:
    return await asyncio.to_thread(_sync_audio_to_text, audio_data)