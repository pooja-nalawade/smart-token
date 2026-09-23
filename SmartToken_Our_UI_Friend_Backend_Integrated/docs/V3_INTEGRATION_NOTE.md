# Connecting the unchanged frontend

The frontend design and files are unchanged. The current prototype's JavaScript still displays simulated notification messages.

To activate real delivery, the appointment submit handler must call:

```js
fetch('http://localhost:5000/api/appointments', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: patient.name,
    email: patient.email,
    phone: patient.phone,
    hospital: selectedHospital.name,
    department: selectedSpecialty.name,
    token: generatedToken,
    appointmentTime: appointmentTime,
    waitMinutes: waitMinutes
  })
});
```

For cancellation, emergency, or doctor-unavailable events, call `/api/queue-update` with the affected appointment IDs and the newly calculated wait time.

The frontend visual appearance is intentionally not changed. This note identifies the exact backend contract needed to replace the prototype's simulated notification calls.
