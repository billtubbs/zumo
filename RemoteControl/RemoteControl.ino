/* Adaptation of the example RemoteControl to control
Zumo 32U4 mobile robot from computer over USB serial.

  https://www.pololu.com/category/170/zumo-32u4-robot

See Python script robots.py for how to send commands
to the robot.
*/

#include <Wire.h>
#include <Zumo32U4.h>

LSM303 compass;
L3G gyro;

// Baud rate for serial communications
# define BAUD 9600

// String to send when identification requested by host
# define DEVICE_NAME "Zumo1"

Zumo32U4LCD lcd;
Zumo32U4ProximitySensors proxSensors;
Zumo32U4LineSensors lineSensors;
Zumo32U4Encoders encoders;
Zumo32U4Motors motors;
Zumo32U4Buzzer buzzer;
Zumo32U4ButtonA buttonA;

uint16_t lineSensorValues[5] = { 0, 0, 0, 0, 0 };
bool proxLeftActive;
bool proxFrontActive;
bool proxRightActive;

const char encoderErrorLeft[] PROGMEM = "!<c2";
const char encoderErrorRight[] PROGMEM = "!<e2";

int16_t speeds[] = {0, 100, 200, 300, 400};

void setup()
{
  Wire.begin();
  
  if (!compass.init())
  {
    // Failed to detect the compass.
    ledRed(1);
    while(1)
    {
      Serial.println(F("Failed to detect the compass."));
      delay(100);
    }
  }
  compass.enableDefault();

  if (!gyro.init())
  {
    // Failed to detect the gyro.
    ledRed(1);
    while(1)
    {
      Serial.println(F("Failed to detect gyro."));
      delay(100);
    }
  }
  gyro.enableDefault();
  
  // Initialize serial communication and set baud rate
  Serial.begin(BAUD);
  
  // Initialize sensors
  lineSensors.initThreeSensors();
  proxSensors.initThreeSensors();
  
  // Display message on LCD screen
  lcd.clear();
  lcd.print(F("Ready"));
}

char n, command[3] = "";
int16_t gear = 2;

