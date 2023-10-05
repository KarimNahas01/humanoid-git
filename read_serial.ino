void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

}

int servoValues[5] = {0,0,0,0,0};
String inStr = "";

void loop() {
  // put your main code here, to run repeatedly:
  while (Serial.available() == 0) {} // Wait for data
  inStr = Serial.readString();
  inStr.trim();

  int percentValues[5];
  for (int i = 0; i < 5; i++) {
    String num = inStr.substring(2*i, 2*i+1);
    percentValues[i] = num.toInt();
  }

  // Now we need to convert the percentage values to servo values
}
