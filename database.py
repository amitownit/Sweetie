"""
Database module - saves logs to Supabase and retrieves conversation history
"""

import os
import json
from datetime import datetime
import httpx

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY or "",
    "Authorization": f"Bearer {SUPABASE_KEY or ''}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


def save_log(phone: str, user_message: str, bot_reply: str, extracted: dict | None):
    """Save a conversation turn + any extracted health data to Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️  Supabase not configured — skipping database save")
        return

    payload = {
        "phone": phone,
        "user_message": user_message,
        "bot_reply": bot_reply,
        "timestamp": datetime.utcnow().isoformat(),
        # Extracted health fields (can be null)
        "glucose": extracted.get("glucose") if extracted else None,
        "glucose_unit": extracted.get("glucose_unit") if extracted else None,
        "meal": extracted.get("meal") if extracted else None,
        "insulin": extracted.get("insulin") if extracted else None,
        "mood": extracted.get("mood") if extracted else None,
        "activity": extracted.get("activity") if extracted else None,
        "notes": extracted.get("notes") if extracted else None,
    }

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/diabetes_logs",
                headers=HEADERS,
                json=payload,
            )
            if resp.status_code not in (200, 201):
                print(f"⚠️  Supabase save failed: {resp.status_code} {resp.text}")
            else:
                print(f"✅ Log saved for {phone}")
    except Exception as e:
        print(f"❌ Database error: {e}")


def get_user_history(phone: str, limit: int = 10) -> list:
    """
    Retrieve recent conversation history for a user.
    Returns list of {"role": "user"|"assistant", "content": "..."} dicts.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{SUPABASE_URL}/rest/v1/diabetes_logs",
                headers={**HEADERS, "Prefer": ""},
                params={
                    "phone": f"eq.{phone}",
                    "order": "timestamp.desc",
                    "limit": str(limit),
                    "select": "user_message,bot_reply",
                },
            )
            if resp.status_code != 200:
                return []

            rows = resp.json()
            # Reverse so oldest is first (correct order for Claude context)
            rows = list(reversed(rows))

            history = []
            for row in rows:
                history.append({"role": "user", "content": row["user_message"]})
                history.append({"role": "assistant", "content": row["bot_reply"]})

            return history

    except Exception as e:
        print(f"❌ History fetch error: {e}")
        return []