void loop()
{
  static uint16_t lastSampleTime = 0;
  static uint8_t displayErrorLeftCountdown = 0;
  static uint8_t displayErrorRightCountdown = 0;
  
  int16_t countsLeft = encoders.getCountsLeft();
  int16_t countsRight = encoders.getCountsRight();
  int16_t leftSpeed, rightSpeed;

  // Check if data received on serial port
  // and if so read in next command (must be 2 chars)
  if (Serial.available()) { 
    command[0] = Serial.read();
    command[1] = Serial.read();
    
    // Display command on LCD screen
    lcd.clear();
    lcd.print(command);

    // Command List
    //
    // Actuator commands
    // 
    // 'N_'     - Buzzer (1=C, 2=D, 3=E)
    // 'F_'     - Forward at specified speed (0-4)
    //            (use 'F0' to stop moving)
    // 'B_'     - Backward at specified speed (0-4)
    // 'L_'     - Turn to left at specified speed (0-4)
    // 'R_'     - Turn to right at specified speed (0-4)
    // 'Y_'     - Yellow LED (1=on, 0=off)
    // 'Z_'     - Green LED (1=on, 0=off)
    // 'ID'     - Identification request (Zumo responds by sending its name)
    // 'SS____' - Set wheel speeds (4 chars represent leftSpeed, rightSpeed)
    //
    // Sensor read commands
    //
    // 'EL' - Get left wheel encoder reading (returns 16-bit integer)
    // 'ER' - Get right wheel encoder reading (returns 16-bit integer)
    // 'PF' - Get both values from front proximity sensor
    // 'PL' - Get value from left proximity sensor
    // 'PR' - Get value from right proximity sensor
    // 'BA' - Get battery voltage (returns millivolts as 16-bit integer)
    // 'CA' - Get compass readings, a.x, a.y, a.z (returns 3 16-bit integers)
    // 'CM' - Get compass readings, m.x, m.y, m.z (returns 3 16-bit integers)
    // 'GY' - Get angular velocities from gyro (returns 3 16-bit integers)
  
  switch(command[0])
    {
    
    case 'N':
      switch(command[1]) {
        
        case '1':
          buzzer.playNote(NOTE_C(4), 200, 15);
          break;
          
        case '2':
          buzzer.playNote(NOTE_D(4), 200, 15);
          break;

        case '3':
          buzzer.playNote(NOTE_E(4), 200, 15);
          break;
   
        case '0':
          buzzer.stopPlaying();
          break;
 
      }
      break;
 
    case 'F':
      if(command[1] >= '0' && command[1] <= '4') {
        gear = command[1] - 48;
        motors.setSpeeds(speeds[gear], speeds[gear]);
      }
      break;
  
    case 'B':
      if(command[1] >= '0' && command[1] <= '4') {
        gear = command[1] - 48;
        motors.setSpeeds(-speeds[gear], -speeds[gear]);
      }
      else if(command[1] >= 'A') {
        uint16_t batteryMillivolts = readBatteryMillivolts();
        Serial.write(batteryMillivolts >> 8);
        Serial.write(batteryMillivolts & 0xff);
      }
      break;
  
    case 'L':;
      if(command[1] >= '0' && command[1] <= '4') {
        gear = command[1] - 48;
        motors.setSpeeds(-speeds[gear], speeds[gear]);
      }
      break;
  
    case 'R':
      if(command[1] >= '0' && command[1] <= '4') {
        gear = command[1] - 48;
        motors.setSpeeds(speeds[gear], -speeds[gear]);
      }
      break;
 
    case 'Y':
      switch(command[1]) {
        case '1':
          ledYellow(1);
          break;
        
        case '0':
          ledYellow(0);
          break;
      }
      break;

    case 'Z':
      switch(command[1]) {
        case '1':
          ledGreen(1);
          break;
        
        case '0':
          ledGreen(0);
          break;
      }
      break;
  
    case 'I':
      if(command[1] == 'D') {
        lcd.gotoXY(0, 1);
        lcd.print(F(DEVICE_NAME));
        Serial.println(DEVICE_NAME);
      }
      break;
    
    case 'S':
      if(command[1] == 'S') {
        leftSpeed = int16_t((Serial.read() << 8) + Serial.read());
        rightSpeed = int16_t((Serial.read() << 8) + Serial.read());
        lcd.gotoXY(0, 1);
        lcd.print(leftSpeed);
        lcd.gotoXY(4, 1);
        lcd.print(rightSpeed);
        motors.setSpeeds(leftSpeed, rightSpeed);
      }
      break;

    case 'E':
      switch(command[1]) {
 
        case 'L':
        Serial.write(countsLeft >> 8);
        Serial.write(countsLeft & 0xff);
        break;
        
        case 'R':
        Serial.write(countsRight >> 8);
        Serial.write(countsRight & 0xff);
        break;
        
      }
      break;

    case 'P':
      switch(command[1]) {

        case 'F':
        Serial.write(proxSensors.countsFrontWithLeftLeds());
        Serial.write(proxSensors.countsFrontWithRightLeds());
        break;

        case 'L':
        Serial.write(proxSensors.countsLeftWithLeftLeds());
        break;

        case 'R':
        Serial.write(proxSensors.countsRightWithRightLeds());
        break;
      }
      break;
      
    case 'G':
      if(command[1] == 'Y') {
        Serial.write(gyro.g.x >> 8);
        Serial.write(gyro.g.x & 0xff);
        Serial.write(gyro.g.y >> 8);
        Serial.write(gyro.g.y & 0xff);
        Serial.write(gyro.g.z >> 8);
        Serial.write(gyro.g.z & 0xff);
      }
      break;
 
    case 'C':
      if(command[1] == 'A') {
        Serial.write(compass.a.x >> 8);
        Serial.write(compass.a.x & 0xff);
        Serial.write(compass.a.y >> 8);
        Serial.write(compass.a.y & 0xff);
        Serial.write(compass.a.z >> 8);
        Serial.write(compass.a.z & 0xff);
      }
      else if(command[1] == 'M') {
        Serial.write(compass.m.x >> 8);
        Serial.write(compass.m.x & 0xff);
        Serial.write(compass.m.y >> 8);
        Serial.write(compass.m.y & 0xff);
        Serial.write(compass.m.z >> 8);
        Serial.write(compass.m.z & 0xff);
      }
      break;

    }
  }

  // Periodically read sensors 
  if ((uint16_t)(millis() - lastSampleTime) >= 100)
  {
    lastSampleTime = millis();
    
    // Check for A Button pressed
    if(buttonA.isPressed()) {
      leftSpeed = 0;
      rightSpeed = 0;
      motors.setSpeeds(leftSpeed, rightSpeed);
    }
    
    compass.read();
    gyro.read();
    
    // Send IR pulses and read the proximity sensors.
    proxSensors.read();

    // Just read the proximity sensors without sending pulses.
    proxLeftActive = proxSensors.readBasicLeft();
    proxFrontActive = proxSensors.readBasicFront();
    proxRightActive = proxSensors.readBasicRight();

    countsLeft = encoders.getCountsLeft();
    countsRight = encoders.getCountsRight();

    bool errorLeft = encoders.checkErrorLeft();
    bool errorRight = encoders.checkErrorRight();

    if(encoders.checkErrorLeft())
    {
      // An error occurred on the left encoder channel.
      // Display it on the LCD for the next 10 iterations and
      // also beep.
      displayErrorLeftCountdown = 10;
      buzzer.playFromProgramSpace(encoderErrorLeft);
    }

    if(encoders.checkErrorRight())
    {
      // An error occurred on the left encoder channel.
      // Display it on the LCD for the next 10 iterations and
      // also beep.
      displayErrorRightCountdown = 10;
      buzzer.playFromProgramSpace(encoderErrorRight);
    }

    // Update the LCD with encoder counts and error info.
    //lcd.clear();
    //lcd.print(countsLeft);
    //lcd.gotoXY(0, 1);
    //lcd.print(countsRight);

    if (displayErrorLeftCountdown)
    {
      // Show an exclamation point on the first line to
      // indicate an error from the left encoder.
      lcd.gotoXY(7, 0);
      lcd.print('!');
      displayErrorLeftCountdown--;
    }

    if (displayErrorRightCountdown)
    {
      // Show an exclamation point on the second line to
      // indicate an error from the left encoder.
      lcd.gotoXY(7, 1);
      lcd.print('!');
      displayErrorRightCountdown--;
    }

    // Send the information to the serial monitor also.
    //snprintf_P(report, sizeof(report),
    //    PSTR("%6d %6d %1d %1d"),
    //    countsLeft, countsRight, errorLeft, errorRight);
    //Serial.println(report);
  }

}
