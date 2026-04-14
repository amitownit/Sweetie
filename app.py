"""
DiabetesBot - WhatsApp webhook server
Receives messages from Twilio, processes via Claude, saves to Supabase
"""

from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse
import uvicorn
import os
from claude_agent import get_claude_response
from database import save_log, get_user_history

app = FastAPI(title="DiabetesBot")


@app.get("/")
def health_check():
    return {"status": "DiabetesBot is running! 🩺"}


@app.post("/webhook", response_class=PlainTextResponse)
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
):
    """
    Twilio sends a POST request here every time a user sends a WhatsApp message.
    We process it and return a TwiML response.
    """
    user_phone = From.replace("whatsapp:", "")
    user_message = Body.strip()

    print(f"📩 Message from {user_phone}: {user_message}")

    # Get last 10 messages for context
    history = get_user_history(user_phone, limit=10)

    # Get Claude's response + extracted data
    result = get_claude_response(user_message, history)

    reply_text = result["reply"]
    extracted = result.get("extracted")  # glucose, meal, mood, etc.

    # Save to database
    save_log(
        phone=user_phone,
        user_message=user_message,
        bot_reply=reply_text,
        extracted=extracted,
    )

    # Return TwiML (Twilio's format for WhatsApp replies)
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_text}</Message>
</Response>"""

    return PlainTextResponse(content=twiml, media_type="application/xml")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
