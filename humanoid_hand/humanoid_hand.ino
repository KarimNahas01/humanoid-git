#include <Servo.h>

const int N = 5;
const int fingerComplete[N] = {2100, 2100, 1800, 1800, 1800};
const float fingerRatioUp[N] = {0.7, 0.85, 0.82, 0.87, 0.78};
const int vStop[N] = {89, 89, 90, 88, 87};
const int vClose = 180;
const int vOpen = 0;
const int pins[N] = {3, 5, 6, 9, 10};

String inStr = "";

int servoValues[N] = {0,0,0,0,0};
int servoDelays[N];
byte indexArray[N];

Servo servos[N];


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  for(int i =0; i < N; i++){
    servos[i].attach(pins[i]);
  }

  // TODO: Calibrate hand everytime arduino restarts? Closing hand fully no matter position and then opening it.

  stopFingers();

  Serial.print("Setup complete");

}

void loop() {
  while (Serial.available() > 0) {

    inStr = Serial.readStringUntil('\n');
    inStr.trim();

    decodeInput(inStr);

    Serial.print(inStr);
    Serial.print("**");

    moveFingers();
  }

}

void decodeInput(String inputString){
  int percentValues[N];
  float ratio;
  int newPos;
  for (int i = 0; i < N; i++) {
    String num = inputString.substring(2*i, 2*i+2);
    percentValues[i] = num.toInt();

    Serial.print("Finger ");
    Serial.print(i);
    Serial.print(" = ");
    Serial.print(percentValues[i]);
    Serial.print("\t");

    //Serial.print(" Complete ");
    //Serial.print(fingerComplete[i]);

    // Converting the percentage values to servo values
    ratio = percentValues[i] / 99.0;

    Serial.print(" Ratio ");
    Serial.print(ratio);

    newPos = int(fingerComplete[i] * ratio);

    Serial.print(" NewPos ");
    Serial.print(newPos);
    //Serial.print(" OldPos ");
    //Serial.print(servoValues[i]);

    float servoDelay = newPos - servoValues[i];
    if (servoDelay < 0){
      servoDelay = int(servoDelay * fingerRatioUp[i]);
    }

    //Serial.print(" Delay ");
    //Serial.print(servoDelay);

    servoDelays[i] = servoDelay;
    servoValues[i] = newPos;
    
  }
  
}


void sortIndexes(int * data){
  byte i, j, k, flg;
  indexArray[ 0 ] = 0;
  for ( i = 1; i < N; i++ )
  {
    flg = 0;
    for ( j = 0; j < i; j++ )
    {
      if ( abs(data[ i ]) < abs(data[ indexArray[ j ]]) ) // new number is less than indexed value
      {
        for ( k = i; k > j; k-- ) // move finished indexes up
        {
          indexArray[ k ] = indexArray[ k - 1 ];
        }
        indexArray[ j ] = i;
        j = i;
        flg = 1;
      }
      if ( flg == 0 )
      {
        indexArray[ i ] = i;
      }
    }
      
  }

}

void stopFingers(){
  for(int i =0; i < N; i++){
    servos[i].write(vStop[i]);
  }
}

void moveFingers(){

  int val;
  int timeDelayed = 0;
  int idFinger;
  
  sortIndexes(servoDelays);

  // Starting fingers
  for (int i = 0; i < N; i++){
    idFinger = indexArray[i];
    val = servoDelays[idFinger];
    
    if (val > 0){
      // Close fingeridFinger
      Serial.print("\tClose finger ");
      servos[idFinger].write(vClose);
    }
    else if (val < 0){
      // Open finger
      Serial.print("\tOpen finger ");
      servos[idFinger].write(vOpen);
    }
    else{
      // Dont activate servo
      Serial.print("\tStop finger ");
    }
    Serial.print(idFinger);

  }

  // Stopping fingers
  for (int i = 0; i < N; i++){
    idFinger = indexArray[i]; 
    
    val = abs(servoDelays[idFinger]);
    if (val > 0){
      // Delay and stop servo
      delay(val - timeDelayed);
      servos[idFinger].write(vStop[idFinger]);
      Serial.print("\tStop finger ");
      Serial.print(idFinger);
      
    }
    
    timeDelayed = abs(val);
    Serial.print(" Time Delayed: ");
    Serial.print(timeDelayed);
  }
  Serial.print("**");
}
