import asyncio
from typing import Optional

from app.database.mongoDB import add_message, get_history
from app.service.ai_groq import o4_model
from app.wa_agent_service.all_service_for_agent import (extract_project_name,
                                                        sys_prompt)
from app.wa_agent_service.get_data import DataResp

s = DataResp()

async def console_chat():
    user_id = input("User ID (From): ").strip()

    # получение данных и промпта
    context: Optional[str] = await s.set_data()
    system_prompt = sys_prompt(context)
    messages = [{"role": "system", "content": system_prompt}]


    print("\nЗапуск чата. Вводите сообщения. Для выхода наберите 'exit'.\n")

    while True:
        user_text = input("You: ").strip()
        await add_message(user_id, "user", [{"type": "text", "text": user_text}])

        if user_text.lower() == "exit":
            print("Выход из чата.")
            break

        # загрузка последних 10 сообщений
        messages += await get_history(user_id, limit=10)
        # проверка на просьбу ссылки на проект
        name_project = extract_project_name(user_text)
        if name_project:
            # получение данных о конкретном проекте
            info = await s.set_info_project(name_project) or ""
            messages.append(dict(role="system", content=f"If you asked about a specific project {info}"))

        print("…Отправляем в модель")
        response = await o4_model(messages).completion_model()
        print(f'Response {response}')

        if not response:
            print("Ошибка: пустой ответ от модели")
            continue

        messages.append({"role": "assistant", "content": response})
        await add_message(user_id, "assistant", [{"type": "text", "text": response}])

if __name__ == "__main__":
    asyncio.run(console_chat())
