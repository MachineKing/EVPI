
/*
Author: Jeran

bq77pl900 I2C read and write

*/


#include <Wire.h>

#define SCL_PIN 1 //pin 9 on uno
#define SCL_PORT PORTB 
#define SDA_PIN 2 //pin 10 on uno
#define SDA_PORT PORTB 
#define I2C_SLOWMODE 1 

#define on_off 6
#define Vin A1
#define Iin A0
#define AREF 3.3 //measure and tune

#include <SoftI2CMaster.h>

//BQ77PL900 configuration registers
#define output_control 0x01
#define oc_val 0x00

#define state_control 0x02
#define sc_val 0x42 //set VGAIN = 0.2 (VREF=1.2V) Host mode enabled

#define function_control 0x03
#define fc_val 0x01   //enable VAEN it has to be enabled before entering calibration (presumably to let the comparators "wamr up") 

#define cell_balance 0x04
#define cb_val 0x00

#define cell_sel 0x05
#define cs_val 0x00

#define ov_cfg 0x06
#define ov_cfg_val 0x01 //set overvoltage to 4.2V

#define uv_cfg 0x07
#define uv_val 0x06 //hysterisis set to 0.2V cell undervoltage set to 2V thus undervoltage recovery will occur at 2.2V

#define ov_delay 0x09
#define ov_val 0x00 //disable cell balancing

#define pladdr 0x20

#define balance_point 0.7 //the difference between average cell value and actual at which balancing occurs

byte STATUS=0;
float Kact, Vout_0V;
float IA_offset=1.186;
float cv[10];
float Iout;
int mode = 1;
volatile boolean pwr_state = false; //BMS output state (true = on)

unsigned int previous_millis=0;
unsigned int current_millis=0;


void setup() {
  
  //Set up pins
  pinMode(on_off, INPUT_PULLUP);
  //attachInterrupt(0, pwr_toggle, FALLING);
  
  analogReference(EXTERNAL);
  for(int k=0; k<10; k++){
    analogRead(Vin);
    analogRead(Iin);}

    
    Serial.begin(9600);
  if (!i2c_init()){ 
    Serial.println("Initialization error. SDA or SCL are low");}
  else{
    Serial.println("I2C started");}
    if(pl900_setup()){
  Serial.println("BQ77PL900 Succesfully setup");}
  else{Serial.println("UNSUCCESFUL check cfg registers");}
      
    status_reset();
    
    pack_scan();
    Serial.print("status bits:  ");
   Serial.println(readi2c(0x00));
   Serial.println("voltage calibration");
   delay(500);
   vout_cal();
   delay(100);
   vout_cal();
   //iout_cal();
   Serial.print("IA OFFSET =   ");
   Serial.println(IA_offset);

}
//===========================================================================================================
//==============================================MAIN========================================================
//===========================================================================================================
void loop() {
  //writei2c(output_control, 0x02); //switch on DSG fet (PAck + output on);
//Serial.println(analogRead(Vin));
//status_reset();

if(digitalRead(on_off)==LOW){
  writei2c(output_control, 0x04); //switch on CHG fet switch off DSG (PAck + input on)
  writei2c(ov_delay, 0x80); //switch on cell balancing
  writei2c(state_control, 0x40); //switch to standalone mode
  mode = 0;
}
else{
  writei2c(output_control, 0x02); //switch OFF CHG and switch on DSG fet (PAck + output on)
  writei2c(ov_delay, 0x00); //switch off cell balancing
  writei2c(state_control, 0x42); //switch to host mode
  mode = 1;
}

  if(mode == 1){  
    current_millis=millis();
    if((current_millis-previous_millis)>3999){

        Serial.print("status bits:  ");
        Serial.println(readi2c(0x00), BIN);
          pack_scan();
          Serial.println("cell voltages = ");
          for(byte i=0; i<10; i++){
             Serial.print(cv[i]);
             Serial.print(" ");
          }
        Serial.println("");
        Serial.println("Pack Current = ");
        Serial.println(Iout);
      
    previous_millis=current_millis;
    }
  }
}


//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//,asjkkkkkkkkkkkkkkkkkkkkkkkkkkkkkaskjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj
//,asjkkkkkkkkkkkkkkkkkkkkkkkkkkkkkaskjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj
//,asjkkkkkkkkkkkkkkkkkkkkkkkkkkkkkaskjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj
//,asjkkkkkkkkkkkkkkkkkkkkkkkkkkkkkaskjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj
//,asjkkkkkkkkkkkkkkkkkkkkkkkkkkkkkaskjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

