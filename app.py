"""
DiabetesBot - WhatsApp webhook server
Receives messages from Twilio, processes via Claude, saves to Supabase
"""

from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
import uvicorn
import os
from claude_agent import get_claude_response
from database import save_log, get_user_history, is_new_user, save_user_profile

app = FastAPI(title="DiabetesBot")

WELCOME_MESSAGE = """Hey! 👋 I'm *Dia*, your personal diabetes companion.

I'm here to help you log your blood sugar, meals, and how you're feeling — easily and naturally, just like texting a friend 💬

A few things I can do:
📊 Log your glucose readings
🍕 Remember what you ate
💊 Track your insulin
😴 Note how you're feeling

To get started — what's your name, and do you measure your glucose in *mg/dL* or *mmol/L*? 🩺"""


@app.get("/")
def health_check():
    return {"status": "DiabetesBot is running! 🩺"}


@app.post("/webhook", response_class=PlainTextResponse)
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
):
    user_phone = From.replace("whatsapp:", "")
    user_message = Body.strip()

    print(f"📩 Message from {user_phone}: {user_message}")

    # Check if this is a brand new user
    if is_new_user(user_phone):
        print(f"🆕 New user: {user_phone} — sending welcome message")
        save_log(
            phone=user_phone,
            user_message=user_message,
            bot_reply=WELCOME_MESSAGE,
            extracted=None,
        )
        reply_text = WELCOME_MESSAGE
    else:
        # Get last 10 messages for context
        history = get_user_history(user_phone, limit=10)

        # Get Claude's response + extracted data
        result = get_claude_response(user_message, history)
        reply_text = result["reply"]
        extracted = result.get("extracted")

        # If Claude extracted a name or glucose unit, save to user profile
        if extracted:
            profile_updates = {}
            if extracted.get("user_name"):
                profile_updates["name"] = extracted["user_name"]
            if extracted.get("glucose_unit"):
                profile_updates["preferred_unit"] = extracted["glucose_unit"]
            if profile_updates:
                save_user_profile(user_phone, profile_updates)

        # Save conversation log
        save_log(
            phone=user_phone,
            user_message=user_message,
            bot_reply=reply_text,
            extracted=extracted,
        )

    # Return TwiML response
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_text}</Message>
</Response>"""

    return PlainTextResponse(content=twiml, media_type="application/xml")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
