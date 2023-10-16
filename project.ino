#include <Servo.h>
Servo servo1; //thumb -- Closing 1500ms (1.5s) delay, Coming up with 1500*0.9
Servo servo2; //index finger -- Closing 1750ms (1.5s) delay, Coming up with 1750*0.9
Servo servo3; //middle finger -- Closing 1500ms (1.5s) delay, Coming up with 1500*0.9
Servo servo4; //ring finger -- Closing 1500ms (1.5s) delay, Coming up with 1500*0.9
Servo servo5; //little finger -- Closing 1500ms (1.5s) delay, Coming up with 1500*0.9

int e8 = 88;
int e9 = 89;
int nty = 90;

float ratio = 0.9;

void setup() {
  // put your setup code here, to run once:

  //attach servos to PWM pins
  servo1.attach(3); //thumb servo on pin 3
  servo2.attach(5); //index servo on pin 5
  servo3.attach(6); //middle servo on pin 6
  servo4.attach(9); //ring servo on pin 9
  servo5.attach(10); // little servo on pin 10

}

void thumb(){ //done
  servo1.write(0);
  delay(2000);
  servo1.write(90);
  delay(3000);
  servo1.write(180);
  delay(2000);
  servo1.write(90);
  delay(3000);
  //servo1.write(90); maybe?
}

void index(){ //done
  servo2.write(0);
  delay(3000);
  servo2.write(90);
  delay(3000);
  servo2.write(180);
  delay(3000);
  servo2.write(90);
  delay(3000);
  //servo2.write(90); maybe?
}

void middle(){
  servo3.write(0);
  delay(3000);
  servo3.write(90);
  delay(3000);
  servo3.write(180);
  delay(3000);
  servo3.write(90);
  delay(3000);
  //servo3.write(90); maybe?
}

void ring(){
  servo4.write(0);
  delay(3000);
  servo4.write(90);
  delay(3000);
  servo4.write(180);
  delay(3000);
  servo4.write(90);
  delay(3000);
  //servo4.write(90); maybe?
}

void little(){ // change 
  servo5.write(0);
  delay(3000);
  servo5.write(90);
  delay(3000);
  servo5.write(180);
  delay(3000);
  servo5.write(90);
  delay(3000);
  //servo5.write(90); maybe?
}

void loop() {
  // put your main code here, to run repeatedly:
  servo1.write(e9);
  servo2.write(e9);
  servo3.write(nty);
  servo4.write(e9);
  servo5.write(e8);

  servo2.write(180);
  servo3.write(180);
  servo4.write(180);
  servo5.write(180); 
  delay(2000);       // closing
  servo2.write(e9);
  servo3.write(nty);
  servo4.write(e9);
  servo5.write(e8);
  delay(3000);       // waiting
  servo2.write(0);
  servo3.write(0);
  servo4.write(0);
  servo5.write(0);
  delay(2000*0.85);
  servo3.write(nty);
  delay(2000*ratio - 2000*0.85); // Coming up
  servo2.write(e9);
  servo4.write(e9);
  servo5.write(e8);
  delay(3000);


  //servo1.write(0);
  //servo2.write(0);
  //servo3.write(0);
  //servo4.write(0);
  //servo5.write(0);
  //delay(1000);
  //servo1.write(90);
  //servo2.write(90);
  //servo3.write(90);
  //servo4.write(90);
  //servo5.write(90);
  //delay(1000);

  
}








