from fastapi import FastAPI, Request
import openai
import requests
import uvicorn
import os

app = FastAPI()

WHATSAPP_TOKEN = "EAAPPmGsaoGUBSofferPbOP9eZCnOj66bDYLkZALgE1qHRNcV7rXgLQnTguKy9lR5yeDDRSdQFZCBmqGXeLHXudesZA1UIFLTqvkoZAzCIbQiZBVetw2YfEyLCKVyGkpatvEPx5huzicLvgKVZBdyBSgzztZCJ52CgCD0kYvVLfVJyCfkA4YaBjynjU4kpW9qlGAO7LpQiZB5m4nhnDSuV1KZCkg9fEUDNHyhkiIJaMLgu2SBDkL4Ol6SOXZCDa2I4fMwxyP8VHeGdbIU3ay7TrUQEdkvl97ZCgZDZD"
PHONE_NUMBER_ID = "1337167026145657"
VERIFY_TOKEN = "my_secure_verify_token"
OPENAI_API_KEY = "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"

client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.get("/")
def home():
    return {"status": "SAHAM Bot is running"}

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
    print("=== WEBHOOK POST REQUEST HIT ===")
    try:
        body = await request.json()
        print("Webhook Payload:", body)
        
        changes = body.get("entry", [])[0].get("changes", [])[0].get("value", {})
        if "messages" in changes:
            phone_number = changes["messages"][0]["from"]
            message_body = changes["messages"][0]["text"]["body"]

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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
