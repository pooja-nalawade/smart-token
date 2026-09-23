# SmartToken — Smart OPD Token & Live Wait-Time Prediction

A frontend-first hackathon prototype for a government-hospital OPD smart token system.

## Core idea
The system replaces paper-token uncertainty with:
- Digital patient registration
- Specialty selection
- Location + nearby-hospital discovery
- Appointment/token generation
- Estimated waiting time (EWT)
- Estimated arrival time (EAT)
- Live queue position
- SMS/email notification simulation
- Administrator live queue dashboard
- Three live disruption events:
  1. Patient cancellation
  2. Emergency walk-in insertion
  3. Doctor unavailability + alternative doctor transfer

The uploaded project presentation describes the central twist as live re-forecasting when emergency/priority patients change the queue. It also describes token + ETA, hospital/OPD dashboard, queue engine, prediction layer, and SMS/basic-phone accessibility.

## Demo
Open `frontend/index.html` in a browser.

For the best local experience, use VS Code Live Server or:
```bash
python -m http.server 5500
```
then visit:
`http://localhost:5500/frontend/`

## Important prototype note
This ZIP is a working frontend prototype. Real email/SMS, authentication, maps/places, persistent database, and ML prediction require backend/API integration.

## Suggested production stack
Frontend: HTML/CSS/JavaScript or React
Backend: Node.js/Express or PHP
Database: MySQL/PostgreSQL
Maps/Places: Google Maps/Places or another approved provider
Notifications: SMS gateway + email provider
Prediction: Python service / ML model
Realtime: WebSocket/Socket.IO

## Safety/privacy
For a real healthcare deployment, add consent, secure authentication, encryption, audit logs, role-based access, data minimization, and applicable Indian healthcare/privacy requirements.
