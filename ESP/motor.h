#ifndef MOTOR_H
#define MOTOR_H

// L298N Motor Driver pins

#define IN1 D1
#define IN2 D2

#define IN3 D3
#define IN4 D4


// Function declarations
void motor_init();
void forward();
void reverse();
void left();
void right();
void stop();


// ---------------- MOTOR INITIALIZATION ----------------

void motor_init() {

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  stop();
}


// ---------------- FORWARD ----------------

void forward() {

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  Serial.println("FORWARD");
}


// ---------------- REVERSE ----------------

void reverse() {

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  Serial.println("REVERSE");
}


// ---------------- LEFT ----------------

void left() {

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  Serial.println("LEFT");
}


// ---------------- RIGHT ----------------

void right() {

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  Serial.println("RIGHT");
}


// ---------------- STOP ----------------

void stop() {

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  Serial.println("STOP");
}

#endif