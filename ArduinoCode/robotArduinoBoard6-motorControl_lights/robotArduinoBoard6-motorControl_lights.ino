char buffer[12];

int speed1 = 0;
int speed2 = 0;
int getSensors = 0;
int led_on = 0;
int index = 0;

//serial read and parsing modified from https://arduino.stackexchange.com/questions/49986/read-from-serial-monitor-till-timeout
void setup() {
  // put your setup code here, to run once:
Serial.begin(57600);
pinMode(LED_BUILTIN, OUTPUT);

// initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(2, OUTPUT); //led driver
  pinMode(3, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(9, OUTPUT);

  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(2, LOW); 
  fullStop();  
}

void fullStop()
  {
  analogWrite(3, 0); 
  analogWrite(5, 0); 
  analogWrite(6, 0); 
  analogWrite(9, 0); 

  //turn off headlights
  digitalWrite(2, LOW);
  }

  void setMotors(int speed1, int speed2)
  {
    //right track forward
    if (speed2 >= 0)
      {
      analogWrite(5, 0);
      analogWrite(9, speed2);
      }

    //right track reverse
    if (speed2 < 0)
      {
      analogWrite(9, 0);
      analogWrite(5, speed2 * -1);
      }
      
       //left track forward
    if (speed1 >= 0)
      {
      analogWrite(3, 0);
      analogWrite(6, speed1);
      }
      
    //left track reverse
    if (speed1 < 0)
      {
      analogWrite(6, 0);
      analogWrite(3, speed1 * -1);
      }    
  }

String getValue(String data, char separator, int index)
{
    //returns substring based on index and separators
    //from 
    //https://arduino.stackexchange.com/questions/1013/how-do-i-split-an-incoming-string
    
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;
    
    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

int parseCommandString()
{

//Serial.println(buffer);  
  
if (buffer[0] != 'C')
  {
    //Serial.println("First char not C, invalid command");  
    return 0; 
  }
  
//no need to check for E, that's how we got called. We need to check for size as we parse though

String s_speed1 = getValue(buffer, ':', 1);
String s_speed2 = getValue(buffer, ':', 2);
String s_getSensors = getValue(buffer, ':', 3);
String s_led_on = getValue(buffer, ':', 4);

//if the parser didn't return a string for any of these, we have an invalid line

if (s_speed1.length() < 1)
  return 0;

  if (s_speed2.length() < 1)
  return 0;

if (s_getSensors.length() < 1)
  return 0;

if (s_led_on.length() < 1)
  return 0;
  
speed1 = s_speed1.toInt();
speed2 = s_speed2.toInt();
getSensors = s_getSensors.toInt();
led_on = s_led_on.toInt();
return 1;
}

float getBattVoltage()
{
 int val;
  int inval = 0;
  float battVoltage = 0.0;
  
//batt voltage is analog reading * 6.494
  inval = analogRead(A0);  // read the input pin
  //multiply by appropriate value for the voltage divider 
  battVoltage = ((5.0 * inval) / 1024.0) * 6.494; 
  return battVoltage;         

}

void loop() {

//since loop() runs continuously, declare local variables as static so that won't get reset it time it runs
static unsigned long timeLastInput = 0;
static unsigned long now = 0;


static char incomingByte = 0; 
static int incomingInt = 0;
static int valid = 0;   //replace with boolean
String outputStr = "";
 
//expects strings of the form:
//C:80:75:1:0:E

//C indicates start of command
//first 2 digits are motor speeds, positive or negative to indicate direction
//third is binary - should I return sensor values, 0 or 1
//third is binary - headlights on or off, 0 or 1
//ends with E, easier than detecting newline
  
if (Serial.available() > 0)
  {
    //runs every time a byte is received on the serial line
    
    delay (5);
    
    //begin nonblocking byte by byte read
    incomingByte = Serial.read();
    
    if (incomingByte != 'E') 
      {
        //ignore any newlines - we only want characters, commas, or numbers
        if ( isDigit(incomingByte) || isAlpha(incomingByte) || isPunct(incomingByte) )
          {
            buffer[index] = incomingByte;
            index ++;          
          }
      }  
      else
      {
      buffer[index] = '\0'; //null character

      valid = parseCommandString();
      index = 0;

    //Serial.println(speed1, DEC);
    //Serial.println(speed2, DEC);
    //Serial.println(getSensors, DEC);
    //Serial.println(led_on, DEC);
      
      if (valid == 1)
        {
          digitalWrite(LED_BUILTIN, LOW);
         
          now = millis();
          timeLastInput = now;
          setMotors(speed1, speed2);

          if (led_on)
            digitalWrite(2, HIGH);
          else
            digitalWrite(2, LOW);

          outputStr = "OK:";
          
          if (getSensors == 1)
            { 
              outputStr = outputStr + String(getBattVoltage());
              outputStr = outputStr + ":";
            }
            
            Serial.println(outputStr);
        }
       else
         {
           Serial.println("INVALID");
         }
           
      }
      
  }  
    
    //end nonblocking byte by byte read

 //if too much time has passed since reset of watchdog, do something      

 if (millis() - timeLastInput > 200)
    {
      digitalWrite(LED_BUILTIN, HIGH);
      fullStop();
    }
    
    
}
 
 
 
