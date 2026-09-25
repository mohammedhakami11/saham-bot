from fastapi import FastAPI, Request
import requests

app = FastAPI()

WHATSAPP_TOKEN = "EAAPMgSaoGUBsofferPbOP9eZCnOj66bDrYLkZALGe1qHRncV7rXgLQntGuKy91R5yEDDSDQfCbMqGXelHXudesZA1UIFLTqvkoZAZCibQIZBWetV2FfYLKGyGkpatVEP5huzicLvgKZBdyBS"
PHONE_NUMBER_ID = "1337167026145657"
VERIFY_TOKEN = "my_secure_verify_token"

@app.get("/")
def home():
    return {"status": "SAHAM Bot is running (Smart Free Version)"}

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
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages")
        
        if messages:
            sender_phone = messages[0]["from"]
            message_body = messages[0]["text"]["body"].strip().lower()
            print(f"Received message from {sender_phone}: {message_body}")
            
            # منطق الردود الذكية المجانية بناءً على الكلمات المفتاحية
            if "مرحباً" in message_body or "السلام" in message_body or "اهلا" in message_body:
                reply_text = "أهلاً بك في بوت سهم (SAHAM)! 🚀 كيف يمكنني مساعدتك اليوم؟ (اختر: خدمات، أسعار، تواصل)"
            elif "خدمات" in message_body:
                reply_text = "نحن نقدم خدمات تقنية متقدمة، ربط أنظمة، وتطوير مساعدين ذكيين عبر واتساب."
            elif "أسعار" in message_body or "سعر" in message_body:
                reply_text = "الخدمة الحالية مجانية تماماً للتجربة والتطوير! 💡"
            elif "تواصل" in message_body:
                reply_text = "يمكنك التواصل معنا مباشرة عبر الرد على هذه الرسالة."
            else:
                reply_text = f"عذراً، لم أفهم رسالتك: '{message_body}'. يمكنك كتابة (خدمات) أو (أسعار) أو (مرحباً)."
            
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
