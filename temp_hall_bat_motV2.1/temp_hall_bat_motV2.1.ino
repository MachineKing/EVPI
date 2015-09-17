#include <OneWire.h>
#include <SPI.h>
#define spi_speed 12000000
#define bat_cs 49
#define mot_cs 47
#define bat_sample_size 10
#define mot_sample_size 20
uint8_t data_high_v[mot_sample_size];
uint8_t data_low_v[mot_sample_size];
uint8_t data_high_i[mot_sample_size];
uint8_t data_low_i[mot_sample_size];
byte data=0;
unsigned int adc_v;
unsigned int adc_i;

#define hall_one 8


OneWire  ds(13);  // on pin 13 (a 4.7K resistor is necessary)

  byte bms_addr[8]={0x28, 0xF9, 0xE8, 0x03, 0x05, 0x00, 0x00, 0xA3};
  byte bat_addr[8]={0x28, 0x3E, 0x95, 0x03, 0x05, 0x00, 0x00, 0x38};
  byte motor_addr[8]={0x28, 0x45, 0x2C, 0x04, 0x05, 0x00, 0x00, 0x62};
  byte inSerial;
void setup(void) {
  
    // set the slaveSelectPins as an outputs:
  pinMode (bat_cs, OUTPUT);
  pinMode (mot_cs, OUTPUT);
  digitalWrite(mot_cs, HIGH);
  digitalWrite(bat_cs, HIGH);
  // initialize SPI:
  SPI.begin();//Transaction(SPISettings(spi_speed, MSBFIRST, SPI_MODE3)); 
  SPI.setClockDivider(SPI_CLOCK_DIV2); 
  Serial.begin(115200);
    pinMode(hall_one, INPUT_PULLUP);//the hall effect sensor is open drain
}

