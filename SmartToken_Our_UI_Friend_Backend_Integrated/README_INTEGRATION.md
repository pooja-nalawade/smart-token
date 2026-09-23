# SmartToken — Your UI + Integrated Real Email/SMS Backend

## What this version does

This version keeps the **existing SmartToken frontend UI unchanged**:
- same landing page
- same patient registration modal
- same specialty cards
- same Mumbai hospital cards and nearby sorting
- same appointment confirmation screen
- same admin dashboard
- same event modal/design

Only the JavaScript behavior and backend are connected.

The backend is adapted from the supplied friend project and provides:
- FastAPI API
- SQLite database (no MySQL setup is required for this integrated version)
- live queue recalculation
- real Gmail SMTP email
- real Twilio SMS
- patient registration
- appointment creation
- patient live ETA polling
- cancellation -> affected patients receive updated ETA email/SMS
- emergency walk-in -> admin supplies department + delay minutes; affected patients receive updated ETA email/SMS
- doctor unavailable -> queue transfers to an alternative doctor; affected patients receive doctor-change email/SMS
- admin dashboard polling every 5 seconds

## Important

The ZIP does **not** contain your email password, Gmail app password, Twilio Account SID, Twilio Auth Token, or other secrets.

You must create `backend/.env` yourself from `backend/.env.example`.

---

# Windows 11 setup

## 1. Install Python

Install Python 3.11+.

Check:

```bat
python --version
```

or:

```bat
py --version
```

## 2. Open this project in VS Code

Open the extracted project folder:

```text
SmartToken_Our_UI_Friend_Backend_Integrated
```

## 3. Open Command Prompt / VS Code terminal

Run:

```bat
cd backend
```

Create a virtual environment:

```bat
py -m venv .venv
```

Activate it:

```bat
.venv\Scripts\activate
```

Install dependencies:

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Create the backend .env

Copy:

```text
backend/.env.example
```

to:

```text
backend/.env
```

Do NOT commit `.env` to GitHub.

---

# REAL EMAIL SETUP — Gmail

Use a Gmail address that you control.

## A. Turn on 2-Step Verification

Open your Google Account security settings and enable 2-Step Verification.

## B. Create a Google App Password

Create an App Password for this SmartToken project.

Google gives you a 16-character app password.

Put that app password into:

```env
SMTP_PASSWORD=your_16_character_app_password
```

Do NOT put your normal Gmail password here.

Example:

```env
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=yourgmail@gmail.com
SMTP_PASSWORD=xxxxxxxxxxxxxxxx
SMTP_FROM=SmartToken <yourgmail@gmail.com>
```

The 16-character value is a secret. Never put it in GitHub or send it in screenshots.

---

# REAL SMS SETUP — Twilio

Create/sign in to a Twilio account.

Get:
- Account SID
- Auth Token
- Twilio phone number capable of sending SMS

Put them in:

```env
SMS_ENABLED=true
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_FROM_NUMBER=+1xxxxxxxxxx
TWILIO_MESSAGING_SERVICE_SID=
```

For a Twilio trial account, the destination number may need to be verified in Twilio before trial SMS can be sent.

Use an Indian mobile number in the SmartToken patient form:

```text
9876543210
```

The backend converts it to:

```text
+919876543210
```

---

# 5. Start the backend

From:

```text
backend
```

with the virtual environment activated:

```bat
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```text
Uvicorn running on http://0.0.0.0:8000
```

Open:

```text
http://localhost:8000
```

This opens **your original SmartToken UI**.

Do NOT open `frontend/index.html` directly with file://.

---

# 6. Check the backend

Open:

```text
http://localhost:8000/api/health
```

Expected:

```json
{
  "status": "ok",
  "email_enabled": true,
  "sms_enabled": true
}
```

If either is false, check `backend/.env`.

---

# 7. Test a real appointment

Use a real test email that you can access.

Use your own mobile number first.

Flow:

```text
SmartToken home
    ↓
Patient Registration
    ↓
Choose specialty
    ↓
Choose hospital
    ↓
Confirm appointment
    ↓
Generate Smart Token
```

The backend creates the patient + appointment.

It then:
1. calculates queue position
2. calculates waiting time
3. calculates estimated consultation time
4. calculates recommended arrival time
5. sends appointment email
6. sends appointment SMS
7. returns the token to your UI

---

# 8. Test the live cancellation event

First create at least 3 appointments for the same department using different email/mobile numbers.

Example:

```text
Token T-001
Token T-002
Token T-003
```

Open:

```text
http://localhost:8000/admin.html
```

Choose:

```text
Patient cancellation
```

Select the department and token.

Click:

```text
Apply & Re-forecast Queue
```

Backend behavior:

```text
Patient cancels
      ↓
Appointment status = CANCELLED
      ↓
Queue recalculated
      ↓
Remaining patients get new position
      ↓
Waiting time recalculated
      ↓
ETA recalculated
      ↓
Email sent
      ↓
SMS sent
```

So the next patients receive the new information automatically.

---

# 9. Test emergency insertion

Open:

```text
Admin → Emergency walk-in
```

Select:
- department
- emergency handling time, e.g. 20 minutes
- emergency identifier

Click:

```text
Apply & Re-forecast Queue
```

Backend:

```text
Emergency inserted at priority position
        ↓
20-minute delay added to affected normal patients
        ↓
Queue recalculated
        ↓
New ETA generated
        ↓
Affected patients receive email + SMS
```

---

# 10. Test doctor unavailable

Open:

```text
Admin → Doctor unavailable
```

Select:
- department
- alternative doctor
- reason

Click:

```text
Apply & Re-forecast Queue
```

Backend:

```text
Current doctor marked unavailable
        ↓
Alternative doctor selected
        ↓
Waiting appointments transferred
        ↓
Queue recalculated
        ↓
Patients receive doctor-change email + SMS
```

---

# 11. Live patient update

After booking, the patient page polls:

```text
/api/queue/appointment/{appointment_id}
```

every 5 seconds.

Therefore the token screen can update when:
- another patient cancels
- an emergency is inserted
- the doctor changes
- the queue is otherwise re-forecasted

---

# Files you should know

```text
SmartToken_Our_UI_Friend_Backend_Integrated/
│
├── frontend/
│   ├── index.html                 ← YOUR UI, unchanged
│   ├── admin.html                 ← YOUR UI, unchanged
│   └── assets/
│       ├── css/styles.css         ← YOUR UI styling, unchanged
│       └── js/
│           ├── app.js             ← UI connected to real backend
│           └── admin.js           ← UI connected to real backend
│
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── models.py
│       ├── schemas.py
│       ├── seed.py
│       ├── database.py
│       ├── config.py
│       ├── routes/
│       │   ├── patients.py
│       │   ├── specialties.py
│       │   ├── hospitals.py
│       │   ├── appointments.py
│       │   ├── queue.py
│       │   └── admin.py
│       └── services/
│           ├── notification_service.py
│           └── prediction_service.py
│
└── docs/
```

## UI guarantee

No HTML/CSS redesign was made for this integration.

The existing UI is used as the presentation layer. The backend replaces the old simulated queue/notification behavior.

## Security reminder

Never upload:

```text
backend/.env
```

to GitHub.

Never share:

```text
Gmail App Password
Twilio Auth Token
Twilio Account SID
```

in screenshots or presentations.
