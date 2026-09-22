from fastapi import FastAPI, Request
import openai
import requests

app = FastAPI()

# بيانات واتساب ومفتاح OpenAI الخاص بك (محدثة وجاهزة)
WHATSAPP_TOKEN = "EAAPPmGsaoGUBSuCds7puVQsPulfu039qZArxhiLi61vk0z1nVZAa6Ev2YvnGc6BMij09HzWcCZCLlTM0b0hJOeYzDw9IPubZBW0YA0TNMu6YL2XAfBkm3u7xoxj9XmjyP5ljhybJxlV1cuAOLkjf4DjTygCFHhFlseYo6IXOeDZCTneb0JPEZCxOKZAsYFFvOsZAozM3jiCj5dh9x6SL046bfG433pOXFWF4XLWnTUpEEj1q6Y7HnPZC3oVXaXMgjJ99Eqpc6N3qjgc1peAhPYQ0Gt4c1"
PHONE_NUMBER_ID = "1337167026145657"
VERIFY_TOKEN = "my_secure_verify_token"
OPENAI_API_KEY = (
    "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"
)

client = openai.OpenAI(api_key=OPENAI_API_KEY)


@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return int(challenge) if challenge.isdigit() else challenge
    return {"error": "Invalid verification token"}


@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()

    try:
        changes = body["entry"][0]["changes"][0]["value"]
        if "messages" in changes:
            phone_number = changes["messages"][0]["from"]
            message_body = changes["messages"][0]["text"]["body"]

            # إرسال الرسالة إلى نموذج OpenAI للحصول على رد ذكي
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "أنت مساعد ذكي ومفيد عبر واتساب لشركة SAHAM، أجب"
                            " باختصار وودود."
                        ),
                    },
                    {"role": "user", "content": message_body},
                ],
            )
            ai_response = response.choices[0].message.content

            # إرسال الرد عبر واتساب API
            url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                "Content-Type": "application/json",
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "text": {"body": ai_response},
            }
            requests.post(url, json=payload, headers=headers)

    except Exception as e:
        print(f"Error: {e}")

    return {"status": "success"}
