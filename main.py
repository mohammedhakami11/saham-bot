from fastapi import FastAPI, Request
import openai
import requests

app = FastAPI()

WHATSAPP_TOKEN = "EAAPPmGsaoGUBSofferPbOP9eZCnOj66bDYLkZALgE1qHRNcV7rXgLQnTguKy9lR5yeDDRSdQFZCBmqGXeLHXudesZA1UIFLTqvkoZAzCIbQiZBVetw2YfEyLCKVyGkpatvEPx5huzicLvgKVZBdyBSgzztZCJ52CgCD0kYvVLfVJyCfkA4YaBjynjU4kpW9qlGAO7LpQiZB5m4nhnDSuV1KZCkg9fEUDNHyhkiIJaMLgu2SBDkL4Ol6SOXZCDa2I4fMwxyP8VHeGdbIU3ay7TrUQEdkvl97ZCgZDZD"
PHONE_NUMBER_ID = "1337167026145657"
VERIFY_TOKEN = "my_secure_verify_token"
OPENAI_API_KEY = "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"

client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return int(challenge) if challenge and challenge.isdigit() else challenge
    return {"error": "Invalid verification token"}

@app.post("/webhook")
async def receive_message(request: Request):
    try:
        body = await request.json()
        print("--- Webhook Received ---")
        print(body)
        
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
                        "content": "أنت مساعد ذكي ومفيد عبر واتساب لشركة SAHAM، أجب باختصار وودود."
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
            res = requests.post(url, json=payload, headers=headers)
            print("WhatsApp API Response:", res.text)

    except Exception as e:
        print(f"Error occurred: {e}")

    return {"status": "success"}
