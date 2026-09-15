#ifndef ULTRA_H
#define ULTRA_H

// ============================================================
// HC-SR04 PINS
// ============================================================

#define TRIG_PIN D7
#define ECHO_PIN D8


// ============================================================
// INITIALIZE ULTRASONIC SENSOR
// ============================================================

void ultra_init() {

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  digitalWrite(TRIG_PIN, LOW);
}


// ============================================================
// GET DISTANCE
// Returns distance in centimeters
// ============================================================

float dist() {

  // Send trigger pulse

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);


  // Read echo

  long duration = pulseIn(
    ECHO_PIN,
    HIGH,
    30000
  );


  // No echo

  if (duration == 0) {

    return 999;
  }


  // Calculate distance

  float distance =
    duration * 0.0343 / 2;


  return distance;
}

#endif