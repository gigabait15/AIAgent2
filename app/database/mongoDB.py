from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["chatbot"]
messages = db["messages"]

# Создать индекс один раз
async def ensure_indexes():
    await messages.create_index([("user_id", ASCENDING), ("timestamp", ASCENDING)])

# Добавить сообщение
async def add_message(user_id: str, role: str, content: list[dict]):
    await messages.insert_one({
        "user_id": user_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })

# Получить последние N сообщений
async def get_history(user_id: str, limit: int = 10):
    cursor = messages.find(
        {"user_id": user_id},  {"_id": 0, "role": 1, "content": 1}
    ).sort("timestamp", -1
           ).limit(limit)
    history = await cursor.to_list(length=limit)
    return history[::-1]
