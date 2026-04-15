"""
Database module - saves logs to Supabase and retrieves conversation history
Includes user profile support (name, preferred glucose unit)
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


def is_new_user(phone: str) -> bool:
    """Returns True if this phone number has never messaged before."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{SUPABASE_URL}/rest/v1/diabetes_logs",
                headers={**HEADERS, "Prefer": ""},
                params={
                    "phone": f"eq.{phone}",
                    "limit": "1",
                    "select": "id",
                },
            )
            if resp.status_code == 200:
                return len(resp.json()) == 0
    except Exception as e:
        print(f"❌ is_new_user error: {e}")
    return False


def save_user_profile(phone: str, updates: dict):
    """
    Save or update user profile info (name, preferred glucose unit).
    Uses upsert so it creates or updates.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return

    payload = {"phone": phone, **updates}

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/user_profiles",
                headers={**HEADERS, "Prefer": "resolution=merge-duplicates"},
                json=payload,
            )
            if resp.status_code not in (200, 201):
                print(f"⚠️ Profile save failed: {resp.status_code} {resp.text}")
            else:
                print(f"✅ Profile updated for {phone}: {updates}")
    except Exception as e:
        print(f"❌ Profile save error: {e}")


def get_user_profile(phone: str) -> dict:
    """Get user profile (name, preferred unit) if it exists."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {}
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{SUPABASE_URL}/rest/v1/user_profiles",
                headers={**HEADERS, "Prefer": ""},
                params={"phone": f"eq.{phone}", "select": "*"},
            )
            if resp.status_code == 200:
                rows = resp.json()
                return rows[0] if rows else {}
    except Exception as e:
        print(f"❌ Profile fetch error: {e}")
    return {}


def save_log(phone: str, user_message: str, bot_reply: str, extracted: dict | None):
    """Save a conversation turn + extracted health data to Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️  Supabase not configured — skipping save")
        return

    payload = {
        "phone": phone,
        "user_message": user_message,
        "bot_reply": bot_reply,
        "timestamp": datetime.utcnow().isoformat(),
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
                print(f"⚠️  Log save failed: {resp.status_code} {resp.text}")
            else:
                print(f"✅ Log saved for {phone}")
    except Exception as e:
        print(f"❌ Database error: {e}")


def get_user_history(phone: str, limit: int = 10) -> list:
    """
    Retrieve recent conversation history for context.
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

            rows = list(reversed(resp.json()))
            history = []
            for row in rows:
                history.append({"role": "user", "content": row["user_message"]})
                history.append({"role": "assistant", "content": row["bot_reply"]})
            return history

    except Exception as e:
        print(f"❌ History fetch error: {e}")
        return []
