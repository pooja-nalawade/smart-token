USE smarttoken;

ALTER TABLE appointments
  ADD COLUMN IF NOT EXISTS appointment_time VARCHAR(80) NULL,
  ADD COLUMN IF NOT EXISTS wait_minutes INT NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS arrival_time VARCHAR(80) NULL,
  ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'BOOKED';

CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_token ON appointments(token_id);
