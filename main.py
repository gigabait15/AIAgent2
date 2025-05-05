import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from app.database.mongoDB import add_message, get_history
from app.service.ai_groq import o4_model
from app.wa_agent_service.all_service_for_agent import (extract_project_name,
                                                        get_context,
                                                        sys_prompt)
from app.wa_agent_service.get_data import DataResp

app = FastAPI()
s = DataResp()

@app.get('/')
async def root():
    return {'message': 'WAAgent Twillo'}


@app.post("/wh", summary="Webhook для WhatsApp от Twilio", response_class=Response)
async def whatsapp_webhook(request: Request):
    form = await request.form()
    prompt, user_id = await get_context(form)

    context = await s.set_data()
    system_prompt = sys_prompt(context)
    chat_history = [{"role": "system", "content": system_prompt}]

    await add_message(user_id, "user", [{"type": "text", "text": prompt}])
    clean_history = []
    for msg in await get_history(user_id, limit=10):
        if msg.get("role") in ("user", "assistant") and isinstance(msg.get("content"), list):
            text = "".join(
                chunk.get("text", "")
                for chunk in msg["content"]
                if isinstance(chunk, dict)
            )
            clean_history.append({
                "role": msg["role"],
                "content": text
            })

    chat_history += clean_history
    chat_history.append({"role": "user", "content": prompt})

    name_project = extract_project_name(prompt)
    print(name_project)
    if name_project is not None:
        info = await s.set_info_project(name_project) or ""
        chat_history.append(dict(role="system", content=f"If you asked about a specific project {info}"))
        print(f'Получение данных об проекте')

    try:
        response = await o4_model(chat_history).completion_model()
        print(f'ответ модели')
        if not response:
            return {"error": "Empty response from model"}
        print(f'Answer: {response}')

        await add_message(user_id, "assistant", [{"type": "text", "text": response}])

        resp = MessagingResponse()
        resp.message(response)
        chat_history.append({"role": "assistant", "content": response})
        return Response(content=str(resp), media_type="application/xml")

    except Exception as e:
        print(f"Ошибка: {e}")
        return Response(content="Ошибка на сервере", status_code=500)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)