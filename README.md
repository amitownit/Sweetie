# 🩺 DiabetesBot — WhatsApp + Claude MVP

A WhatsApp chatbot that helps teenagers with diabetes log their glucose levels, meals, and moods — naturally, like texting a friend.

---

## What You'll Need (all free to start)

| Account | Website | Notes |
|---|---|---|
| Twilio | twilio.com | For WhatsApp. Free trial gives ~$15 credit |
| Anthropic | console.anthropic.com | For Claude AI. Add $5 to start |
| Railway | railway.app | To host the bot. Free tier works |
| Supabase | supabase.com | For the database. Free tier works |

---

## Step 1 — Set Up Supabase (the database)

1. Go to **supabase.com** → click **Start your project** → sign up
2. Click **New Project** → give it a name like `diabetesbot` → set a password → click **Create project**
3. Wait ~1 minute for it to set up
4. In the left sidebar, click **SQL Editor**
5. Copy the entire contents of the file `setup_database.sql` and paste it in → click **Run**
6. You should see "Success. No rows returned" — that means the table was created ✅
7. Now go to **Project Settings** (gear icon) → **API**
8. Copy these two values — you'll need them later:
   - **Project URL** (looks like `https://abcdef.supabase.co`)
   - **anon / public** key (a long string)

---

## Step 2 — Set Up Twilio for WhatsApp

1. Go to **twilio.com** → sign up for a free account
2. Verify your phone number when asked
3. In the Twilio Console, go to **Messaging → Try it out → Send a WhatsApp message**
4. Follow the instructions to connect your own phone to the Twilio Sandbox (you'll send a code like `join <word>-<word>` to a Twilio number)
5. Your phone is now connected to the sandbox ✅
6. Keep this page open — you'll come back to add the webhook URL in Step 4

---

## Step 3 — Deploy the Bot to Railway

1. Go to **railway.app** → sign up (use GitHub to sign in — easiest)
2. Click **New Project** → **Deploy from GitHub repo**
   - If you haven't uploaded the code yet: first create a free GitHub account, create a new repository, and upload all 4 files (`app.py`, `claude_agent.py`, `database.py`, `requirements.txt`)
3. Select your repository → Railway will detect it's a Python app automatically
4. Click on your deployed service → go to **Variables** tab
5. Add these environment variables (click **+ New Variable** for each):

| Variable Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your key from console.anthropic.com → API Keys |
| `SUPABASE_URL` | The Project URL from Step 1 |
| `SUPABASE_KEY` | The anon/public key from Step 1 |

6. Go to **Settings** → **Networking** → click **Generate Domain**
7. Copy the URL — it looks like `https://diabetesbot-production.up.railway.app`

---

## Step 4 — Connect Twilio to Your Bot

1. Go back to Twilio → **Messaging → Settings → WhatsApp Sandbox Settings**
2. In the field **"When a message comes in"**, paste your Railway URL + `/webhook`:
   ```
   https://diabetesbot-production.up.railway.app/webhook
   ```
3. Make sure the method is set to **HTTP POST**
4. Click **Save**

---

## Step 5 — Test It! 🎉

Send a WhatsApp message to your Twilio sandbox number (the one you connected in Step 2).

Try these messages:
- `"hey, just checked, 142"` → bot should acknowledge the glucose reading
- `"had pizza for lunch"` → bot should log the meal
- `"feeling a bit tired today"` → bot should respond with care

---

## Checking Your Data

To see all logged data:
1. Go to **supabase.com** → your project → **Table Editor**
2. Click on **diabetes_logs**
3. You'll see every message, extracted glucose readings, meals, moods, etc.

---

## Common Problems

**Bot doesn't reply:**
- Check Railway logs (click your service → **Logs** tab) for error messages
- Make sure all 3 environment variables are set correctly
- Make sure the Twilio webhook URL ends with `/webhook`

**"Supabase not configured" in logs:**
- Double-check your `SUPABASE_URL` and `SUPABASE_KEY` variables in Railway

**Claude gives an error:**
- Check your `ANTHROPIC_API_KEY` is correct
- Make sure you have credit on your Anthropic account

---

## What's Next (after MVP works)

- 📊 **Doctor dashboard** — a simple web page showing a patient's glucose chart
- ⏰ **Reminders** — scheduled messages to prompt teens to log
- 📄 **Weekly PDF report** — auto-generated summary to share with medical staff
- 👨‍👩‍👧 **Parent notifications** — alert when a dangerous reading is detected

---

## File Overview

| File | What it does |
|---|---|
| `app.py` | The main server — receives WhatsApp messages from Twilio |
| `claude_agent.py` | Sends messages to Claude, gets back a reply + extracted data |
| `database.py` | Saves conversations and health data to Supabase |
| `requirements.txt` | Python packages needed to run the bot |
| `setup_database.sql` | SQL to create the database table in Supabase |
