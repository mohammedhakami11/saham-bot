from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

WHATSAPP_TOKEN = "EAAPPmGsaoGUBSiilbMTVGYRyFFwNOsxnBMAqF8xYuQk3foN3HTt6YxZA8bmlJfs7ZAFWznxYjHpy9SduLYyPOxtEAyzPgsqve3Rb1S1jI47ZBBOdDRO4TyuIy9eEmtpoZCmVIF769RzPO8ZBktQ6I0lRl4fzaZATZBPfTfF5xLTBpHVqjVdi3208gQ2PZAjZBO8dBP5XN2NVZAHXuVhg4A481EaNTMddgZBaZAErkZC34PjlZAnZCRytILEaTX1fIf5vfPZAZCLGS1lmbKUlyDt3UJ6xg5hEW5qbr"
PHONE_NUMBER_ID = "1337167026145657"
VERIFY_TOKEN = "my_secure_verify_token"

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
        return "Verification failed", 403
    return "Hello World", 200

@app.post("/webhook")
async def webhook_listener(request: Request):
    data = await request.json()
    print("Webhook Payload:", data)
    
    try:
        # استخراج رقم المرسل ونص الرسالة من طلب واتساب
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages")
        
        if messages:
            sender_phone = messages[0]["from"]
            message_body = messages[0]["text"]["body"]
            print(f"Received message from {sender_phone}: {message_body}")
            
            # إرسال رد ثابت ومباشر إلى واتساب بدون الحاجة لـ OpenAI
            reply_text = f"أهلاً بك! وصلني ردك: ({message_body})، البوت يعمل بنجاح!"
            
            headers = {
                "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": sender_phone,
                "type": "text",
                "text": {"body": reply_text}
            }
            
            response = requests.post(
                f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages",
                json=payload,
                headers=headers
            )
            print("WhatsApp API Response:", response.text)
            
    except Exception as e:
        print("Error processing webhook:", e)
        
    return {"status": "received"}
