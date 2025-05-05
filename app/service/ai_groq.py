import asyncio
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from app import setting

load_dotenv()


class ModelLLM:
    model = "o4-mini-2025-04-16"

    def __init__(self, history: List[Dict[Any, Any]]) -> None:
        """
        Инициализация модели.
        :param history: История сообщений для передачи в чат.
        """
        self.api_key = setting.OPENAI
        self.history = history
        self.client = self.init_client()

    def init_client(self):
        """Инициализирует клиента."""
        return OpenAI(api_key=self.api_key)

    def init_model(self) -> str:
        """
        Синхронный вызов Chat Completion API.
        :return: Ответ модели в виде строки.
        """
        response = self.client.responses.create(
            model=self.model,
            input=self.history
        )
        return response.output[1].content[0].text

    async def completion_model(self) -> str:
        """
        Асинхронный вызов модели с использованием run_in_executor.
        :return: Ответ модели в виде строки.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.init_model)


o4_model = ModelLLM