void loop(void) {
  start_temp_conversion(); //ds18b20 takes up to 1second to take a temperature reading
  read_rpm();
  read_bat();
  send_power('b');
  read_motor();
  send_power('m');
  delay(1000);
  read_temp(); //read the temperatures
  /*
if(Serial.available()){
  inSerial=Serial.read();
  if(inSerial==0x41){
   read_temp(); 
  }
  else if(inSerial==0x52){
    read_rpm();
  }
}*/
}
//==========================================================================================
//==========================================================================================
void start_temp_conversion(){
  ds.reset();
  ds.select(bms_addr);
  ds.write(0x44, 1);        // start conversion, with parasite power on at the end 
  ds.reset();
   ds.select(bat_addr);
  ds.write(0x44, 1);        // start conversion, with parasite power on at the end 
  ds.reset();
    ds.select(motor_addr);
  ds.write(0x44, 1);        // start conversion, with parasite power on at the end 
  return;
}
void read_temp(){
  byte i;
  byte present = 0;
  byte type_s;
  byte data[12];
  float T1, T2, T3;
  // we might do a ds.depower() here, but the reset will take care of it.
  
  present = ds.reset();
  ds.select(bms_addr);    
  ds.write(0xBE);         // Read Scratchpad

  for ( i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();
  }

  // Convert the data to actual temperature
  // because the result is a 16 bit signed integer, it should
  // be stored to an "int16_t" type, which is always 16 bits
  // even when compiled on a 32 bit processor.
  int16_t raw = (data[1] << 8) | data[0];
  if (type_s) {
    raw = raw << 3; // 9 bit resolution default
    if (data[7] == 0x10) {
      // "count remain" gives full 12 bit resolution
      raw = (raw & 0xFFF0) + 12 - data[6];
    }
  } else {
    byte cfg = (data[4] & 0x60);
    // at lower res, the low bits are undefined, so let's zero them
    if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
    else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
    else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
    //// default is 12 bit resolution, 750 ms conversion time
  }
  T1 = (float)raw / 16.0;
  
    present = ds.reset();
  ds.select(bat_addr);    
  ds.write(0xBE);         // Read Scratchpad
  for ( i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();}
  raw = (data[1] << 8) | data[0];
  if (type_s) {
    raw = raw << 3;
    if (data[7] == 0x10) {
      raw = (raw & 0xFFF0) + 12 - data[6];}
  } else {
    byte cfg = (data[4] & 0x60);
    if (cfg == 0x00) raw = raw & ~7;
    else if (cfg == 0x20) raw = raw & ~3;
    else if (cfg == 0x40) raw = raw & ~1;
  }
    T2 = (float)raw / 16.0;
    
   present = ds.reset();
  ds.select(motor_addr);    
  ds.write(0xBE);         // Read Scratchpad
  for ( i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();}
  raw = (data[1] << 8) | data[0];
  if (type_s) {
    raw = raw << 3;
    if (data[7] == 0x10) {
      raw = (raw & 0xFFF0) + 12 - data[6];}
  } else {
    byte cfg = (data[4] & 0x60);
    if (cfg == 0x00) raw = raw & ~7;
    else if (cfg == 0x20) raw = raw & ~3;
    else if (cfg == 0x40) raw = raw & ~1;
  }
    T3 = (float)raw / 16.0;
  Serial.println("temperatures = ");
  Serial.print(T2);
  Serial.print(" ");
  Serial.print(T1);
  Serial.print(" ");
  Serial.println(T3);
}
//==========================================================================================
//==========================================================================================
void read_rpm(){
  float rpm = 0;
  unsigned int previous=0;
  unsigned int current=0;
  unsigned int time=0;
  //commented for testing without motor
        previous=millis();
    while(digitalRead(hall_one)==1 && time<=1000){//wait for magnet to trigger the hall
    current=millis();
      time=current-previous;
    }
    while(digitalRead(hall_one)==0 && time<=1000){//wait for magnet to pass
    current=millis();
    time=current-previous;
    }
    while(digitalRead(hall_one)==1 && time<=1000){//wait for magnet to trigger the hall again. (with 1second timeout - 60rpm)
      current=millis();
      time=current-previous;
    }
    rpm =60000/time;
    Serial.println("rpm = ");
   // Serial.println(time);
    Serial.print(rpm);
    Serial.print(" ");
    Serial.print(rpm);
    Serial.print(" ");
    Serial.print(rpm);
    Serial.println(" ");
  
}
//==========================================================================================
//==========================================================================================
void read_motor(){
  char cmd1 = B00000001;
  char cmdi = B10100000;
  char cmdv = B11100000;
  uint8_t temp;
   SPI.begin();
  SPI.setClockDivider(SPI_CLOCK_DIV2);
  
    //take and discard 20 readings
    for(int i=0; i<20; i++){
    digitalWrite(mot_cs, LOW);
    temp=SPI.transfer(cmd1); //send start bit
    data_high_v[0]=SPI.transfer(cmdv);//send format of data output and receive top 4 bits
    data_low_v[0]=SPI.transfer(0x00);//receive bottom 8 bits
    digitalWrite(mot_cs, HIGH);
    delayMicroseconds(1);
    digitalWrite(mot_cs, LOW);
    temp=SPI.transfer(cmd1); //send start bit
    data_high_i[0]=SPI.transfer(cmdi);//send format of data output and receive top 4 bits
    data_low_i[0]=SPI.transfer(0x00);//receive bottom 8 bits
    digitalWrite(mot_cs, HIGH);
    delayMicroseconds(10);
  }
  
  
  
  for(int i=0; i<mot_sample_size; i++){
    digitalWrite(mot_cs, LOW);
    temp=SPI.transfer(cmd1); //send start bit
    data_high_v[i]=SPI.transfer(cmdv);//send format of data output and receive top 4 bits
    data_low_v[i]=SPI.transfer(0x00);//receive bottom 8 bits
    digitalWrite(mot_cs, HIGH);
    delayMicroseconds(1);
    digitalWrite(mot_cs, LOW);
    temp=SPI.transfer(cmd1); //send start bit
    data_high_i[i]=SPI.transfer(cmdi);//send format of data output and receive top 4 bits
    data_low_i[i]=SPI.transfer(0x00);//receive bottom 8 bits
    digitalWrite(mot_cs, HIGH);
    delayMicroseconds(9);
  }
    SPI.end();
  return;  
}
//==========================================================================================
//==========================================================================================
void send_power(char element){
  unsigned int current_time=0;
  unsigned int previous_time=0;
  
  if(element == 0x62){
    Serial.print("battery voltage = ");
  }
  else if(element == 0x6d){
     Serial.print("motor voltage = ");
  }
  Serial.print("\n");
  for(int c=0; c<mot_sample_size; c++){
    data_high_v[c]=data_high_v[c] & 0x0f; //clear the don;t care bits in the top 4 msb byte
    data_high_i[c]=data_high_i[c] & 0x0f; //clear the don;t care bits in the top 4 msb byte
    adc_v=data_low_v[c]+(data_high_v[c]*255); //combine the msb and lsb bytes
    adc_i=data_low_i[c]+(data_high_i[c]*255); //combine the msb and lsb bytes
    Serial.print(adc_v);
    Serial.print("\n");
  }
  Serial.print("end");
  Serial.print("\n");
previous_time=millis(); 
while(!Serial.available() && current_time-previous_time<250){ //wait for acknowledge from pi
current_time=millis();
}
  
      if(element == 0x62){
    Serial.print("battery current = ");
  }
  else if(element == 0x6d){
     Serial.print("motor current = ");
  }
  Serial.print("\n");
  for(int c=0; c<mot_sample_size; c++){
    data_high_i[c]=data_high_i[c] & 0x0f; //clear the don;t care bits in the top 4 msb byte
    adc_i=data_low_i[c]+(data_high_i[c]*255); //combine the msb and lsb bytes
    Serial.print(adc_i);
    Serial.print("\n");
  }
  Serial.print("end");
  Serial.print("\n");
  previous_time=millis();
while(!Serial.available() && current_time-previous_time<250){ //wait for acknowledge from pi
current_time=millis();
}
 Serial.read();  
}
//==========================================================================================
//==========================================================================================
void read_bat(){
  char cmd1 = B00000001;
  char cmdv = B11100000;
  char cmdi = B10100000;
  uint8_t temp;
   SPI.begin();
  SPI.setClockDivider(SPI_CLOCK_DIV2);
  //take and discard 20 readings
    for(int i=0; i<20; i++){
    digitalWrite(bat_cs, LOW);
    temp=SPI.transfer(cmd1); //send start bit
    data_high_v[0]=SPI.transfer(cmdv);//send format of data output and receive top 4 bits
    data_low_v[0]=SPI.transfer(0x00);//receive bottom 8 bits
    digitalWrite(bat_cs, HIGH);
    delayMicroseconds(1);
    digitalWrite(bat_cs, LOW);
    temp=SPI.transfer(cmd1); //send start bit
    data_high_i[0]=SPI.transfer(cmdi);//send format of data output and receive top 4 bits
    data_low_i[0]=SPI.transfer(0x00);//receive bottom 8 bits
    digitalWrite(bat_cs, HIGH);
    delayMicroseconds(10);
  }
  
  for(int i=0; i<mot_sample_size; i++){
    digitalWrite(bat_cs, LOW);
    temp=SPI.transfer(cmd1); //send start bit
    data_high_v[i]=SPI.transfer(cmdv);//send format of data output and receive top 4 bits
    data_low_v[i]=SPI.transfer(0x00);//receive bottom 8 bits
    digitalWrite(bat_cs, HIGH);
    delayMicroseconds(1);
    digitalWrite(bat_cs, LOW);
    temp=SPI.transfer(cmd1); //send start bit
    data_high_i[i]=SPI.transfer(cmdi);//send format of data output and receive top 4 bits
    data_low_i[i]=SPI.transfer(0x00);//receive bottom 8 bits
    digitalWrite(bat_cs, HIGH);
    delayMicroseconds(9);
  }
    SPI.end();
  return;  
}