void balance(){
  int average_cell=0;
  byte cel_bal=0;
  for(int i = 0; i<10; i++){
    average_cell+=cv[i];
  }
  average_cell = average_cell/10;
  
  for(int i =1; i<9; i++){
     if(cv[i]-average_cell>=balance_point){   
           bitSet(cel_bal, i);
           Serial.println(i);
           writei2c(cell_balance, cel_bal);
           writei2c(ov_delay, 0x80); //switch on cell balancing
           break;
         }   
  }
  
  Serial.println(cel_bal, BIN);
  
}


//======================================================================================
//=============================PL900 Communications=====================================
//======================================================================================
boolean writei2c(byte reg_addr, byte data){
if (!i2c_start(pladdr | I2C_WRITE)) return false;
  if (!i2c_write(reg_addr)) return false;
  if (!i2c_write(data)) return false;
  i2c_stop();
  return true;
}

//======================================================================================

byte readi2c(byte reg_addr){
if (!i2c_start(pladdr | I2C_WRITE)) return false;
  if (!i2c_write(reg_addr)) return false;
  if (!i2c_rep_start(pladdr | I2C_READ)) return false;
    byte data =i2c_read(true);
  i2c_stop();

  //Serial.println(data, BIN);
  return data;
}
//====================================================================================
//================================PL900 functions=====================================
//====================================================================================
void pack_scan(){
  float filter_cv[10]={0,0,0,0,0,0,0,0,0,0};
  float I_calc;
  float avg_i=0;
 
  writei2c(ov_delay, 0x00); //switch off cell balancing in order to measure the cells
  writei2c(cell_balance, 0x00); //switch off cell balance some more
  delay(10);  
  writei2c(function_control, 0x01); //set VAEN bit
  delay(5);
   
      for(byte cell=0; cell<10; cell++){
          writei2c(cell_sel, cell);
          delay(5);
          filter_cv[cell]+=float((Vout_0V-analogRead(Vin)*(AREF/1023.0))/Kact); //
      }
  writei2c(function_control, 0x00); //clear VAEN bit
  delay(2);
  writei2c(function_control, 0x02); //set IAEN bit
  delay(100);
  for(int h=0; h<10; h++){
    avg_i+=float(analogRead(Iin)*(AREF/1023.0));
    delay(10);
  }
  I_calc=avg_i/10;
  Iout = (I_calc-IA_offset)/(10*0.001);  
  
  writei2c(function_control, 0x00); //clear IAEN bit  
  
   for(byte cell=0; cell<10; cell++){
      cv[cell]=filter_cv[cell];
    }
  delay(3); 
  writei2c(ov_delay, 0x80); //switch on cell balancing

return; 
}
//=====================================================================================
float battery_voltage(){
  
    float filter_bat=0;
    float bat_v;
    
      writei2c(ov_delay, 0x00); //switch off cell balancing in order to measure the cells
      //writei2c(function_control, 0x10); //set bat voltage output
      writei2c(function_control, 0x11); //enable VAEN and bat voltage output
    
  for(byte cell=0; cell<10; cell++){
    delay(5);
    filter_bat+= analogRead(Vin)*(AREF/1023.0)*50;//float((Vout_0V-analogRead(Vin)*(AREF/1023.0))/Kact)*50;
  }
  bat_v = (filter_bat/10) + 1.35;
  Serial.print("bat Total voltage = ");
  Serial.println(bat_v);
  writei2c(function_control, 0x0); //disable vaen
  return bat_v;
}
//=====================================================================================
void iout_cal(){
  float avg;
  
  writei2c(state_control, 0x42); //switch to host mode
  delay(3);
  writei2c(ov_delay, 0x00); //switch off cell balancing in order to measure the cells
  delay(3);    
  writei2c(function_control, 0x00);
  delay(5);
  writei2c(function_control, 0x06);//set IACAL, IAEN
  delay(10);
  for(int j=0; j<10; j++){
    avg+= float(analogRead(Iin)*(AREF/1023.0)); 
    delay(10);
  }
  IA_offset = avg/10;
  writei2c(function_control, 0x00); //disable IACAL, IAEN
  delay(5);
  writei2c(ov_delay, 0x80); //switch on cell balancing
  delay(3);
  writei2c(state_control, 0x40); //switch to standalone mode
  delay(3);
 return; 
}
//=====================================================================================
void vout_cal(){
  float Vdout_0V, VREF_m, Vdout_VREF_m, Kdact, Vdout_2V5, Vref_2V5, Vout_0V9, Vout_2V5;
  float vout_0v_sum =0;
  float kact_sum =0;
  int adc_val;
  float kact_sum_array[10];
  float bat_v;
  float sum_v=0;
  boolean loop_control = true;  
    
    
  writei2c(state_control, 0x42); //switch to host mode
  delay(10);
  writei2c(ov_delay, 0x00); //switch off cell balancing in order to measure the cells
  delay(3);  
  writei2c(cell_sel, 0x00);  
  writei2c(cell_balance, 0x00); 
  
  while(loop_control){
      writei2c(function_control, 0x00);
      writei2c(function_control, 0x01); //enable VAEN
      delay(10);
    
      //step1
      writei2c(cell_sel, 0x10);  
      delay(3);
      Vdout_0V=float(analogRead(Vin)*(AREF/1023.0));
      
      //step2
      writei2c(cell_sel,0x30);
      delay(3);
      VREF_m= float(analogRead(Vin)*(AREF/1023.0));
      
      //step3
      writei2c(cell_sel,0x20);
      delay(3);
      Vdout_VREF_m=float(analogRead(Vin)*(AREF/1023.0));
      Kdact=(Vdout_0V-Vdout_VREF_m)/VREF_m;
      
      //step 4
      writei2c(cell_sel,0x40);
      delay(3);
      Vdout_2V5=float(analogRead(Vin)*(AREF/1023.0));
      Vref_2V5=(Vdout_0V-Vdout_2V5)/Kdact;
      
      //step 5
      writei2c(cell_sel,0x50);
      delay(3);
      Vout_0V9=float(analogRead(Vin)*(AREF/1023.0));
      
      //step 6
      writei2c(cell_sel,0x60);
      delay(3);
      Vout_2V5=float(analogRead(Vin)*(AREF/1023.0));
      Kact =-(Vout_2V5-Vout_0V9)/(Vref_2V5-VREF_m);
      Vout_0V = Vout_2V5+Kact*Vref_2V5;
      
     /* Serial.print("Vdout = ");
      Serial.println(Vdout_0V);
      Serial.print("VREF_m = ");
      Serial.println(VREF_m);
      Serial.print("Kdact = ");
      Serial.println(Kdact);
      Serial.print("Vdout_2V5 = ");
      Serial.println(Vdout_2V5);
      
      Serial.print("Vref_2V5 = ");
      Serial.println(Vref_2V5);
      
      Serial.print("Vout_0V9 = ");
      Serial.println(Vout_0V9);
      
      Serial.print("Vout_2V5 = ");
      Serial.println(Vout_2V5);*/

    
      writei2c(cell_sel, 0x00); //clear CAL bits
      writei2c(function_control, 0x00); //clear VAEN
      writei2c(ov_delay, 0x80); //switch on cell balancing
      delay(3);
      //writei2c(state_control, 0x40); //switch to standalone mode
      delay(3);
      Serial.println("===========================================");
      Serial.print("Vout_0V = ");
      Serial.println(Vout_0V, 4);
      Serial.print("Kact = ");
      Serial.println(Kact, 4);
      
      pack_scan();
      
      bat_v = battery_voltage();
      sum_v =0;
      for(int cell=0; cell<10; cell++){
       sum_v+=cv[cell];
      }
      Serial.print("bat voltage = ");
      Serial.println(sum_v);
      if(abs(bat_v-sum_v)<=0.7){
       loop_control = false;
      } 
  }
  
 return; 
}

//====================================================================================
void status_reset(){
  byte oc_stat=oc_val|B00000001; //set bit 0
  if(!writei2c(output_control, oc_stat)){Serial.println("failed to reset status");}
  oc_stat=oc_val^B00000001; //clear bit 0
  if(!writei2c(output_control, oc_stat)){Serial.println("failed to reset status");}
  return;
}
//=====================================================================================
boolean pl900_setup(){
  if(!writei2c(output_control, oc_val)){return false;}
  if(!writei2c(state_control, sc_val)){return false;}
  if(!writei2c(function_control, fc_val)){return false;}
  if(!writei2c(cell_balance, cb_val)){return false;}
  if(!writei2c(cell_sel, cs_val)){return false;}
  if(!writei2c(uv_cfg, uv_val)){return false;}
  if(!writei2c(ov_delay, ov_val)){return false;}  
  if(!writei2c(ov_cfg, ov_cfg_val)){return false;} //set overvoltage to 4.2V
  return true;  
}
//=====================================================================================
//==================================ISR's==========================================++++
//=====================================================================================
void pwr_toggle(){
  pwr_state=!pwr_state;
}
