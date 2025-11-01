-- heart_schema.sql
CREATE DATABASE IF NOT EXISTS heart_disease_db;
USE heart_disease_db;

CREATE TABLE patients (
  patient_id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  dob DATE,
  gender VARCHAR(16),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE encounters (
  encounter_id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  visit_date DATETIME NOT NULL,
  doctor VARCHAR(100),
  notes TEXT,
  FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

CREATE TABLE ecg_tests (
  test_id INT AUTO_INCREMENT PRIMARY KEY,
  encounter_id INT NOT NULL,
  age INT,
  sex INT,
  cp INT,
  trestbps INT,
  chol INT,
  fbs INT,
  restecg INT,
  thalach INT,
  exang INT,
  oldpeak DECIMAL(4,2),
  slope INT,
  ca INT,
  thal INT,
  target INT,
  FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id) ON DELETE CASCADE
);

CREATE TABLE audit_logs (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  action VARCHAR(50) NOT NULL,
  object_type VARCHAR(50),
  object_id VARCHAR(64),
  details JSON,
  logged_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patients_name ON patients(last_name, first_name);
CREATE INDEX idx_encounters_patient ON encounters(patient_id);
CREATE INDEX idx_ecg_tests_encounter ON ecg_tests(encounter_id);

DELIMITER //
CREATE PROCEDURE insert_new_patient(
  IN p_first VARCHAR(100),
  IN p_last VARCHAR(100),
  IN p_dob DATE,
  IN p_gender VARCHAR(16)
)
BEGIN
  DECLARE new_id INT;

  IF p_dob > CURDATE() THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Date of birth cannot be in the future';
  END IF;

  INSERT INTO patients(first_name, last_name, dob, gender)
  VALUES (p_first, p_last, p_dob, p_gender);

  SET new_id = LAST_INSERT_ID();

  INSERT INTO audit_logs(action, object_type, object_id, details)
  VALUES('INSERT', 'patients', new_id, JSON_OBJECT('first_name', p_first, 'last_name', p_last));

  SELECT new_id AS patient_id;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER after_ecg_insert
AFTER INSERT ON ecg_tests
FOR EACH ROW
BEGIN
  INSERT INTO audit_logs(action, object_type, object_id, details)
  VALUES('INSERT','ecg_tests', NEW.test_id, JSON_OBJECT('encounter_id', NEW.encounter_id, 'target', NEW.target, 'age', NEW.age));
END //
DELIMITER ;
