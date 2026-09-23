# SmartToken Feature Specification

## Patient flow
1. Landing page
2. Patient Register / Login
3. Patient details:
   - Full name
   - Location
   - Phone
   - Email
4. Choose doctor specialty
5. Enter location preference and optionally choose a nearby hospital
6. Search hospitals by hospital name, locality, city, PIN code or service
7. Confirm appointment
8. Generate token
9. Show:
   - Token number
   - Queue position
   - Appointment time
   - Estimated waiting time
   - Estimated arrival time
10. Notification center simulates email + SMS updates.

## Administrator flow
1. Hospital code login
2. Hospital dashboard
3. Specialty/department cards
4. Queue list with token, patient, status and ETA
5. Event controls:
   - Cancellation
   - Emergency insertion
   - Doctor unavailable / transfer
6. Re-forecast queue
7. Notify affected patients

## Re-forecast rule in prototype
The demo uses a transparent simulation rather than claiming a trained ML model.

Estimated waiting time is recalculated from:
- Current queue order
- Department average consultation duration
- Priority/emergency insertion
- Cancellation
- Doctor availability
- Small operational buffer

The architecture leaves a clear place for a trained model later.


### Nearby hospital ranking upgrade
- Added additional Mumbai public/municipal hospitals across central, western and eastern suburbs.
- Existing frontend remains unchanged.
- When the patient taps **Use my location**, compatible browsers request location permission and hospitals matching the selected specialty are sorted from nearest to farthest using straight-line geographic distance.
- Distance is displayed on each hospital card.
- Hospital-name, locality, city and PIN search continues to work normally.
- If the patient does not share location, the existing search flow continues unchanged.
