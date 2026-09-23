-- SmartToken starter database schema
CREATE DATABASE IF NOT EXISTS smart_token;
USE smart_token;

CREATE TABLE patients (
  id INT PRIMARY KEY AUTO_INCREMENT,
  full_name VARCHAR(120) NOT NULL,
  location VARCHAR(255) NOT NULL,
  phone VARCHAR(30) NOT NULL,
  email VARCHAR(160) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hospitals (
  id INT PRIMARY KEY AUTO_INCREMENT,
  hospital_code VARCHAR(40) UNIQUE NOT NULL,
  name VARCHAR(180) NOT NULL,
  address VARCHAR(300) NOT NULL,
  locality VARCHAR(120),
  city VARCHAR(120),
  state VARCHAR(120),
  pincode VARCHAR(10),
  latitude DECIMAL(10,7),
  longitude DECIMAL(10,7)
);

CREATE TABLE departments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  hospital_id INT NOT NULL,
  name VARCHAR(120) NOT NULL,
  avg_consult_minutes INT NOT NULL DEFAULT 10,
  FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
);

CREATE TABLE appointments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  patient_id INT NOT NULL,
  hospital_id INT NOT NULL,
  department_id INT NOT NULL,
  token_number INT NOT NULL,
  appointment_time DATETIME NOT NULL,
  estimated_wait_minutes INT NOT NULL,
  estimated_arrival_time DATETIME NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'WAITING',
  priority VARCHAR(30) NOT NULL DEFAULT 'NORMAL',
  FOREIGN KEY (patient_id) REFERENCES patients(id),
  FOREIGN KEY (hospital_id) REFERENCES hospitals(id),
  FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE queue_events (
  id INT PRIMARY KEY AUTO_INCREMENT,
  hospital_id INT NOT NULL,
  department_id INT NOT NULL,
  event_type VARCHAR(40) NOT NULL,
  event_minutes INT NULL,
  details TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notification_log (
  id INT PRIMARY KEY AUTO_INCREMENT,
  appointment_id INT NOT NULL,
  channel VARCHAR(20) NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
