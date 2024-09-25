#include <Encoder.h>

#define L_MOTOR_IN1 10
#define L_MOTOR_IN2 11
#define L_MOTOR_PWM 12

#define R_MOTOR_IN1 7
#define R_MOTOR_IN2 8
#define R_MOTOR_PWM 13

#define MOTOR_STBY 9 // 모터 스탠바이 핀

#define L_ENC_A 2 // 왼쪽 모터 엔코더 핀 A
#define L_ENC_B 22 // 왼쪽 모터 엔코더 핀 B
#define R_ENC_A 3 // 오른쪽 모터 엔코더 핀 A
#define R_ENC_B 23 // 오른쪽 모터 엔코더 핀 B

Encoder leftEncoder(L_ENC_A, L_ENC_B);
Encoder rightEncoder(R_ENC_A, R_ENC_B);

long leftEncoderValue = 0;
long rightEncoderValue = 0;
char motorState = 'S';

void setup()
{
  pinMode(L_MOTOR_IN1, OUTPUT);
  pinMode(L_MOTOR_IN2, OUTPUT);
  pinMode(L_MOTOR_PWM, OUTPUT);

  pinMode(R_MOTOR_IN1, OUTPUT);
  pinMode(R_MOTOR_IN2, OUTPUT);
  pinMode(R_MOTOR_PWM, OUTPUT);

  pinMode(MOTOR_STBY, OUTPUT);
  digitalWrite(MOTOR_STBY, HIGH);

  Serial.begin(9600);
}

void loop()
{
    if (Serial.available() > 0)
    {
        motorState = Serial.read();
    }

    if (motorState == 'F')
    {
        digitalWrite(L_MOTOR_IN1, LOW);
        digitalWrite(L_MOTOR_IN2, HIGH);
        analogWrite(L_MOTOR_PWM, 10);

        digitalWrite(R_MOTOR_IN1, HIGH);
        digitalWrite(R_MOTOR_IN2, LOW);
        analogWrite(R_MOTOR_PWM, 10);
    }
    else if (motorState == 'S')
    {
        analogWrite(L_MOTOR_PWM, 0);
        analogWrite(R_MOTOR_PWM, 0);
    }

    leftEncoderValue = leftEncoder.read();
    rightEncoderValue = rightEncoder.read();

    Serial.print("L: ");
    Serial.print(leftEncoderValue);
    Serial.print(" R: ");
    Serial.println(rightEncoderValue);

    delay(100);
}