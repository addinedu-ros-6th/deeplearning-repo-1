int startSensor = 8;    // Door 센서의 신호핀 연결
int endSensor = 7;    // Card 센서의 신호핀 연결
int start = 0;
int end = 0;
unsigned long startTime = 0;
unsigned long endTime = 0;
unsigned long currentTime = 0;
int speed = 0;
int startCheck = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); 
  pinMode(startSensor, INPUT);  
  pinMode(endSensor, INPUT);  
}

 

void loop() {
  // put your main code here, to run repeatedly:

  char send_buffer[16];

  if (digitalRead(startSensor) == 1 && startCheck == 0)
  {
    Serial.print("startSensor : ");
    Serial.print(digitalRead(startSensor));
    Serial.println();
    startTime = millis();
    startCheck = 1;

  }

   if (digitalRead(endSensor) == 1 && startCheck == 1)
  {
    Serial.print("endSensor :   ");
    Serial.println(digitalRead(endSensor));
    currentTime = millis();
    endTime = (currentTime - startTime)/1000;
    Serial.print("time :      ");
    Serial.println(endTime);
    Serial.println();  
    speed = 15 / endTime;
    Serial.print("speed  :      ");
    Serial.print(speed);
    Serial.print("cm/s");
    Serial.println();  
    startCheck = 0;
  }

  Serial.println(speed);
  delay(100);
  
}
