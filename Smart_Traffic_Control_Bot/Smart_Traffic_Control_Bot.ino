#include <DHT.h>
#include <SoftwareSerial.h>

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define TRIG 2
#define ECHO 3
#define RED_LED 5
#define YELLOW_LED 6
#define GREEN_LED 7
#define GAS_SENSOR A0

SoftwareSerial espSerial(11, 10); // RX, TX

long duration;
int distance;
int redTime;
float temp;
int gasValue;

void setup() {
  Serial.begin(9600);
  espSerial.begin(9600);
  dht.begin();
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
}

void loop() {
  // Measure distance
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  duration = pulseIn(ECHO, HIGH);
  distance = duration * 0.034 / 2;

  // Red light time logic
  redTime = (distance < 50) ? 30 : 10;

  // Read temperature
  temp = dht.readTemperature();
  if (isnan(temp)) temp = 0;

  // Read gas value
  gasValue = analogRead(GAS_SENSOR);

  // Simulate signal
  digitalWrite(RED_LED, HIGH);
  digitalWrite(GREEN_LED, LOW);
  delay(redTime * 1000);

  digitalWrite(RED_LED, LOW);
  digitalWrite(YELLOW_LED, HIGH);
  delay(2000);
  digitalWrite(YELLOW_LED, LOW);

  digitalWrite(GREEN_LED, HIGH);
  delay(10000);
  digitalWrite(GREEN_LED, LOW);

  // Send sensor data to ESP8266
  Serial.print("TEMP:");
  Serial.print(temp);
  Serial.print(",TIME:");
  Serial.print(redTime);
  Serial.print(",GAS:");
  Serial.print(gasValue);
  Serial.print(",DIST:");
  Serial.print(distance);
  Serial.println();
}
